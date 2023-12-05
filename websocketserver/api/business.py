import json
import requests
from random import randint
from uuid import uuid4
from django.apps import apps
from django.conf import settings
from requests import Response
from websocketserver.gcloud.storage import upload_file, list_building_thumbnails, download_file
from websocketserver.ws import consumers as cs
from logging import getLogger

logger = getLogger(__file__)


def save_char_model(username: str, url: str):
    res: Response = requests.get(url)
    if not res.ok:
        return

    char_url = f"{uuid4().hex}.glb"
    upload_file(name=f"{settings.GCLOUD_CDN_CHARACTERS_PREFIX}{char_url}", contents=res.content)

    CharacterModel = apps.get_model("api.CharacterModel")
    char = CharacterModel.objects.create(
        username=username,
        url=char_url,
    )

    # load the thumbnail
    data = {
        "model": url,
        "scene": "fullbody-portrait-v1"
    }
    headers = {
        "Content-Type": "application/json"
    }
    render_res: Response = requests.post(settings.THUMBNAIL_RENDER_URL, data=json.dumps(data), headers=headers)
    if render_res.ok:
        renders_list = json.loads(render_res.text).get('renders')
        char.thumbnail = renders_list[0] if len(renders_list) > 0 else None
    char.save()


def call_building_render(uid: str, building_id: int):
    BuildingBlock = apps.get_model("api.BuildingBlock")
    blocks = BuildingBlock.objects.filter(building_id=building_id).all()
    data = []
    for block in blocks:
        data.append({
            "building_game_id": block.building_game_id,
            "elevation": float(block.elevation),
            "scale": float(block.scale),
            "rotation": float(block.rotation),
            "floor": block.floor
        })
    req_body = {
        "uid": uid,
        "env": settings.SERVER_ENV,
        "data": data
    }
    headers = {
        "Content-Type": "application/json"
    }
    render_res: Response = requests.post(settings.RENDER_SERVER_ENDPOINT, data=json.dumps(req_body), headers=headers)
    call_clear_thumbnails(10)  # 10% chance to call remove old thumbnails, to call this function every so often


def call_clear_thumbnails(r_int: int):
    """
    on chance x percent, where x is computed as x = (1 / r_int) * 100, call the remove unused thumbnails
    """
    if not randint(0, r_int):
        admin_delete_unused_building_thumbnails()


def admin_render_building(data: dict):
    ids = data.get('id', [])
    Building = apps.get_model("api.Building")
    if ids:
        buildings = Building.objects.filter(id__in=ids).prefetch_related('blocks').all()
    else:
        buildings = Building.objects.prefetch_related('blocks').all()
    i = 0
    blen = len(buildings)
    cs.admin_broadcast({"task": f"loaded {blen} buildings"})
    for building in buildings:
        i += 1
        cs.admin_broadcast({"task": f"rendering thumbnail on building id {building.id}"})
        blocks = building.blocks.all()
        if blocks:
            uid = uuid4().hex
            request_data = []
            for block in blocks:
                request_data.append({
                    "building_game_id": block.building_game_id,
                    "elevation": float(block.elevation),
                    "scale": float(block.scale),
                    "rotation": float(block.rotation),
                    "floor": block.floor
                })
            req_body = {
                "uid": uid,
                "env": settings.SERVER_ENV,
                "data": request_data
            }
            render_res = requests.post(settings.RENDER_SERVER_ENDPOINT, json=req_body)
            if render_res.ok:
                building.thumbnail_url = f"{uid}.png"
                building.save()
                cs.admin_broadcast({"task": f"rendering thumbnail on building id {building.id} successful, {i}/{blen} DONE"})
            else:
                cs.admin_broadcast({"task": f"error when rendering building id {building.id}", "error": render_res.text})
    return cs.admin_broadcast({"task": "done with all loaded buildings"}, end_task=True)


def admin_delete_unused_building_thumbnails():
    logger.info("THUMBNAIL_CHECK | Checking for unused thumbnails")
    Building = apps.get_model("api.Building")
    used_thumbnails = list(Building.objects.values_list('thumbnail_url', flat=True)
                           .exclude(thumbnail_url__isnull=True).all())
    removed = 0
    iteration = 0
    for thumbnail in list_building_thumbnails():
        iteration += 1
        if thumbnail.name.split('/')[-1] not in used_thumbnails:
            removed += 1
            logger.info(f"THUMBNAIL_CHECK | removing thumbnail {thumbnail.name}")
            cs.admin_broadcast({"task": f"removing thumbnail {thumbnail.name}"})
            thumbnail.delete()
    logger.info(f"THUMBNAIL_CHECK | done")
    cs.admin_broadcast({"task": f"done with removing unused thumbnails",
                        "building_thumbnails": len(used_thumbnails),
                        "thumbnails_in_bucket": iteration,
                        "removed_thumbnails": removed}, end_task=True)


def migrate_char_models_to_envs():
    logger.info("MIGRATING_CHAR_MODELS | checking for models to migrate")
    cs.admin_broadcast({"task": f"checking for characters to migrate"})
    CharacterModel = apps.get_model("api.CharacterModel")
    char_models = CharacterModel.objects.exclude(url__isnull=True).all()

    for char_model in char_models:
        print(f"loaded character id {char_model.id}", end='')
        char_bytes = download_file(f"characters/{char_model.url}")
        if char_bytes:
            upload_file(name=f"{settings.GCLOUD_CDN_CHARACTERS_PREFIX}{char_model.url}", contents=char_bytes)
            print(", success=True")
    logger.info("MIGRATING_CHAR_MODELS | done")
    cs.admin_broadcast({"task": f"done with migrating characters"}, end_task=True)

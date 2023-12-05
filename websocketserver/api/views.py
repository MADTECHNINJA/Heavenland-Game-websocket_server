import threading
from uuid import uuid4
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from websocketserver.auth.auth import HeavenlandUserAndPass, HeavenlandBearerOrBasic, ApiKeyAuth
from websocketserver.heavenland.client import game_login, get_inventory, remove_from_inventory, add_to_inventory, \
    list_assets
from websocketserver.ws.consumers import broadcast_message
from .redis import redis_instance
from .models import Building, BuildingBlock, CharacterModel, Parcel, GlobalGameSetting
from .business import save_char_model, call_building_render


headers = {"Access-Control-Allow-Origin": "*"}
cors_headers = {"Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
                "Access-Control-Allow-Headers": "Authorization, Content-Type",
                "Access-Control-Allow-Methods": "*"}


class ApiBaseView(APIView):
    allowed_methods = {'GET'}
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(status=status.HTTP_200_OK, headers=headers)


class ApiVersionView(APIView):
    allowed_methods = {'GET'}
    permission_classes = [AllowAny]

    def get(self, request):
        data = {"api": "v1.0.1", "env": settings.HEAVENLAND_API_ENVIRONMENT, "desc": "Websocket Server Python"}
        return Response(status=status.HTTP_200_OK, headers=headers, data=data)


class BuildingBlockView(APIView):
    allowed_methods = {'DELETE', "OPTIONS"}
    authentication_classes = [HeavenlandBearerOrBasic]

    def delete(self, request, building_id, floor):
        try:
            building_query = Building.objects.filter(username=request.user['user_id'], id=building_id).get()
        except Building.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, headers=cors_headers)
        count, _ = BuildingBlock.objects.filter(building_id=building_query, floor=floor).delete()
        if count > 0:
            return Response(status=status.HTTP_200_OK, headers=cors_headers)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND, headers=cors_headers)

    def options(self, request, *args, **kwargs):
        if self.metadata_class is None:
            return self.http_method_not_allowed(request, *args, **kwargs)
        data = self.metadata_class().determine_metadata(request, self)
        return Response(data, status=status.HTTP_200_OK, headers=cors_headers)


class BuildingBlocksView(APIView):
    allowed_methods = {'PUT', 'GET', "OPTIONS"}
    authentication_classes = [HeavenlandBearerOrBasic]

    def put(self, request, building_id):
        try:
            building = Building.objects.filter(id=building_id, username=request.user['user_id']).get()
        except Building.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, headers=cors_headers)

        for block in request.data:
            try:
                building_block, _ = BuildingBlock.objects.get_or_create(building_id=building, floor=block['floor'])
                building_block.building_game_id = block['building_game_id']
                building_block.elevation = block['elevation']
                building_block.scale = block['scale']
                building_block.rotation = block['rotation']
                building_block.save()
            except IndexError:
                return Response({"error": "missing key in the request body"},
                                status.HTTP_400_BAD_REQUEST, headers=cors_headers)
        floors = [d.get('floor') for d in request.data]
        _, _ = BuildingBlock.objects.filter(building_id=building_id).exclude(floor__in=floors).delete()
        uid = uuid4().hex
        threading.Thread(target=call_building_render, args=[uid, building.id]).start()
        building.thumbnail_url = f"{uid}.png"
        building.save()
        return Response(status=status.HTTP_201_CREATED, headers=cors_headers)

    def get(self, request, building_id):
        building_query = Building.objects.filter(username=request.user['user_id'], id=building_id).get()
        building_blocks = BuildingBlock.objects.filter(building_id=building_query).all().order_by('floor')
        resp = []
        for block in building_blocks:
            resp.append({
                "building_game_id": block.building_game_id,
                "elevation": block.elevation,
                "scale": block.scale,
                "rotation": block.rotation,
                "floor": block.floor,
            })
        return Response(resp, status.HTTP_200_OK, headers=cors_headers)

    def options(self, request, *args, **kwargs):
        if self.metadata_class is None:
            return self.http_method_not_allowed(request, *args, **kwargs)
        data = self.metadata_class().determine_metadata(request, self)
        return Response(data, status=status.HTTP_200_OK, headers=cors_headers)


class BuildingView(APIView):
    allowed_methods = {'PATCH', 'GET', 'OPTIONS', "DELETE"}
    authentication_classes = [HeavenlandBearerOrBasic]

    def patch(self, request, building_id):
        try:
            building = Building.objects.get(id=building_id, username=request.user['user_id'])
            building.name = request.data.get('name')
            building.save()
            return Response(status=status.HTTP_200_OK, headers=cors_headers)
        except Building.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, headers=cors_headers)

    def delete(self, request, building_id):
        count, _ = Building.objects.filter(id=building_id, username=request.user['user_id']).delete()
        if count > 0:
            return Response(status=status.HTTP_200_OK, headers=cors_headers)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND, headers=cors_headers)

    def get(self, request, building_id, *args, **kwargs):
        try:
            building_query = Building.objects.filter(username=request.user['user_id'], id=building_id).get()
            building_blocks = BuildingBlock.objects.filter(building_id=building_query).all().order_by('floor')
            blocks = []
            thumbnail = None
            if building_query.thumbnail_url:
                thumbnail = f"{settings.GCLOUD_CDN_BUILDING_THUMBNAIL_URL}{building_query.thumbnail_url}"
            for block in building_blocks:
                blocks.append({
                    "building_game_id": block.building_game_id,
                    "elevation": float(block.elevation),
                    "scale": float(block.scale),
                    "rotation": float(block.rotation),
                    "floor": block.floor,
                })
            resp = {
                "id": building_query.id,
                "name": building_query.name,
                "thumbnail": thumbnail,
                "blocks": blocks
            }
            return Response(resp, status.HTTP_200_OK, headers=cors_headers)
        except Building.DoesNotExist or BuildingBlock.DoesNotExist as e:
            return Response({"error": "building not found"}, status=status.HTTP_400_BAD_REQUEST, headers=cors_headers)

    def options(self, request, *args, **kwargs):
        if self.metadata_class is None:
            return self.http_method_not_allowed(request, *args, **kwargs)
        data = self.metadata_class().determine_metadata(request, self)
        return Response(data, status=status.HTTP_200_OK, headers=cors_headers)


class BuildingsView(APIView):
    allowed_methods = {'POST', 'GET', "DELETE"}
    authentication_classes = [HeavenlandBearerOrBasic]

    def post(self, request, *args, **kwargs):
        name = request.data.get("name", f"default_{uuid4().hex[:16]}")
        count = Building.objects.filter(username=request.user['user_id']).count()
        if count >= settings.BUILDING_MAX_AMOUNT:
            return Response({"error": "maximum number of buildings reached"}, status.HTTP_400_BAD_REQUEST,
                            headers=cors_headers)
        building = Building.objects.create(name=name, username=request.user['user_id'])
        building.save()
        resp = {
            "id": building.id,
            "name": building.name
        }
        return Response(resp, status.HTTP_201_CREATED, headers=cors_headers)

    def get(self, request, *args, **kwargs):
        buildings = Building.objects.filter(username=request.user['user_id']).all()
        resp = []
        for building in buildings:
            building_blocks = BuildingBlock.objects.filter(building_id=building).all().order_by('floor')
            blocks = []
            thumbnail = None
            if building.thumbnail_url:
                thumbnail = f"{settings.GCLOUD_CDN_BUILDING_THUMBNAIL_URL}{building.thumbnail_url}"
            for block in building_blocks:
                blocks.append({
                    "building_game_id": block.building_game_id,
                    "elevation": block.elevation,
                    "scale": block.scale,
                    "rotation": block.rotation,
                    "floor": block.floor,
                })
            resp.append({
                "id": building.id,
                "name": building.name,
                "thumbnail": thumbnail,
                "blocks": blocks
            })
        return Response(resp, status.HTTP_200_OK, headers=cors_headers)

    def options(self, request, *args, **kwargs):
        if self.metadata_class is None:
            return self.http_method_not_allowed(request, *args, **kwargs)
        data = self.metadata_class().determine_metadata(request, self)
        return Response(data, status=status.HTTP_200_OK, headers=cors_headers)


class CharacterEditorView(APIView):
    allowed_methods = {'POST', 'OPTIONS'}
    authentication_classes = [HeavenlandBearerOrBasic]

    def post(self, request):
        char_url = request.data.get('charUrl')
        if not char_url:
            return Response({"error": "missing charUrl in the request body"}, status.HTTP_400_BAD_REQUEST,
                            headers=cors_headers)

        user_id = request.user.get('user_id')
        count = CharacterModel.objects.filter(username=user_id).count()
        if count >= settings.CHARACTER_MAX_AMOUNT:
            return Response({"error": "maximum number of characters reached"}, status.HTTP_400_BAD_REQUEST,
                            headers=cors_headers)
        threading.Thread(target=save_char_model, args=[user_id, char_url]).start()
        return Response(status=status.HTTP_201_CREATED, headers=cors_headers)

    def options(self, request, *args, **kwargs):
        if self.metadata_class is None:
            return self.http_method_not_allowed(request, *args, **kwargs)
        data = self.metadata_class().determine_metadata(request, self)
        return Response(data, status=status.HTTP_200_OK, headers=cors_headers)


class CharacterView(APIView):
    allowed_methods = {'GET', 'DELETE', 'OPTIONS'}
    authentication_classes = [HeavenlandBearerOrBasic]

    def get(self, request, id):
        user_id = request.user.get('user_id')
        char = CharacterModel.objects.filter(id=id, username=user_id).get()
        resp = {
            "charUrl": f"{settings.GCLOUD_CDN_CHARACTERS_URL}{char.url}",
            "charId": char.id,
            "thumbnail": char.thumbnail,
        }
        if char:
            return HttpResponse(resp, status=status.HTTP_200_OK, headers=cors_headers)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND, headers=cors_headers)

    def delete(self, request, id, *args, **kwargs):
        user_id = request.user.get('user_id')
        count, _ = CharacterModel.objects.filter(id=id, username=user_id).delete()
        if count > 0:
            return Response(status=status.HTTP_200_OK, headers=cors_headers)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND, headers=cors_headers)

    def options(self, request, *args, **kwargs):
        if self.metadata_class is None:
            return self.http_method_not_allowed(request, *args, **kwargs)
        data = self.metadata_class().determine_metadata(request, self)
        return Response(data, status=status.HTTP_200_OK, headers=cors_headers)


class CharacterListView(APIView):
    allowed_methods = {'GET', 'OPTIONS'}
    authentication_classes = [HeavenlandBearerOrBasic]

    def get(self, request):
        user_id = request.user.get('user_id')
        chars = CharacterModel.objects.filter(username=user_id)
        resp = []
        for char in chars:
            resp.append({
                "charUrl": f"{settings.GCLOUD_CDN_CHARACTERS_URL}{char.url}",
                "charId": char.id,
                "thumbnail": char.thumbnail
            })
        return Response(resp, headers=cors_headers)

    def options(self, request, *args, **kwargs):
        if self.metadata_class is None:
            return self.http_method_not_allowed(request, *args, **kwargs)
        data = self.metadata_class().determine_metadata(request, self)
        return Response(data, status=status.HTTP_200_OK, headers=cors_headers)


class GameLoginView(APIView):
    allowed_methods = {'POST'}
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({"error": "missing username or password in the request body"}, status.HTTP_400_BAD_REQUEST,
                            headers=headers)
        payload = game_login(username, password)
        token = uuid4().hex
        redis_instance.hmset(name=token, mapping=payload)
        return Response({"token": token}, status.HTTP_200_OK, headers=headers)


class GameAssetsView(APIView):
    allowed_methods = {'GET'}
    permission_classes = [AllowAny]

    def get(self, request):
        limit = request.query_params.get('item_id')
        offset = request.query_params.get('item_id')
        res = list_assets(limit, offset)
        return Response(res, headers=headers)


class GameGlobalSettingsView(APIView):
    allowed_methods = {'GET', 'PATCH'}
    authentication_classes = [ApiKeyAuth]

    def get(self, request):
        ggs = GlobalGameSetting.objects.filter(id=1).get()
        res = {
            'gameFullSpeedSpinner': ggs.game_full_speed_spinner,
            'gameFullBoomer': ggs.game_full_boomer,
        }
        return Response(res, status=status.HTTP_200_OK, headers=cors_headers)

    def patch(self, request):
        data = request.data
        ggs = GlobalGameSetting.objects.filter(id=1).get()
        ggs.game_full_speed_spinner = data.get('gameFullSpeedSpinner', ggs.game_full_speed_spinner)
        ggs.game_full_boomer = data.get('gameFullBoomer', ggs.game_full_boomer)
        ggs.save()
        res = {
            'gameFullSpeedSpinner': ggs.game_full_speed_spinner,
            'gameFullBoomer': ggs.game_full_boomer,
        }
        return Response(res, status=status.HTTP_200_OK, headers=cors_headers)


class InventoryView(APIView):
    allowed_methods = {'POST', 'GET', 'DELETE'}
    authentication_classes = [HeavenlandUserAndPass]

    def get(self, request):
        inventory = get_inventory(request.user.get('access_token'), request.user.get('user_id'))
        return Response(inventory, headers=headers)

    def post(self, request):
        item_id = request.query_params.get('item_id')
        if not item_id:
            return Response({"error": "item_id has to be provided"}, status.HTTP_400_BAD_REQUEST, headers=headers)
        resp = add_to_inventory(request.user.get('access_token'), request.user.get('user_id'), item_id)
        if "statusCode" in resp.keys():
            return Response(resp, status.HTTP_404_NOT_FOUND, headers=headers)
        return Response({"success": True}, headers=headers)

    def delete(self, request):
        item_id = request.query_params.get('item_id')
        if not item_id:
            return Response({"error": "item_id has to be provided"}, status.HTTP_400_BAD_REQUEST, headers=headers)
        resp = remove_from_inventory(request.user.get('access_token'), request.user.get('user_id'), item_id)
        if "statusCode" in resp.keys():
            return Response(resp, status.HTTP_404_NOT_FOUND, headers=headers)
        return Response({"success": True}, headers=headers)


class ParcelsView(APIView):
    allowed_methods = {'PUT', 'GET', 'OPTIONS'}
    authentication_classes = [HeavenlandBearerOrBasic]

    def put(self, request, parcel_id, *args, **kwargs):
        if 'building_id' not in request.data.keys():
            return Response(status=status.HTTP_200_OK, headers=cors_headers)
        building_id = request.data.get('building_id')
        parcel = Parcel.objects.filter(id=parcel_id, username=request.user['user_id']).first()
        if not parcel:
            return Response({"error": "parcel not found or you are not an owner"},
                            status=status.HTTP_400_BAD_REQUEST, headers=cors_headers)
        if parcel.building_id and building_id:
            return Response({"error": "this parcel already have building spawned"},
                            status=status.HTTP_400_BAD_REQUEST, headers=cors_headers)
        if building_id:
            try:
                building_query = Building.objects.filter(username=request.user['user_id'], id=building_id).get()
                building_blocks = BuildingBlock.objects.filter(building_id=building_query).all()
                parcel.building_id = building_id
                parcel.save()
                blocks = []
                for block in building_blocks:
                    blocks.append({
                        "building_game_id": block.building_game_id,
                        "elevation": float(block.elevation),
                        "scale": float(block.scale),
                        "rotation": float(block.rotation),
                        "floor": block.floor,
                    })
                resp = {
                    "action": "spawn_building",
                    "parcel": {
                        "id": parcel.id,
                        "name": parcel.name,
                        "x": float(parcel.location_x),
                        "y": float(parcel.location_y)
                    },
                    "building": {
                        "id": building_query.id,
                        "name": building_query.name,
                        "blocks": blocks
                    }
                }
                broadcast_message(resp)
            except Building.DoesNotExist or BuildingBlock.DoesNotExist as e:
                return Response({"error": "building not found"}, status=status.HTTP_400_BAD_REQUEST, headers=cors_headers)
        elif parcel.building_id and not building_id:
            parcel.building_id = building_id
            parcel.save()
            resp = {
                "action": "despawn_building",
                "parcel": {
                    "id": parcel.id,
                    "name": parcel.name,
                    "x": float(parcel.location_x),
                    "y": float(parcel.location_y)
                },
                "building": None
            }
            broadcast_message(resp)
        return Response(status=status.HTTP_200_OK, headers=cors_headers)

    def get(self, request, parcel_id, *args, **kwargs):
        parcel = Parcel.objects.filter(id=parcel_id, username=request.user['user_id']).first()
        if not parcel:
            return Response({"error": "parcel not found or you are not an owner"},
                            status=status.HTTP_400_BAD_REQUEST, headers=cors_headers)
        resp = {
            "id": parcel.id,
            "name": parcel.name,
            "x": parcel.location_x,
            "y": parcel.location_y,
            "building_id": parcel.building_id,
            "thumbnail": parcel.thumbnail,
        }
        return Response(resp, status=status.HTTP_200_OK, headers=cors_headers)

    def options(self, request, *args, **kwargs):
        if self.metadata_class is None:
            return self.http_method_not_allowed(request, *args, **kwargs)
        data = self.metadata_class().determine_metadata(request, self)
        return Response(data, status=status.HTTP_200_OK, headers=cors_headers)

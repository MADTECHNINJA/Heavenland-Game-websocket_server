from google.cloud import storage
from google.cloud.storage.bucket import Bucket
from django.conf import settings

# Instantiates a client
storage_client = storage.Client()


def upload_file(name: str, contents: bytes):
    bucket: Bucket = storage_client.bucket(bucket_name=settings.GCLOUD_CDN_BUCKET_NAME)
    blob = bucket.blob(f"{name}")
    blob.upload_from_string(contents)


def download_file(name: str) -> bytes:
    bucket: Bucket = storage_client.bucket(bucket_name=settings.GCLOUD_CDN_BUCKET_NAME)
    blob = bucket.blob(f"{name}")
    contents: bytes = blob.download_as_bytes()
    return contents


def list_building_thumbnails() -> list:
    prefix = settings.GCLOUD_CDN_THUMBNAIL_PREFIX
    return list(blob for blob in storage_client.list_blobs(settings.GCLOUD_CDN_BUCKET_NAME, prefix=prefix))


def list_character_models() -> list:
    prefix = settings.GCLOUD_CDN_CHARACTERS_PREFIX
    return list(blob for blob in storage_client.list_blobs(settings.GCLOUD_CDN_BUCKET_NAME, prefix=prefix))


def delete_file(name):
    bucket: Bucket = storage_client.bucket(bucket_name=settings.GCLOUD_CDN_BUCKET_NAME)
    blob = bucket.blob(f"{name}")
    blob.delete()

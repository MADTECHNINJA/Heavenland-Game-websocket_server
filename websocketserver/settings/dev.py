"""
Django settings for websocketserver project.

Generated by 'django-admin startproject' using Django 3.2.12.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'localrandomkey'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


# Application definition

INSTALLED_APPS = [
    'rest_framework',
    'channels',
    'websocketserver.api',
    'websocketserver.ws',
    'websocketserver.gcloud',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'websocketserver.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'websocketserver.wsgi.application'
ASGI_APPLICATION = 'websocketserver.asgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': "35.193.192.30",
        'PORT': "5432",
        'NAME': "heavenland",
        'USER': "root",
        'PASSWORD': "root",
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

HEAVENLAND_AUD = "heavenland-api"
HEAVENLAND_ALGORITHM = "RS256"
VERIFYING_KEY = b"-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAh60iywNSeJRXntdHl2nfUrJGXoQnWW6SB0jUGIwWckM/A+DYb+KBwOGCvvrWhIs7dR6oewmyDWWC8NMWLzxThjX2cOQawXhx3sXDu88HxV4YQpXIAZChirGutS3IMusEEqDmdcBpwn4b/uYxRGO4XdUVSaw2Tfnz+UTS0ndmfdUmr1zQbWd2SD8KW7w3cDY6g9lEn5l/vO0sw3yo3HJuI394/m3s7chcyUge+gXxX9RLlzPzvIIbhI8Kn5wuI/AsSWecfPuJEuCfKiwp6rI8UylkFbgqt0ih+MPkXOttE2k1hYx+4jpa389W/WvlZ19h9UZaTphjU4H5GUn8yZKkiAAUHzr5SvlJ+DXJVahwlSD9MN0f/kGRLBUGIqM8f+UCBdeZPjUQmKkqJFyI1a/SgVfMeNORSbT0uZhf6tE7k/AQVTsS+FaANYwGqeyXZmkvQsazpWMGFFKI0yPnxShBNIIrNmrJCsQgqStONW6ANbAIQ9Cxtbxqjf22Uji9MyExQxdrgPQWRsXRAfrkIPGlv2l4dvbCMVXlGUf+w6frdVUnmnP5e6yWmTMT3ZVrr2vpBmzddveO7tpVatpaqLRIOzTUFS3asNo1cX4NGJSYjIo7w7iRXBAaCOquyZaQk/PPvMCBCsSXveNpuaGpv9pem+p9Ik2+/dx2XixPCDTor0MCAwEAAQ==\n-----END PUBLIC KEY-----"

ALLOW_UNAUTHENTICATED = True

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379

CHARACTER_MAX_AMOUNT = 5
THUMBNAIL_RENDER_URL = "https://render.readyplayer.me/render"
BUILDING_MAX_AMOUNT = 50

UE4_SECRET = "tHlTh4zihWYn3eawaEYQwmKcaw8ARVkLrdtaCsDayTEbCsEHChEHbWjXOtwYxbLY"
ADMIN_SECRET = "HfyjJOD6nh2KkFoja6qU7H-ByFynZpZXSsCuGpq1XrdaLhFcCGiejOhXiNc_Mrj1"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# google gcloud
config_path = Path(__file__).resolve().parent.parent.parent
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(config_path, "extreme-arch-cdn.json")
GCLOUD_CDN_BUCKET_NAME = "heavenland_backend_cdn"
GCLOUD_CDN_BUCKET_URL = "https://storage.googleapis.com/heavenland_backend_cdn/"
GCLOUD_CDN_THUMBNAIL_PREFIX = "buildings/thumbnails/dev/"
GCLOUD_CDN_BUILDING_THUMBNAIL_URL = GCLOUD_CDN_BUCKET_URL + GCLOUD_CDN_THUMBNAIL_PREFIX
GCLOUD_CDN_CHARACTERS_PREFIX = "characters/dev/"
GCLOUD_CDN_CHARACTERS_URL = GCLOUD_CDN_BUCKET_URL + GCLOUD_CDN_CHARACTERS_PREFIX

SERVER_ENV = "DEVELOPMENT"

RENDER_SERVER_ENDPOINT = "https://building-render-bt4zme4z7q-uc.a.run.app/api/building/render"

HEAVENLAND_API_URL = "https://api.heavenland.io"
HEAVENLAND_API_ENVIRONMENT = "LOCAL DEV"

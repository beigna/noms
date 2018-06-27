from settings.base import *

# Auth
AUTH_BACKEND = 'auth.'
AUTH_BACKEND_HOST = ''

# Cosas para Flask
SENTRY_DSN = 'https://@sentry.io/'  # noqa
REDIS_URL = 'redis://localhost:6379/0'

# Source & Cache paths
IMAGES_SOURCE_DIR = '/tmp'
IMAGES_CACHE_DIR = '/tmp'

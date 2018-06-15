

class Config(object):
    DEBUG = False
    TESTING = False

    SENTRY_DSN = None
    REDIS_URL = None

    SOURCE_IMAGES = None
    CACHE_IMAGES = None


class DevConfig(Config):
    DEBUG = True

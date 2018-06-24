from flask import Flask
from flask_redis import FlaskRedis
from raven.contrib.flask import Sentry

import settings


def flask_settings(settings):
    keys = filter(lambda x: x.startswith('FLASK_'), dir(settings))
    d = {}
    for key in keys:
        d[key[6:]] = getattr(settings, key)
    return d


app = Flask(__name__)
app.config.update(flask_settings(settings))
sentry = Sentry(app, dsn=app.config['SENTRY_DSN'])
redis_store = FlaskRedis(app)

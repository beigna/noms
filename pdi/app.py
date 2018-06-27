from flask import Flask
from flask_redis import FlaskRedis
from raven.contrib.flask import Sentry

from os import environ

app = Flask(__name__)
app.config.from_object(environ['PDI_SETTINGS'])

sentry = Sentry(app, dsn=app.config['SENTRY_DSN'])
redis_store = FlaskRedis(app)

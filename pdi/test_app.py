

from app import flask_settings
import settings


def test_flask_settings():
    data = flask_settings(settings)
    assert 'SENTRY_DSN' in data

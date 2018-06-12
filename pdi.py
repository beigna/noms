from flask import Flask, request, abort, send_file
from flask_redis import FlaskRedis
from raven.contrib.flask import Sentry

import os.path

from imagelib import Imagenator

import settings

app = Flask(__name__)
sentry = Sentry(app, dsn=settings.SENTRY_DSN)
redis_store = FlaskRedis(app)


from helpers import (
    get_access_token, get_accept, get_account, get_size,
    get_cache_key, cache_get, cache_set, get_cache_path
)  # noqa


@app.route('/img/<path:source>')
def default(source):
    access_token = get_access_token(request)
    if access_token is None:
        abort(401)

    account = get_account(access_token)

    if account.is_active is False:
        abort(403)

    strategy = request.args.get('s', 'fit')
    if strategy not in ('fit', 'crop'):
        abort(400)

    target_size = get_size(request)
    img_format = 'WEBP' if 'webp' in get_accept(request).lower() else 'JPEG'
    img_mime = 'image/webp' if img_format == 'WEBP' else 'image/jpeg'

    # -- Lógica
    source = os.path.join(settings.SOURCE_IMAGES, source)

    skip_cache = False
    cache_path = None

    cache_key = get_cache_key(source, strategy, target_size, img_format)
    data = cache_get(redis_store, cache_key)

    if data:
        cache_path = data.decode('utf-8')

    if cache_path is None:
        if not os.path.isfile(source):
            # se cambia el source por un default
            source = 'error.jpg'
            skip_cache = True

        cache_path = get_cache_path(settings.CACHE_IMAGES, cache_key)

        # -----------------------------------------
        image = Imagenator(source)              # -
        if strategy == 'fit':                   # -
            image.resize_fitin(target_size)     # -
        else:                                   # -
            image.resize_crop(target_size, 2)   # -
        image.save(cache_path, img_format, 90)  # -
        # -----------------------------------------

        if not skip_cache:
            cache_set(redis_store, cache_key, cache_path)

    return send_file(cache_path, mimetype=img_mime)

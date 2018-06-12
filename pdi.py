from flask import Flask, request, abort, send_file
from flask_redis import FlaskRedis
from raven.contrib.flask import Sentry

import settings

app = Flask(__name__)
sentry = Sentry(app, dsn=settings.SENTRY_DSN)
redis_store = FlaskRedis(app)


from helpers import (
    get_access_token, get_accept, get_account, get_size, resizer
)  # noqa


def graph_response(source, strategy, target_size, img_format):
    img_mime = 'image/webp' if img_format == 'WEBP' else 'image/jpeg'
    cache_path = resizer(source, strategy, target_size, img_format)
    return send_file(cache_path, mimetype=img_mime)


@app.route('/img/<path:source>')
def default(source):
    target_size = get_size(request)
    img_format = 'WEBP' if 'webp' in get_accept(request).lower() else 'JPEG'

    strategy = request.args.get('s', 'fit')
    if strategy not in ('fit', 'crop'):
        return graph_response('error.jpg', 'fit', target_size, img_format)

    access_token = get_access_token(request)
    if access_token is None:
        return graph_response('error.jpg', strategy, target_size, img_format)

    account = get_account(access_token)

    if account.is_active is False:
        return graph_response('error.jpg', strategy, target_size, img_format)
        abort(403)

    return graph_response(source, strategy, target_size, img_format)

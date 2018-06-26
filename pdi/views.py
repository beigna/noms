from app import app, sentry
from flask import request, send_file
from helpers import resizer, ResizerError
from utils import parse_request

import auth
import settings


def graph_response(img, remember=True):
    saved_at = resizer(img, remember)
    return send_file(saved_at, mimetype=img.format.mime)


@app.route('/img/<path:source>')
def default(source):
    req_img = parse_request(source, request)

    if None in (req_img.strategy, req_img.quality):
        req_img.strategy = 'crop'
        req_img.quality = 60
        req_img.path = settings.IMAGE_400

    if req_img.path is None:
        req_img.path = settings.IMAGE_404

    if not auth.acl.has_permission(request):
        req_img.path = settings.IMAGE_401

    try:
        return graph_response(req_img)

    except ResizerError:
        req_img.path = settings.IMAGE_500
        return graph_response(req_img)

    except Exception:
        sentry.captureException()
        return send_file(settings.IMAGE_500, mimetype='image/jpeg')

from app import app, sentry
from flask import request, send_file
from helpers import resizer
from utils import parse_request

import auth
import settings


def graph_response(img, remember=True):
    try:
        saved_at = resizer(img, remember)

    except Exception:
        # Estamos ante un quiñone!
        sentry.captureException()

        img.path = settings.IMAGE_500
        saved_at = resizer(img, remember)

    return send_file(saved_at, mimetype=img.format.mime)


@app.route('/img/<path:source>')
def default(source):
    req_img = parse_request(source, request)

    if not auth.acl.has_permission(request):
        # Loggear?
        req_img.path = settings.IMAGE_401
        return graph_response(req_img)

    if None in (req_img.strategy, req_img.quality):
        # Loggear?
        req_img.strategy = 'crop'
        req_img.quality = 60
        req_img.path = settings.IMAGE_400
        return graph_response(req_img)

    if req_img.path is None:
        # Loggear?
        req_img.path = settings.IMAGE_404
        return graph_response(req_img)

    return graph_response(req_img)

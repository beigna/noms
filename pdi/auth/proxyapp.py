import requests
import json

from app import redis_store as cache, sentry, app


class ProxyAppError(Exception):
    pass


def fetch_account_info(access_token):
    res = requests.post(
        '{}/api/account/info/'.format(app.config['AUTH_BACKEND_HOST']),
        data={'access_token': access_token}
    )

    if res.status_code == 200:
        data = res.json()
        return data['is_active']

    if res.status_code == 404:
        return False

    else:
        raise ProxyAppError(res.content)


def check_account(access_token):
    key = 'ses_{}'.format(access_token)

    data = cache.get(key)
    if data:
        return json.loads(data.decode('utf-8'))

    data = fetch_account_info(access_token)
    if data in (True, False):
        cache.set(key, json.dumps(data), 500)
        return data

    return False


def get_access_token(req):
    raw = req.headers.get('Authorization')
    if raw:
        chunks = raw.split()
        if len(chunks) == 2:
            return chunks[1]
    return None


def has_permission(request):
    access_token = get_access_token(request)
    if access_token is None:
        return False

    try:
        return check_account(access_token)

    except Exception:
        sentry.captureException()
        return False

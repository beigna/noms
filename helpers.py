from collections import namedtuple
from hashlib import sha1
from redis.exceptions import RedisError
from requests.exceptions import RequestException
import json
import os
import requests

from pdi import sentry, redis_store

HOST = 'https://proxyapp.desarrollo.gdn/api'
MAX_WIDTH = 3000
MAX_HEIGHT = 3000


def try_or_false(except_class, sentry):
    def decorator(f):
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)

            except except_class:
                sentry.captureException()
                return False

        return wrapper

    return decorator


def get_access_token(req):
    raw = req.headers.get('Authorization')
    if raw:
        chunks = raw.split()
        if len(chunks) == 2:
            return chunks[1]
    return None


def get_accept(req):
    return req.headers.get('Accept')


def get_size(req):
    w = int(req.args.get('w', 0))
    h = int(req.args.get('h', 0))

    w = max(MAX_WIDTH if w > MAX_WIDTH else w, 1)
    h = max(MAX_HEIGHT if h > MAX_HEIGHT else h, 1)

    return (w, h)


def get_cache_key(source, strategy, size, format_):
    return sha1(
        '{}-{}-{}-{}'.format(source, strategy, size, format_).encode('utf-8')
    ).hexdigest()


def get_cache_path(base_dir, filename):
    path = os.path.join(base_dir, filename[:2])

    try:
        os.mkdir(path)

    except FileExistsError:
        pass

    return os.path.join(path, filename)


@try_or_false(RedisError, sentry)
def cache_get(r, key):
    return r.get(key)


@try_or_false(RedisError, sentry)
def cache_set(r, key, value, ex=None):
    return r.set(key, value, ex)


@try_or_false(RequestException, sentry)
def fetch_account_info(access_token):
    res = requests.post('{}/account/info/'.format(HOST),
                        data={'access_token': access_token})

    if res.status_code == 200:
        data = res.json()
        return {'is_active': data['is_active'], 'user': data['user']}

    if res.status_code == 404:
        return {'is_active': False, 'user': None}

    return False


# - ProxyApp
Account = namedtuple('Account', ['is_active', 'user'])


def get_account(access_token):
    global redis_store

    key = 'sess_{}'.format(access_token)

    data = cache_get(redis_store, key)
    if data:
        data = json.loads(data.decode('utf-8'))

    else:
        data = fetch_account_info(access_token)
        if data is False:
            data = {'is_active': False, 'user': None}

        else:
            cache_set(redis_store, key,
                      json.dumps({'is_active': data['is_active'],
                                  'user': data['user']}),
                      500)

    return Account(data['is_active'], data['user'])

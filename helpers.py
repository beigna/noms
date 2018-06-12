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


# - imágenes!


class Imagenator1(object):

    def __init__(self, source, width, height, strategy, img_format):
        self._source = source
        self._width = width
        self._height = height
        self._strategy = strategy
        self._format = img_format

        self._hash = sha1(
            '{}-{}-{}-{}-{}'.format(source, width, height,
                                    strategy, img_format).encode('utf-8')
        ).hexdigest()
        self._key = 'img_{}'.format(self._hash)

    def run(self):
        skip_cache = False
        path = None

        data = cache_get(redis_store, self._key)
        if data:
            path, mimetype = data.decode('utf-8').split('***')

        if path is None:
            if not os.path.exists(self._source):
                self._source = 'error.jpg'
                skip_cache = True

            path, mimetype = self._generate()

            if not skip_cache:
                cache_set(redis_store, self._key,
                          '{}***{}'.format(path, mimetype))

        return path, mimetype

        path = os.path.join(path, self._hash)
        with open(path, 'wb') as fp:
            path.save(fp, self._format, quality=90)

        return path, 'image/webp' if self._format == 'WEBP' else 'image/jpeg'

    def _limit(self, value, maximum):
        return max(maximum if value > maximum else value, 1)

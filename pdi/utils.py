from collections import namedtuple
from hashlib import sha1
import os.path

import settings


class ImgRequest(object):

    __slots__ = ['_id', '_path', 'strategy', 'size', 'format', 'quality']

    def __init__(self, path, strategy, size, format, quality):
        self._path = path
        self.strategy = strategy
        self.size = size
        self.format = format
        self.quality = quality

        self._set_id()

    def _set_id(self):
        self._id = sha1(
            '{}{}{}{}{}'.format(self._path, self.strategy, self.size,
                                self.format.codec,
                                self.quality).encode('utf-8')
        ).hexdigest()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        raise AttributeError("can't set attribute")

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value
        self._set_id()


ImgFormat = namedtuple('ImgFormat', ['codec', 'mime'])
ImgSizeBase = namedtuple('ImgSize', ['width', 'height'])


class ImgSize(ImgSizeBase):
    def __str__(self):
        return '{}x{}'.format(self.width, self.height)


def get_size(req):
    w = int(req.args.get('w', settings.DEFAULT_WIDTH))
    h = int(req.args.get('h', settings.DEFAULT_HEIGHT))

    w = max(settings.MAX_WIDTH if w > settings.MAX_WIDTH else w, 1)
    h = max(settings.MAX_HEIGHT if h > settings.MAX_HEIGHT else h, 1)

    return ImgSize(w, h)


def get_format(req):
    if 'webp' in req.headers.get('Accept', '').lower():
        return ImgFormat('WEBP', 'image/webp')
    return ImgFormat('JPEG', 'image/jpeg')


def get_quality(req):
    q = int(req.args.get('q', settings.DEFAULT_QUALITY))
    if q < 0 or q > 100:
        return None
    return q

# hugo me bardeó por no usar excepciones, tiene razón


def get_strategy(req):
    s = req.args.get('s', '')
    if s not in ('fit', 'crop', 'cropb', 'crope'):
        return None
    return s


def get_source(source):
    source = os.path.join(settings.IMAGES_SOURCE_DIR, source)
    if os.path.isfile(source):
        return source
    return None


def parse_request(source, request):
    return ImgRequest(
        get_source(source),
        get_strategy(request),
        get_size(request),
        get_format(request),
        get_quality(request)
    )

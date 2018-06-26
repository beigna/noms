from imagelib import Imagenator
import os

import settings

from app import redis_store as cache


def cache_image(func_resize):
    def wrapper(*args, **kwargs):
        img, remember = args

        cache_key = 'img_{}'.format(img.id)

        path = cache.get(cache_key)

        if path:
            return path.decode('utf-8')

        else:
            path = func_resize(*args, **kwargs)
            if remember:
                cache.set(cache_key, path)

            return path

    return wrapper


@cache_image
def resizer(img, remember):
    save_to = image_save_to(settings.IMAGES_CACHE_DIR, img.id)

    image = Imagenator(img.path)
    if img.strategy == 'fit':
        image.resize_fitin(img.size)
    else:
        image.resize_crop(img.size, 2)
    image.save(save_to, img.format.codec, img.quality)

    return save_to


def image_save_to(base_dir, filename):
    path = os.path.join(base_dir, filename[:2])
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

    return os.path.join(path, filename)

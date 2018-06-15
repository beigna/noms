from PIL import Image


def aspect_ratio(width, height):
    # result > 1: Landscape
    # result < 1: Portrait
    # else: Square
    return width / height


def _left_top(delta_source, delta_target):
    a = 0
    b = delta_target

    return (a, b)


def _medium(delta_source, delta_target):
    a = round((delta_source - delta_target) / 2)
    b = round((delta_source + delta_target) / 2)

    return (a, b)


def _right_bottom(delta_source, delta_target):
    a = delta_source - delta_target
    b = delta_source
    return (a, b)


crop_align = {
    1: _left_top,
    2: _medium,
    3: _right_bottom,
}


def crop_box(source, target, align=2):

    sw, sh = source
    tw, th = target

    source_ratio = sw / sh
    target_ratio = tw / th

    if target_ratio > source_ratio:  # Se recorta el alto
        start_x = 0
        final_x = sw

        delta_y = round(sw / target_ratio)

        start_y, final_y = crop_align[align](sh, delta_y)

    elif target_ratio < source_ratio:  # Se recorta el ancho
        start_y = 0
        final_y = sh

        delta_x = round(sh * target_ratio)

        start_x, final_x = crop_align[align](sw, delta_x)

    else:  # No hace falta recortar
        return False

    return (start_x, start_y, final_x, final_y)


def fitin_size(source, target):

    sw, sh = source
    tw, th = target

    source_ratio = sw / sh
    target_ratio = tw / th

    if target_ratio > source_ratio:  # El alto manda
        width = round(th * source_ratio)
        height = th

    elif target_ratio < source_ratio:  # El ancho manda
        width = tw
        height = round(tw / source_ratio)

    else:
        width = tw
        height = th

    return (width, height)


class Imagenator(object):
    def __init__(self, source_path):
        self._source = Image.open(source_path)
        self._target = None

    def resize_crop(self, new_size, align=2):
        _box = crop_box(self._source.size, new_size, align)

        if _box:
            img = self._source.crop(_box)

        else:
            img = self._source

        self._target = img.resize(new_size, Image.LANCZOS)

    def resize_fitin(self, new_size):
        _size = fitin_size(self._source.size, new_size)
        self._target = self._source.resize(_size, Image.LANCZOS)

    def save(self, path, format_, quality):
        self._target.save(path, format_, quality=quality)

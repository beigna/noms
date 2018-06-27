import pytest
from utils import ImgSize, ImgFormat, ImgRequest


def test_img_size_to_str():
    a = ImgSize(5, 5)
    assert str(a) == '5x5'


def test_img_request_id():
    a = ImgRequest('foto.jpg', 'fit', ImgSize(5, 5),
                   ImgFormat('JPEG', 'image/jpeg'), 60)

    assert a.id == 'df92e0e614bcd13855905cdbcda13dea1131b7ee'


def test_img_request_set_id():
    a = ImgRequest('foto.jpg', 'fit', ImgSize(5, 5),
                   ImgFormat('JPEG', 'image/jpeg'), 60)

    with pytest.raises(AttributeError):
        a.id = 'fail'

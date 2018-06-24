from imagelib import crop_box, fitin_size


def test_crop_box_same_aspect_ratio():
    s = (640, 480)
    t = (320, 240)

    assert crop_box(s, t) is False


def test_crop_box_horizontal_left():
    s = (1000, 500)
    t = (500, 500)

    assert crop_box(s, t, 1) == (0, 0, *t)


def test_crop_box_horizontal_medium():
    s = (1000, 500)
    t = (500, 500)

    assert crop_box(s, t, 2) == (250, 0, 750, 500)


def test_crop_box_horizontal_right():
    s = (1000, 500)
    t = (500, 500)

    assert crop_box(s, t, 3) == (500, 0, 1000, 500)


def test_crop_box_vertical_top():
    s = (1000, 500)
    t = (1000, 200)

    assert crop_box(s, t, 1) == (0, 0, 1000, 200)


def test_crop_box_vertical_medium():
    s = (1000, 500)
    t = (1000, 200)

    assert crop_box(s, t, 2) == (0, 150, 1000, 350)


def test_crop_box_vertical_bottom():
    s = (1000, 500)
    t = (1000, 200)

    assert crop_box(s, t, 3) == (0, 300, 1000, 500)


def test_fit_in_1():
    s = (1000, 500)
    t = (400, 600)

    assert fitin_size(s, t) == (400, 200)


def test_fit_in_2():
    s = (1000, 500)
    t = (300, 50)

    assert fitin_size(s, t) == (100, 50)

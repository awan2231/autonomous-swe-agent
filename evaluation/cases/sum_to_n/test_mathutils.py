from mathutils import sum_to_n


def test_sum_small():
    assert sum_to_n(5) == 15


def test_sum_one():
    assert sum_to_n(1) == 1


def test_sum_zero():
    assert sum_to_n(0) == 0

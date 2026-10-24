from stats import max_value


def test_positive():
    assert max_value([3, 9, 2]) == 9


def test_all_negative():
    assert max_value([-5, -2, -9]) == -2


def test_single_negative():
    assert max_value([-1]) == -1

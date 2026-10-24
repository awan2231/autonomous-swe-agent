from words import word_count


def test_simple():
    assert word_count("hello world") == 2


def test_extra_spaces():
    assert word_count("hello   world") == 2


def test_empty():
    assert word_count("") == 0

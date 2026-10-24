from textutils import is_palindrome


def test_mixed_case():
    assert is_palindrome("Racecar")


def test_with_spaces():
    assert is_palindrome("A man a plan a canal Panama")


def test_not_palindrome():
    assert not is_palindrome("hello")

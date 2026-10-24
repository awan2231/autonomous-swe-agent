from pathlib import Path

CASES_DIR = Path("evaluation/cases")

CASES = {
    "sum_to_n": {
        "title": "sum_to_n(5) returns 10 instead of 15",
        "body": "sum_to_n should add all integers from 1 up to and including n, but it leaves out n.",
        "files": {
            "mathutils.py": '''def sum_to_n(n):
    total = 0
    for i in range(n):
        total += i
    return total
''',
            "test_mathutils.py": '''from mathutils import sum_to_n


def test_sum_small():
    assert sum_to_n(5) == 15


def test_sum_one():
    assert sum_to_n(1) == 1


def test_sum_zero():
    assert sum_to_n(0) == 0
''',
        },
    },
    "palindrome": {
        "title": "is_palindrome fails on mixed case and spaces",
        "body": "is_palindrome('Racecar') returns False. It should ignore letter case and spaces, so 'A man a plan a canal Panama' should also be True.",
        "files": {
            "textutils.py": '''def is_palindrome(text):
    return text == text[::-1]
''',
            "test_textutils.py": '''from textutils import is_palindrome


def test_mixed_case():
    assert is_palindrome("Racecar")


def test_with_spaces():
    assert is_palindrome("A man a plan a canal Panama")


def test_not_palindrome():
    assert not is_palindrome("hello")
''',
        },
    },
    "fizzbuzz": {
        "title": "fizzbuzz(15) returns 'Fizz' instead of 'FizzBuzz'",
        "body": "Numbers divisible by both 3 and 5 should return 'FizzBuzz', but we get 'Fizz'.",
        "files": {
            "fizz.py": '''def fizzbuzz(n):
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    if n % 15 == 0:
        return "FizzBuzz"
    return str(n)
''',
            "test_fizz.py": '''from fizz import fizzbuzz


def test_fizzbuzz_15():
    assert fizzbuzz(15) == "FizzBuzz"


def test_fizz():
    assert fizzbuzz(3) == "Fizz"


def test_buzz():
    assert fizzbuzz(5) == "Buzz"


def test_number():
    assert fizzbuzz(7) == "7"
''',
        },
    },
    "max_value": {
        "title": "max_value returns 0 for lists of negative numbers",
        "body": "max_value([-5, -2, -9]) returns 0 but should return -2. It should work for any list of numbers.",
        "files": {
            "stats.py": '''def max_value(numbers):
    best = 0
    for n in numbers:
        if n > best:
            best = n
    return best
''',
            "test_stats.py": '''from stats import max_value


def test_positive():
    assert max_value([3, 9, 2]) == 9


def test_all_negative():
    assert max_value([-5, -2, -9]) == -2


def test_single_negative():
    assert max_value([-1]) == -1
''',
        },
    },
    "word_count": {
        "title": "word_count miscounts extra spaces and empty text",
        "body": "word_count('hello   world') returns 4 instead of 2, and word_count('') returns 1 instead of 0. Extra whitespace should be ignored.",
        "files": {
            "words.py": '''def word_count(text):
    return len(text.split(" "))
''',
            "test_words.py": '''from words import word_count


def test_simple():
    assert word_count("hello world") == 2


def test_extra_spaces():
    assert word_count("hello   world") == 2


def test_empty():
    assert word_count("") == 0
''',
        },
    },
}


def main():
    for name, case in CASES.items():
        case_dir = CASES_DIR / name
        case_dir.mkdir(parents=True, exist_ok=True)
        for filename, content in case["files"].items():
            (case_dir / filename).write_text(content, encoding="utf-8")
        (case_dir / "issue.md").write_text(
            f"# {case['title']}\n\n{case['body']}\n", encoding="utf-8"
        )
    print(f"Created {len(CASES)} cases in {CASES_DIR}")


if __name__ == "__main__":
    main()
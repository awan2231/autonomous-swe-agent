from fizz import fizzbuzz


def test_fizzbuzz_15():
    assert fizzbuzz(15) == "FizzBuzz"


def test_fizz():
    assert fizzbuzz(3) == "Fizz"


def test_buzz():
    assert fizzbuzz(5) == "Buzz"


def test_number():
    assert fizzbuzz(7) == "7"

def max_value(numbers):
    best = 0
    for n in numbers:
        if n > best:
            best = n
    return best

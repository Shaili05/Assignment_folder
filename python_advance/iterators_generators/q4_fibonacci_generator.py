# Q4 - Generator to produce Fibonacci numbers

from typing import Iterator

def fibonacci_sequence(count: int) -> Iterator[int]:
    """
    Generates Fibonacci numbers one by one.
    first and second are the two previous values we track.
    """
    first: int = 0
    second: int = 1
    for _ in range(count):
        yield first
        first, second = second, first + second

for num in fibonacci_sequence(10):
    print(num, end=" ")
print()
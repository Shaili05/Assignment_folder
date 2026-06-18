# Q3 - Generator function that yields square numbers up to N

from typing import Iterator

def square_numbers(limit: int) -> Iterator[int]:
    """
    Yields squares one at a time instead of storing all in a list.
    More memory-friendly for large N.
    """
    for i in range(1, limit + 1):
        yield i * i

for sq in square_numbers(6):
    print(sq)
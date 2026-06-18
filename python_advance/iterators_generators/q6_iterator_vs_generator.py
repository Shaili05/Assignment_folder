# Q6 - Difference between iterator and generator with examples

from typing import Iterator

# ---- Iterator approach ----
# Need to build a whole class with __iter__ and __next__

class SimpleIterator:
    """Iterator that gives 1, 2, 3"""

    UPPER_LIMIT: int = 3

    def __init__(self) -> None:
        self.num: int = 1

    def __iter__(self) -> "SimpleIterator":
        return self

    def __next__(self) -> int:
        if self.num > self.UPPER_LIMIT:
            raise StopIteration
        value: int = self.num
        self.num += 1
        return value

print("Iterator output:")
for val in SimpleIterator():
    print(val)

# ---- Generator approach ----
# Much shorter, just use yield keyword inside a function

def simple_generator() -> Iterator[int]:
    """Generator that gives 1, 2, 3 - way less code"""
    yield 1
    yield 2
    yield 3

print("Generator output:")
for val in simple_generator():
    print(val)

# Main difference: generators save memory because they produce
# one value at a time, iterators need all data ready
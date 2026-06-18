# Q2 - Custom iterator class that returns numbers from 1 to N

class NumberRange:
    """
    A custom iterator that goes from 1 up to a given number N.
    Uses __iter__ and __next__ to work like a proper iterator.
    """

    def __init__(self, limit: int) -> None:
        self.limit: int = limit
        self.current: int = 1

    def __iter__(self) -> "NumberRange":
        # returning self because this object itself is the iterator
        return self

    def __next__(self) -> int:
        if self.current > self.limit:
            raise StopIteration
        value: int = self.current
        self.current += 1
        return value

counter = NumberRange(5)
for num in counter:
    print(num)
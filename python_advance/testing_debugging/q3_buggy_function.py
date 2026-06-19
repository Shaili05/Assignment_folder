# Q3 - Function with a logical bug, use pdb to find it
# To debug: python -m pdb q3_buggy_function.py
# Then press: n (next line), p variable_name (print value), c (continue)

import pdb

WRONG_DIVISOR: int = 10

def calculate_average(numbers: list[int]) -> float:
    """
    Calculates average of a list.
    There is a bug here - can you find it using pdb?
    """
    total: int = 0
    for num in numbers:
        total += num

    pdb.set_trace()  # debugger pauses here so we can inspect total and numbers

    # bug: dividing by a fixed number instead of len(numbers)
    average: float = total / WRONG_DIVISOR
    return average

result: float = calculate_average([10, 20, 30])
print("Average:", result)
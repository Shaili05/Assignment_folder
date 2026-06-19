# Q4 - Using pdb breakpoints inside a loop to inspect variables
# Run: python q4_pdb_loop.py
# Commands: n = next, p i = print i, p total = print total, c = continue

import pdb

def running_total(numbers: list[int]) -> int:
    """Calculates running total, we pause inside loop to inspect"""
    total: int = 0
    for i in numbers:
        pdb.set_trace()  # pauses every iteration so we can check values
        total += i
    return total

print(running_total([5, 10, 15]))
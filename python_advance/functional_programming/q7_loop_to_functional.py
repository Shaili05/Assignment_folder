# Q7 - Convert a loop-based program to functional style

# ---- Loop version ----
numbers: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

loop_result: list[int] = []
for num in numbers:
    if num % 2 == 0:
        loop_result.append(num * num)

print("Loop style result:", loop_result)

# ---- Functional version (same logic, no loop) ----
# first filter evens, then map to squares
functional_result: list[int] = list(map(lambda n: n * n, filter(lambda n: n % 2 == 0, numbers)))

print("Functional style result:", functional_result)
# Q6 - Recursive Fibonacci

def fibonacci(num: int) -> int:
    """
    Returns nth Fibonacci number using recursion.
    Each number is sum of previous two numbers.
    Base cases: fib(0)=0, fib(1)=1
    """
    if num <= 0:
        return 0
    if num == 1:
        return 1
    return fibonacci(num - 1) + fibonacci(num - 2)

TOTAL_TERMS: int = 10

for i in range(TOTAL_TERMS):
    print(fibonacci(i), end=" ")
print()
# Q5 - Recursive function to calculate factorial

def factorial(num: int) -> int:
    """
    Calculates factorial by calling itself with a smaller number.
    Base case is 0! = 1, otherwise multiply and go smaller.
    """
    if num == 0:
        return 1
    return num * factorial(num - 1)

print("Factorial of 5:", factorial(5))
print("Factorial of 0:", factorial(0))
# Q2 - Divide two numbers, handle ZeroDivisionError

def divide_numbers() -> None:
    """
    Takes two numbers from user and divides them.
    Handles the case where second number is zero.
    """
    try:
        num1: int = int(input("Enter first number: "))
        num2: int = int(input("Enter second number: "))
        result: float = num1 / num2
        print("Result:", result)
    except ZeroDivisionError:
        # division by zero is mathematically not possible
        print("Cannot divide by zero")

divide_numbers()
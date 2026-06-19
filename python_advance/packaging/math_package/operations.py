# Q3 & Q4 - Math operations package with add, subtract, multiply, divide

def add(first_number: float, second_number: float) -> float:
    """Adds two numbers"""
    return first_number + second_number

def subtract(first_number: float, second_number: float) -> float:
    """Subtracts second number from first number"""
    return first_number - second_number

def multiply(first_number: float, second_number: float) -> float:
    """Multiplies two numbers"""
    return first_number * second_number

def divide(first_number: float, second_number: float) -> float | str:
    """Divides first number by second, returns error message for zero division"""
    if second_number == 0:
        return "Cannot divide by zero"
    return first_number / second_number
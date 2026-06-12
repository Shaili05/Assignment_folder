"""
my_module.py
Custom module created for Q24.
This module is imported inside functions_modules.py to demonstrate
how to create and use your own Python module.
"""


def add_two_numbers(first_number: float, second_number: float) -> float:
    """
    Custom utility function - adds two numbers.
    Created as part of Q24 to demonstrate a reusable module function.
    Returns the sum of the two numbers passed to it.
    """
    return first_number + second_number


def is_even(number: int) -> bool:
    """
    Custom utility function - checks if a number is even.
    Created as part of Q24 to demonstrate a reusable module function.
    Returns True if number is even, False if odd.
    """
    return number % 2 == 0


def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Custom utility function - converts Celsius to Fahrenheit.
    Created as part of Q24 to demonstrate a reusable module function.
    Uses the standard formula: (C x 9/5) + 32.
    """
    return (celsius * 9 / 5) + 32
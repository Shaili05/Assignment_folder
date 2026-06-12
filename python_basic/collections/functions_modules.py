"""
functions_modules.py
Section 3 - Functions and Modules
Questions: Q17 to Q24
"""

import math
import random

from my_module import (
    add_two_numbers,
    is_even,
    celsius_to_fahrenheit
)

# Q17
def calculate_square(number: float) -> float:
    """
    Q17 - Write a function to calculate square of a number.
    Takes a number as input and returns its square using the ** operator.
    """
    return number ** 2

print("\n Q17: Square of a Number ")
print("Square of 6:", calculate_square(6))


# Q18
def is_palindrome(value: str) -> bool:
    """
    Q18 - Write a function to check palindrome (number and string).
    Converts input to string, removes spaces, makes lowercase,
    then checks if it reads the same forwards and backwards.
    Works for both numbers like 12321 and strings like 'madam'.
    """
    text = str(value).lower().replace(" ", "")
    return text == text[::-1]

print("\n Q18: Palindrome Check ")
print("Is 'madam' palindrome?", is_palindrome("madam"))
print("Is 12321 palindrome?", is_palindrome(12321))
print("Is 'hello' palindrome?", is_palindrome("hello"))


# Q19
def get_maximum(numbers: list) -> float:
    """
    Q19 - Write a function that returns maximum number from a list.
    Loops through every number in the list and keeps track of the
    largest one found so far. Does not use the built-in max() function.
    """
    largest = numbers[0]
    for num in numbers:
        if num > largest:
            largest = num
    return largest

print("\n Q19: Maximum from List ")
sample_list = [3, 7, 1, 9, 4, 6]
print("Maximum:", get_maximum(sample_list))


# Q20
def greet_user(name: str = "Guest", message: str = "Hello") -> str:
    """
    Q20 - Write a function using default parameters.
    Has default values for both name and message so it works
    even when called with no arguments, one argument, or both.
    """
    return f"{message}, {name}!"

print("\n Q20: Default Parameters ")
print(greet_user())
print(greet_user("Shaili"))
print(greet_user("Shaili", "Good morning"))


# Q22
def use_math_module() -> None:
    """
    Q22 - Use math module to find square root, power, and factorial.
    Demonstrates three different functions from Python's built-in math module.
    """
    num = 5
    print("Square root of 5:", math.sqrt(num))
    print("2 to the power 8:", math.pow(2, 8))
    print("Factorial of 5:", math.factorial(num))

print("\n Q22: Math Module ")
use_math_module()


# Q23
def use_random_module() -> None:
    """
    Q23 - Generate random numbers using random module.
    Demonstrates randint for whole numbers, uniform for decimals,
    and choice for picking randomly from a list.
    """
    print("Random number (1-100):", random.randint(1, 100))
    print("Random float:", round(random.uniform(1.0, 10.0), 2))
    print("Random pick:", random.choice(["Python", "Java", "C++"]))

print("\n Q23: Random Module ")
use_random_module()


# Q24
def use_custom_module() -> None:
    """
    Q24 - Create your own module and import it.
    Imports three functions from our own custom file my_module.py
    and calls them here to show how module importing works.
    """
    print("Sum from my_module:", add_two_numbers(10, 5))
    print("Is 8 even?", is_even(8))
    print("25 Celsius in Fahrenheit:", celsius_to_fahrenheit(25))

print("\n Q24: Custom Module ")
use_custom_module()
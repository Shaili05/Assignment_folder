"""
introduction.py
Section 1 - Introduction to Python
Questions: Q1, Q2, Q3
"""

import sys


# Q1
def print_welcome_message() -> None:
    """
    Q1 - Write a program to print 'Welcome to Python Training'.
    Simply prints the welcome message to the console.
    """
    print("\n--- Q1: Print Welcome Message ---")
    print("Welcome to Python Training")


print_welcome_message()


# Q2
def show_python_version() -> None:
    """
    Q2 - Write a program to check your Python version.
    Uses the sys module to fetch and display the current Python version.
    """
    print("\n--- Q2: Check Python Version ---")
    print("Python version:", sys.version)


show_python_version()


# Q3
def greet_user() -> None:
    """
    Q3 - Take user input (name and age) and print a formatted message.
    Takes name and age as input from the user and prints a greeting.
    """
    print("\n--- Q3: User Input and Greeting ---")
    name = input("Enter your name: ")
    age = input("Enter your age: ")
    print(f"Hello {name}! You are {age} years old.")


greet_user()
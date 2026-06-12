"""
basics.py
Section 2 - Python Basics
Covers: Variables, Data Types, Operators, Conditionals, Loops
Questions: Q4 to Q16
"""

# Constants
GRADE_A_MINIMUM = 80
GRADE_B_MINIMUM = 60
GRADE_C_MINIMUM = 40
TABLE_LIMIT = 11
RANGE_END = 101


# Q4
def show_variable_types() -> None:
    """
    Q4 - Create variables of type int, float, string, and boolean.
    Print their types using type().
    Creates one variable of each type and prints what type each one is.
    """
    whole_number: int = 25
    decimal_number: float = 3.14
    text_value: str = "Shaili"
    is_student: bool = True

    
    print(type(whole_number))
    print(type(decimal_number))
    print(type(text_value))
    print(type(is_student))

print("\n Q4: Variable Types ")
show_variable_types()


# Q5
def swap_two_numbers() -> None:
    """
    Q5 - Write a program to swap two numbers.
    Takes two numbers from user, swaps their values and prints before and after.
    """
    print("\n Q5: Swap Two Numbers ")
    first = int(input("Enter first number: "))
    second = int(input("Enter second number: "))

    print(f"Before swap -> first: {first}, second: {second}")
    first, second = second, first
    print(f"After swap  -> first: {first}, second: {second}")


swap_two_numbers()


# Q6
def basic_arithmetic() -> None:
    """
    Q6 - Take two numbers and print sum, difference, multiplication, and division.
    Takes two numbers as input and performs all four basic arithmetic operations.
    Handles division by zero case as well.
    """
    print("\n Q6: Basic Arithmetic ")
    num_one = float(input("Enter first number: "))
    num_two = float(input("Enter second number: "))

    print("Sum:", num_one + num_two)
    print("Difference:", num_one - num_two)
    print("Multiplication:", num_one * num_two)

    if num_two != 0:
        print("Division:", num_one / num_two)
    else:
        print("Division: Cannot divide by zero")


basic_arithmetic()


# Q7
def check_even_or_odd() -> None:
    """
    Q7 - Write a program to check whether a number is even or odd.
    Takes a number from user and checks if it is divisible by 2.
    """
    print("\n Q7: Even or Odd ")
    number = int(input("Enter a number: "))
    if number % 2 == 0:
        print(number, "is Even")
    else:
        print(number, "is Odd")


check_even_or_odd()


# Q8
def check_sign() -> None:
    """
    Q8 - Check whether a number is positive, negative, or zero.
    Takes a number and checks its sign using if elif else conditions.
    """
    print("\n Q8: Positive Negative Zero ")
    number = float(input("Enter a number: "))
    if number > 0:
        print("Positive")
    elif number < 0:
        print("Negative")
    else:
        print("Zero")


check_sign()


# Q9
def find_largest() -> None:
    """
    Q9 - Find the largest of three numbers.
    Takes three numbers from user and finds which one is the largest
    by comparing them using if elif else.
    """
    print("\n Q9: Largest of Three Numbers ")
    first = float(input("Enter first number: "))
    second = float(input("Enter second number: "))
    third = float(input("Enter third number: "))

    if first >= second and first >= third:
        print("Largest:", first)
    elif second >= first and second >= third:
        print("Largest:", second)
    else:
        print("Largest:", third)


find_largest()


# Q10
def calculate_grade() -> None:
    """
    Q10 - Calculate grade based on marks (A/B/C/Fail).
    Takes marks out of 100 and assigns grade using defined constants
    for each grade boundary to avoid hardcoded values.
    """
    print("\n Q10: Grade Calculator ")
    marks = float(input("Enter marks out of 100: "))

    if marks >= GRADE_A_MINIMUM:
        print("Grade: A")
    elif marks >= GRADE_B_MINIMUM:
        print("Grade: B")
    elif marks >= GRADE_C_MINIMUM:
        print("Grade: C")
    else:
        print("Grade: Fail")


calculate_grade()


# Q11
def check_leap_year() -> None:
    """
    Q11 - Check whether a year is a leap year.
    A year is leap if divisible by 4 but not 100, or divisible by 400.
    Takes year as input and checks both conditions.
    """
    print("\n Q11: Leap Year Check ")
    year = int(input("Enter a year: "))
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        print(year, "is a Leap Year")
    else:
        print(year, "is not a Leap Year")


check_leap_year()


# Q12
def print_one_to_hundred() -> None:
    """
    Q12 - Print numbers from 1 to 100 using a loop.
    Uses a for loop with range to print all numbers from 1 to 100
    on a single line separated by spaces.
    """
    print("\n Q12: Print 1 to 100 ")
    for num in range(1, RANGE_END):
        print(num, end=" ")
    print()


print_one_to_hundred()


# Q13
def print_multiplication_table() -> None:
    """
    Q13 - Print multiplication table of a number.
    Takes a number from user and prints its full multiplication
    table from 1 to 10 using a for loop.
    """
    print("\n Q13: Multiplication Table ")
    num = int(input("Enter a number: "))
    for i in range(1, TABLE_LIMIT):
        print(f"{num} x {i} = {num * i}")


print_multiplication_table()


# Q14
def find_factorial() -> None:
    """
    Q14 - Find factorial of a number.
    Takes a number from user and calculates its factorial
    by multiplying all numbers from 1 to that number using a loop.
    """
    print("\n Q14: Factorial ")
    num = int(input("Enter a number: "))
    result = 1
    for i in range(1, num + 1):
        result *= i
    print(f"Factorial of {num} =", result)


find_factorial()


# Q15
def reverse_number() -> None:
    """
    Q15 - Reverse a number using a loop.
    Takes a number and extracts its digits one by one from the right
    using modulo and builds the reversed number step by step.
    """
    print("\n Q15: Reverse a Number ")
    num = int(input("Enter a number: "))
    reversed_num = 0
    temp = num

    while temp != 0:
        last_digit = temp % 10
        reversed_num = reversed_num * 10 + last_digit
        temp //= 10

    print("Reversed:", reversed_num)


reverse_number()


# Q16
def check_prime() -> None:
    """
    Q16 - Check whether a number is prime.
    A prime number has no factors other than 1 and itself.
    Checks divisibility only up to square root of the number
    for better efficiency - O(sqrt n) instead of O(n).
    """
    print("\n Q16: Prime Number Check ")
    num = int(input("Enter a number: "))

    if num < 2:
        print(num, "is not prime")
        return

    is_prime = True
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            is_prime = False
            break

    if is_prime:
        print(num, "is a Prime number")
    else:
        print(num, "is not a Prime number")


check_prime()
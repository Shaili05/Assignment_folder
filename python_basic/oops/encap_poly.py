"""
encap_poly.py
Section 6 - Object Oriented Programming
Questions: Q43, Q44
"""

import math


# Q43
class BankAccount:
    """
    Q43 - Implement encapsulation using private variables in Bank class.
    The balance is stored as a private variable using double underscore (__balance)
    so it cannot be accessed or changed directly from outside the class.
    Deposit and withdraw methods are the only way to interact with the balance.
    """

    def __init__(self, holder_name: str, opening_balance: float) -> None:
        """Sets up bank account with holder name and an opening balance."""
        self.holder_name = holder_name
        self.__balance = opening_balance

    def deposit(self, amount: float) -> None:
        """
        Adds amount to balance if the amount is a positive number.
        Prints updated balance after successful deposit.
        """
        if amount > 0:
            self.__balance += amount
            print(f"Deposited {amount}. New balance: {self.__balance}")
        else:
            print("Deposit amount must be positive.")

    def withdraw(self, amount: float) -> None:
        """
        Withdraws amount from balance if funds are sufficient.
        Rejects negative amounts and amounts greater than current balance.
        """
        if amount > self.__balance:
            print("Insufficient funds.")
        elif amount <= 0:
            print("Withdrawal amount must be positive.")
        else:
            self.__balance -= amount
            print(f"Withdrawn {amount}. Remaining balance: {self.__balance}")

    def get_balance(self) -> float:
        """Returns the current account balance."""
        return self.__balance

print("\n Q43: Encapsulation - Bank Account ")
account = BankAccount("Shaili", 5000)
account.deposit(1000)
account.withdraw(2000)
print("Final balance:", account.get_balance())


# Q44
class Circle:
    """
    Q44 - Demonstrate polymorphism using different classes with same method name.
    Circle is one of three shape classes. All three have calculate_area()
    and describe() methods with the same name but different logic inside.
    This is polymorphism - same method name, different behaviour per class.
    """

    def __init__(self, radius: float) -> None:
        """Sets up circle with a radius value."""
        self.radius = radius

    def calculate_area(self) -> float:
        """Returns area of the circle using pi * r squared."""
        return round(math.pi * self.radius ** 2, 2)

    def describe(self) -> str:
        """Returns a description of this shape."""
        return f"Circle with radius {self.radius}"


class Rectangle:
    """
    Q44 continued - Rectangle class for polymorphism demonstration.
    Has the same method names as Circle and Triangle but calculates
    area differently using length multiplied by width.
    """

    def __init__(self, length: float, width: float) -> None:
        """Sets up rectangle with length and width values."""
        self.length = length
        self.width = width

    def calculate_area(self) -> float:
        """Returns area of the rectangle using length x width."""
        return self.length * self.width

    def describe(self) -> str:
        """Returns a description of this shape."""
        return f"Rectangle {self.length} x {self.width}"


class Triangle:
    """
    Q44 continued - Triangle class for polymorphism demonstration.
    Has the same method names as Circle and Rectangle but calculates
    area using half base multiplied by height.
    """

    def __init__(self, base: float, height: float) -> None:
        """Sets up triangle with base and height values."""
        self.base = base
        self.height = height

    def calculate_area(self) -> float:
        """Returns area of the triangle using 0.5 x base x height."""
        return 0.5 * self.base * self.height

    def describe(self) -> str:
        """Returns a description of this shape."""
        return f"Triangle base {self.base} height {self.height}"

print("\n Q44: Polymorphism - Shapes ")
shapes = [Circle(7), Rectangle(4, 6), Triangle(5, 8)]
for shape in shapes:
    print(shape.describe(), "-> Area:", shape.calculate_area())
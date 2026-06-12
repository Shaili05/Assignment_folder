"""
inheritance.py
Section 6 - Object Oriented Programming
Question: Q42
"""


# Q42
class Person:
    """
    Q42 - Implement inheritance using Person and Employee class.
    Person is the base class with name and age as basic attributes.
    The introduce method returns a simple introduction string.
    """

    def __init__(self, name: str, age: int) -> None:
        """Sets up the person object with name and age."""
        self.name = name
        self.age = age

    def introduce(self) -> str:
        """Returns a basic introduction of the person."""
        return f"Hi, I am {self.name} and I am {self.age} years old."


class Employee(Person):
    """
    Q42 continued - Employee inherits from Person.
    Adds employee specific attributes like employee_id and department.
    Overrides the introduce method to include work details as well.
    Uses super() to reuse the Person constructor instead of rewriting it.
    """

    def __init__(self, name: str, age: int, employee_id: str, department: str) -> None:
        """Sets up employee using Person's constructor plus adds employee details."""
        super().__init__(name, age)
        self.employee_id = employee_id
        self.department = department

    def introduce(self) -> str:
        """Returns introduction with both personal and work details."""
        base = super().introduce()
        return f"{base} I work in {self.department} (ID: {self.employee_id})."

print("\n Q42: Inheritance - Person and Employee ")
person_one = Person("Rohit", 45)
print(person_one.introduce())

employee_one = Employee("Shaili", 30, "EMP001", "Finance")
print(employee_one.introduce())
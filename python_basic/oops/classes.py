"""
classes.py
Section 6 - Object Oriented Programming
Questions: Q40, Q41
"""


# Q40
class Student:
    """
    Q40 - Create a Student class with attributes and display details.
    Represents a student with name, age and branch as attributes.
    The display_details method prints all the student information.
    """

    def __init__(self, name: str, age: int, branch: str) -> None:
        """Sets up the student object with name, age and branch."""
        self.name = name
        self.age = age
        self.branch = branch

    def display_details(self) -> None:
        """Prints all details of the student."""
        print("Name:", self.name)
        print("Age:", self.age)
        print("Branch:", self.branch)

print("\n Q40: Student Class ")
student_one = Student("Shaili", 21, "Computer Science")
student_one.display_details()


# Q41
class Car:
    """
    Q41 - Create a Car class with a constructor.
    Represents a car with brand, model and year as attributes.
    The constructor takes all three values and the show_info method displays them.
    """

    def __init__(self, brand: str, model: str, year: int) -> None:
        """Sets up the car object with brand, model and manufacturing year."""
        self.brand = brand
        self.model = model
        self.year = year

    def show_info(self) -> None:
        """Prints the car details in a readable format."""
        print(f"{self.year} {self.brand} {self.model}")

print("\n Q41: Car Class ")
my_car = Car("Toyota", "Innova", 2022)
my_car.show_info()
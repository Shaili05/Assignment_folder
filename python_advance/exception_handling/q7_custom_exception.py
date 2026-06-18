# Q7 - Create a custom exception called AgeException
# Raise it when age is less than 18

MINIMUM_AGE: int = 18

class AgeException(Exception):
    """
    Custom exception for age-related validation.
    Inherits from base Exception class.
    """
    pass

def verify_age(age: int) -> None:
    """
    Checks if age meets the minimum requirement.
    Raises AgeException if age is below 18.
    """
    if age < MINIMUM_AGE:
        raise AgeException("Age must be 18 or above, you entered: " + str(age))
    print("Age is valid:", age)

try:
    verify_age(15)
except AgeException as err:
    print("AgeException caught:", err)
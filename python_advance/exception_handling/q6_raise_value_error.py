# Q6 - Manually raise a ValueError if number is negative

def check_positive(number: int) -> int:
    """
    Checks if number is positive.
    If negative, raises a ValueError manually with a message.
    """
    if number < 0:
        raise ValueError("Number cannot be negative, got: " + str(number))
    return number

try:
    check_positive(-5)
except ValueError as err:
    print("Caught error:", err)
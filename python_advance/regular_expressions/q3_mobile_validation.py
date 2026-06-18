# Q3 - Validate a 10-digit mobile number

import re

MOBILE_PATTERN: str = r"^\d{10}$"

def is_valid_mobile(number: str) -> bool:
    """
    Checks mobile number is exactly 10 digits.
    ^ means start, \d{10} means exactly 10 digits, $ means end.
    """
    return bool(re.match(MOBILE_PATTERN, number))

numbers: list[str] = ["9876543210", "12345", "98765432101", "abcdefghij"]

for num in numbers:
    status: str = "Valid" if is_valid_mobile(num) else "Invalid"
    print(num, "->", status)
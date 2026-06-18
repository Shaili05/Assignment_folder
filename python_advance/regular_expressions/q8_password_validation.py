# Q8 - Password validation using regex
# Rules: minimum 16 chars, at least one digit, one special character

import re

MINIMUM_PASSWORD_LENGTH: int = 16
SPECIAL_CHARACTER_PATTERN: str = r"[!@#$%^&*]"
DIGIT_PATTERN: str = r"\d"

def is_valid_password(password: str) -> tuple[bool, str]:
    """
    Validates password against three rules:
    1. Minimum 16 characters long
    2. At least one digit (0-9)
    3. At least one special character from !@#$%^&*
    """
    if len(password) < MINIMUM_PASSWORD_LENGTH:
        return False, "Too short, need at least 16 characters"

    if not re.search(DIGIT_PATTERN, password):
        return False, "Need at least one number"

    if not re.search(SPECIAL_CHARACTER_PATTERN, password):
        return False, "Need at least one special character like !@#"

    return True, "Password is valid"

passwords: list[str] = ["abc", "password1", "Pass@123", "hello!world", "MySecurePass@2026"]

for pwd in passwords:
    valid, message = is_valid_password(pwd)
    print(pwd, "->", message)
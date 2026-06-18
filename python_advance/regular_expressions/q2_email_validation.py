# Q2 - Validate an email address using regex

import re

EMAIL_PATTERN: str = r"^[\w\.-]+@[\w\.-]+\.\w+$"

def is_valid_email(email: str) -> bool:
    """
    Checks if email has the format: something@something.something
    Pattern breaks down:
    [\w\.-]+ = letters, digits, dots or hyphens before @
    @ = literal @ symbol
    [\w\.-]+ = domain name
    \. = literal dot
    \w+ = domain extension like com, org
    """
    return bool(re.match(EMAIL_PATTERN, email))

emails: list[str] = ["test@gmail.com", "bad-email", "hello@.com", "user@domain.org"]

for email in emails:
    status: str = "Valid" if is_valid_email(email) else "Invalid"
    print(email, "->", status)
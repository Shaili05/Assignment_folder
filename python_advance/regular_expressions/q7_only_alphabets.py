# Q7 - Check if a string contains only alphabets

import re

ALPHABET_PATTERN: str = r"^[a-zA-Z]+$"

def is_only_alphabets(text: str) -> bool:
    """
    Returns True if string has only letters (a-z, A-Z).
    ^[a-zA-Z]+$ means start, only letters, end.
    """
    return bool(re.match(ALPHABET_PATTERN, text))

words: list[str] = ["HelloWorld", "Hello123", "Python", "test!"]

for word in words:
    status: str = "Only alphabets" if is_only_alphabets(word) else "Has non-alphabets"
    print(word, "->", status)
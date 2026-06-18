# Q1 - Extract all numbers from a string

import re

text: str = "My order number is 4521 and I paid 250 rupees for 3 items"

# \d+ means one or more digits
all_numbers: list[str] = re.findall(r"\d+", text)

print("Numbers found:", all_numbers)
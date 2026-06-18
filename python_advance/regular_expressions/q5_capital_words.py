# Q5 - Use re.findall() to extract words starting with capital letter

import re

CAPITAL_WORD_PATTERN: str = r"[A-Z][a-z]*"

text: str = "Last week Rashmi and Arpit went to Mumbai for a college fest"

# one capital letter followed by lowercase letters
capital_words: list[str] = re.findall(CAPITAL_WORD_PATTERN, text)

print("Words starting with capital letter:", capital_words)
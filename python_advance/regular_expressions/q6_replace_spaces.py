# Q6 - Replace multiple spaces with a single space using re.sub()

import re

text: str = "hey  can you  please   check this file when you get a chance"

# \s+ matches one or more whitespace characters
# replacing all of them with a single space
cleaned_text: str = re.sub(r"\s+", " ", text)

print("Before:", text)
print("After:", cleaned_text)
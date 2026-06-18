# Q4 - Use re.search() to check if a word exists in a sentence

import re

sentence: str = "I was stuck on this assignment for two days but finally got it working"
word_to_find: str = "assignment"

result = re.search(word_to_find, sentence)

if result:
    print("Word found at position:", result.start())
else:
    print("Word not found")
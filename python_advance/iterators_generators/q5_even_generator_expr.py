# Q5 - Generator expression to get even numbers from 1 to 50

UPPER_LIMIT: int = 50

# this looks like list comprehension but with () instead of []
# it doesn't store all values, generates them one by one
even_numbers = (num for num in range(1, UPPER_LIMIT + 1) if num % 2 == 0)

for even in even_numbers:
    print(even, end=" ")
print()
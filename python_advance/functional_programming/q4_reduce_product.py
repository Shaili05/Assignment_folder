# Q4 - Use reduce() to find product of all elements in a list

from functools import reduce

numbers: list[int] = [1, 2, 3, 4, 5]

# reduce takes two elements at a time and keeps combining
# so it goes: 1*2=2, then 2*3=6, then 6*4=24, then 24*5=120
product: int = reduce(lambda a, b: a * b, numbers)

print("Numbers:", numbers)
print("Product of all:", product)
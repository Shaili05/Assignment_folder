# Q3 - Use filter() to extract only even numbers

numbers: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# filter keeps only those values where function returns True
even_numbers: list[int] = list(filter(lambda num: num % 2 == 0, numbers))

print("All numbers:", numbers)
print("Even numbers:", even_numbers)
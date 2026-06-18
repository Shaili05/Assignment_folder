# Q1 - Create an iterator from a list and print using next()

my_list: list[int] = [10, 20, 30, 40]

# iter() converts the list into an iterator object
my_iterator = iter(my_list)

print(next(my_iterator))  # prints 10
print(next(my_iterator))  # prints 20
print(next(my_iterator))  # prints 30
print(next(my_iterator))  # prints 40
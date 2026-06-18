# Q2 - Use map() to convert list of numbers to their squares

numbers: list[int] = [1, 2, 3, 4, 5]

# map applies the function to every item in the list
squared: list[int] = list(map(lambda num: num * num, numbers))

print("Original:", numbers)
print("Squared:", squared)
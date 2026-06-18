# Q8 - Built-in generators like range() and how to iterate them

START: int = 1
END: int = 6

# range() is a built-in generator, it doesn't store all numbers
number_range = range(START, END)

print("Iterating over range:")
for num in number_range:
    print(num, end=" ")
print()

# enumerate() is also a generator - gives index and value together
fruits: list[str] = ["apple", "banana", "mango"]
print("\nUsing enumerate:")
for index, fruit in enumerate(fruits):
    print(index, "->", fruit)
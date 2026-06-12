"""
data_structures.py
Section 4 - Data Structures
Covers: List, Tuple, Set, Dictionary
Questions: Q25 to Q34
"""


# Q25
def list_operations() -> None:
    """
    Q25 - Create a list of 10 numbers and find sum, max, sort it,
    and remove duplicates.
    Performs four different operations on the same list one by one
    and prints the result of each operation.
    """
    numbers = [4, 7, 2, 9, 1, 5, 3, 8, 6, 4]

    print("Original list:", numbers)
    print("Sum:", sum(numbers))
    print("Max:", max(numbers))

    numbers.sort()
    print("Sorted:", numbers)

    print("After removing duplicates:", list(set(numbers)))

print("\n Q25: List Operations ")
list_operations()


# Q26
def count_even_odd() -> None:
    """
    Q26 - Count even and odd numbers in a list.
    Goes through each number in the list and checks if it is
    divisible by 2 to decide if it is even or odd, then counts both.
    """
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    even_count = 0
    odd_count = 0

    for num in numbers:
        if num % 2 == 0:
            even_count += 1
        else:
            odd_count += 1

    print("Even count:", even_count)
    print("Odd count:", odd_count)

print("\n Q26: Count Even and Odd ")
count_even_odd()


# Q27
def reverse_list_manually() -> None:
    """
    Q27 - Reverse a list without using reverse().
    Loops through the original list backwards using range with -1 step
    and builds a new reversed list by appending each element.
    """
    original = [10, 20, 30, 40, 50]
    reversed_list = []

    for i in range(len(original) - 1, -1, -1):
        reversed_list.append(original[i])

    print("Original:", original)
    print("Reversed:", reversed_list)

print("\n Q27: Reverse List Manually ")
reverse_list_manually()


# Q28 and Q29
def tuple_operations() -> None:
    """
    Q28 - Create a tuple and access elements.
    Q29 - Convert tuple into list and modify it.
    Creates a student tuple, accesses individual elements by index,
    then converts it to a list so we can modify a value (tuples are immutable).
    """
    student_tuple = ("Shaili", 21, "Computer Science", 8.5)

    print("Tuple:", student_tuple)
    print("First element:", student_tuple[0])
    print("Last element:", student_tuple[-1])

    student_list = list(student_tuple)
    student_list[1] = 22
    print("Modified list:", student_list)

print("\n Q28 & Q29: Tuple Operations ")
tuple_operations()


# Q30 and Q31
def set_operations() -> None:
    """
    Q30 - Perform union, intersection, and difference on two sets.
    Q31 - Remove duplicates from list using set.
    Creates two sets and performs all three set operations on them.
    Also shows how converting a list to set automatically removes duplicates.
    """
    set_a = {1, 2, 3, 4, 5}
    set_b = {4, 5, 6, 7, 8}

    print("Union:", set_a | set_b)
    print("Intersection:", set_a & set_b)
    print("Difference (A-B):", set_a - set_b)

    numbers_with_duplicates = [1, 2, 2, 3, 4, 4, 5]
    print("Duplicates removed:", list(set(numbers_with_duplicates)))

print("\n Q30 & Q31: Set Operations ")
set_operations()


# Q32
def student_dictionary() -> None:
    """
    Q32 - Create a student dictionary and access values.
    Creates a dictionary with student details as key value pairs
    and accesses specific values using their keys.
    """
    student = {
        "name": "Shaili",
        "age": 21,
        "branch": "Computer Science",
        "cgpa": 8.5
    }

    print("Name:", student["name"])
    print("Branch:", student["branch"])
    print("CGPA:", student["cgpa"])

print("\n Q32: Student Dictionary ")
student_dictionary()


# Q33
def count_character_frequency() -> None:
    """
    Q33 - Count frequency of characters in a string using dictionary.
    Takes a string input from user, loops through each character,
    and builds a dictionary where each key is a character and
    value is how many times it appears.
    """
    text = input("Enter a string: ")
    frequency = {}

    for char in text:
        if char in frequency:
            frequency[char] += 1
        else:
            frequency[char] = 1

    print("Character frequency:", frequency)

print("\n Q33: Character Frequency ")
count_character_frequency()


# Q34
def merge_dictionaries() -> None:
    """
    Q34 - Merge two dictionaries.
    Creates two separate dictionaries and merges them into one
    using the ** unpacking operator which combines both into a new dict.
    """
    first_dict = {"name": "Shaili", "age": 21}
    second_dict = {"branch": "CS", "cgpa": 8.5}

    merged = {**first_dict, **second_dict}
    print("Merged dictionary:", merged)

print("\n Q34: Merge Dictionaries ")
merge_dictionaries()
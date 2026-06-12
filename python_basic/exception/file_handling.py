"""
file_handling.py
Section 5 - File Handling
Questions: Q35 to Q39
"""

# Constants
FILE_NAME = "student_data.txt"
COPY_FILE_NAME = "student_data_copy.txt"


# Q35
def create_and_write_file() -> None:
    """
    Q35 - Create a file and write your name into it.
    Opens a file in write mode which creates it if it does not exist,
    then writes the name into it. Uses 'with' so file closes automatically.
    """
    with open(FILE_NAME, "w") as file:
        file.write("Shaili\n")
    print("File created and name written.")

print("\n Q35: Create and Write File ")
create_and_write_file()


# Q36
def read_and_count() -> None:
    """
    Q36 - Read a file and count words, lines, and characters.
    Opens file in read mode, reads full content as a string,
    then counts newlines for lines, splits for words, and len for characters.
    Has error handling in case file does not exist yet.
    """
    try:
        with open(FILE_NAME, "r") as file:
            content = file.read()

        print("Lines:", content.count("\n"))
        print("Words:", len(content.split()))
        print("Characters:", len(content))

    except FileNotFoundError:
        print("File not found. Run create_and_write_file() first.")

print("\n Q36: Read and Count ")
read_and_count()


# Q37
def append_to_file() -> None:
    """
    Q37 - Append data to existing file.
    Opens the file in append mode so existing content is not lost,
    then adds a new line at the end of the file.
    """
    with open(FILE_NAME, "a") as file:
        file.write("Python Training\n")
    print("Data appended successfully.")

print("\n Q37: Append to File ")
append_to_file()


# Q38
def copy_file() -> None:
    """
    Q38 - Copy content from one file to another.
    Reads all content from the source file and writes it
    into a new destination file. Handles missing file with try except.
    """
    try:
        with open(FILE_NAME, "r") as source:
            content = source.read()

        with open(COPY_FILE_NAME, "w") as destination:
            destination.write(content)

        print("File copied to", COPY_FILE_NAME)

    except FileNotFoundError:
        print("Source file not found.")

print("\n Q38: Copy File ")
copy_file()


# Q39
def search_word_in_file() -> None:
    """
    Q39 - Search a word in a file.
    Takes a word from user, reads the file content,
    splits it into individual words and counts how many
    times the search word appears. Case insensitive search.
    """
    word = input("Enter word to search: ")

    try:
        with open(FILE_NAME, "r") as file:
            content = file.read()

        count = content.lower().split().count(word.lower())

        if count > 0:
            print(f"'{word}' found {count} time(s).")
        else:
            print(f"'{word}' not found in the file.")

    except FileNotFoundError:
        print("File not found.")

print("\n Q39: Search Word in File ")
search_word_in_file()
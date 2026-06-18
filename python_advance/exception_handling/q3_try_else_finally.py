# Q3 - Read a number from a file and print its square
# Using try-except-else-finally all four blocks

FILE_NAME: str = "number.txt"

def read_and_square() -> None:
    """
    Opens a file, reads a number, prints its square.
    Shows all four blocks - try, except, else, finally.
    """
    try:
        file = open(FILE_NAME, "r")
        content: str = file.read()
        number: int = int(content.strip())
    except FileNotFoundError:
        print("File not found, create a file called number.txt first")
    except ValueError:
        # if file has text instead of a number
        print("File content is not a valid number")
    else:
        # this only runs when no exception happens
        print("Square of", number, "is", number ** 2)
    finally:
        # always runs, whether error or not
        print("Program finished")

read_and_square()
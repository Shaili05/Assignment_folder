# Q8 - Handle FileNotFoundError when opening a file that doesn't exist

def open_file(file_name: str) -> None:
    """
    Tries to open a file. If it doesn't exist,
    handles the error instead of crashing.
    """
    try:
        file = open(file_name, "r")
        data: str = file.read()
        print("File content:", data)
        file.close()
    except FileNotFoundError:
        print("File not found:", file_name)

open_file("this_file_doesnt_exist.txt")
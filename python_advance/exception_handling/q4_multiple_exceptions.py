# Q4 - Handle multiple different exceptions in one program

def handle_multiple() -> None:
    """
    Handles ValueError, ZeroDivisionError, and a general
    Exception all in the same try block.
    """
    try:
        value: int = int(input("Enter a number: "))
        result: float = 100 / value
        my_list: list[int] = [1, 2, 3]
        print(my_list[value])
    except ValueError:
        print("Not a valid number")
    except ZeroDivisionError:
        print("Cannot divide by zero")
    except IndexError:
        # accessing index that doesn't exist in the list
        print("Index out of range for the list")
    except Exception as err:
        print("Some other error occurred:", err)

handle_multiple()
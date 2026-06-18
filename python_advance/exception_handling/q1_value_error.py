# Q1 - Handle ValueError when input is not a valid integer

def get_integer_input() -> None:
    """
    Takes a number from user and handles the case
    where they type something like 'abc' instead of a number.
    """
    try:
        user_input: str = input("Enter a number: ")
        number: int = int(user_input)
        print("You entered:", number)
    except ValueError:
        # this runs when the conversion fails
        print("That's not a valid number, please enter digits only")

get_integer_input()
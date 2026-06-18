# Q5 - Catch any and all exceptions and print the error message

def catch_everything() -> None:
    """
    Uses a broad Exception catch to grab any error.
    Useful for logging when we don't know what might go wrong.
    """
    try:
        result: float = 10 / 0
    except Exception as err:
        # 'err' holds the actual error message
        print("Error occurred:", err)

catch_everything()
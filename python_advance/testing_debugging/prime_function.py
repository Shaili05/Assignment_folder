# Helper module that holds the prime checker function

def is_prime(num: int) -> bool:
    """
    Returns True if num is prime, False otherwise.
    Checks divisibility up to square root of num.
    """
    if num < 2:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True
# Q2 - pytest test cases for prime number checker
# Run with: pytest test_prime.py -v

from prime_function import is_prime

def test_small_prime() -> None:
    assert is_prime(2) == True

def test_prime_number() -> None:
    assert is_prime(7) == True

def test_not_prime() -> None:
    # 9 is 3*3 so not prime
    assert is_prime(9) == False

def test_one_is_not_prime() -> None:
    assert is_prime(1) == False

def test_large_prime() -> None:
    assert is_prime(97) == True
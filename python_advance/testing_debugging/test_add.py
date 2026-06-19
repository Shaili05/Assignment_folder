# Q1 - pytest test cases for the add function
# Run with: pytest test_add.py -v

from add_function import add

def test_add_positive_numbers() -> None:
    # normal addition should work
    assert add(2, 3) == 5

def test_add_with_zero() -> None:
    # adding zero should return same number
    assert add(0, 10) == 10

def test_add_negative_numbers() -> None:
    # negative numbers should also work correctly
    assert add(-3, -2) == -5

def test_add_mixed() -> None:
    # one positive one negative
    assert add(-1, 5) == 4
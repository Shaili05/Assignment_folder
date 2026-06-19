"""
Assignment 1: NumPy Basics
Covers creation of arrays, aggregate operations (mean, max, min, sum),
element-wise array operations, and matrix creation.
"""

import numpy as np
from numpy.typing import NDArray


def create_sample_array() -> NDArray:
    """Create and return the sample NumPy array [10, 20, 30, 40, 50]."""
    return np.array([10, 20, 30, 40, 50])


def calculate_array_statistics(input_array: NDArray) -> dict[str, float]:
    """
    Calculate mean, max, min, and sum for a given NumPy array.

    Args:
        input_array: A 1-D NumPy array of numeric values.

    Returns:
        A dictionary containing the calculated statistics.
    """
    return {
        "mean": float(np.mean(input_array)),
        "max": float(np.max(input_array)),
        "min": float(np.min(input_array)),
        "sum": float(np.sum(input_array)),
    }


def add_arrays(first_array: NDArray, second_array: NDArray) -> NDArray:
    """Return the element-wise addition of two NumPy arrays."""
    return first_array + second_array


def multiply_arrays(first_array: NDArray, second_array: NDArray) -> NDArray:
    """Return the element-wise multiplication of two NumPy arrays."""
    return first_array * second_array


def create_3x3_matrix() -> NDArray:
    """Create and return a 3x3 NumPy matrix with sequential values 1-9."""
    return np.arange(1, 10).reshape(3, 3)


def main() -> None:
    """Run all NumPy basics tasks and print the results."""
    sample_array = create_sample_array()
    print("Sample Array:", sample_array)

    statistics = calculate_array_statistics(sample_array)
    print("Mean:", statistics["mean"])
    print("Max:", statistics["max"])
    print("Min:", statistics["min"])
    print("Sum:", statistics["sum"])

    arr_1 = np.array([1, 2, 3])
    arr_2 = np.array([4, 5, 6])

    addition_result = add_arrays(arr_1, arr_2)
    print("\nArray Addition (arr_1 + arr_2):", addition_result)

    multiplication_result = multiply_arrays(arr_1, arr_2)
    print("Array Multiplication (arr_1 * arr_2):", multiplication_result)

    matrix_3x3 = create_3x3_matrix()
    print("\n3x3 Matrix:\n", matrix_3x3)


if __name__ == "__main__":
    main()
"""
Assignment 3: Data Cleaning
Covers detecting missing values and handling them using
mean imputation and zero-fill strategies.
"""

import numpy as np
import pandas as pd

DEFAULT_SALARY_FOR_MISSING: int = 0


def create_employee_dataframe_with_missing_values() -> pd.DataFrame:
    """
    Create and return a DataFrame containing employee details
    with some missing (NaN) values in Age and Salary.

    Returns:
        A DataFrame with columns: Name, Age, Salary.
    """
    employee_data = {
        "Name": ["Rahul", "Priya", "Anuj"],
        "Age": [25, np.nan, 29],
        "Salary": [30000, 40000, np.nan],
    }
    return pd.DataFrame(employee_data)


def detect_missing_values(employee_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect missing values in the DataFrame.

    Returns:
        A boolean DataFrame where True marks a missing value.
    """
    return employee_df.isnull()


def fill_missing_age_with_mean(employee_df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace missing values in the 'Age' column with the column mean.

    Args:
        employee_df: The employee DataFrame to update.

    Returns:
        A new DataFrame with missing Age values filled.
    """
    updated_df = employee_df.copy()
    mean_age = updated_df["Age"].mean()
    updated_df["Age"] = updated_df["Age"].fillna(mean_age)
    return updated_df


def fill_missing_salary_with_zero(employee_df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace missing values in the 'Salary' column with a default value.

    Args:
        employee_df: The employee DataFrame to update.

    Returns:
        A new DataFrame with missing Salary values filled.
    """
    updated_df = employee_df.copy()
    updated_df["Salary"] = updated_df["Salary"].fillna(DEFAULT_SALARY_FOR_MISSING)
    return updated_df


def main() -> None:
    """Run all Data Cleaning tasks and print the results."""
    employee_df = create_employee_dataframe_with_missing_values()
    print("Original DataFrame:\n", employee_df)

    print("\nMissing Values Detected:\n", detect_missing_values(employee_df))

    df_with_age_filled = fill_missing_age_with_mean(employee_df)
    print("\nAfter Filling Missing Age with Mean:\n", df_with_age_filled)

    df_fully_cleaned = fill_missing_salary_with_zero(df_with_age_filled)
    print("\nAfter Filling Missing Salary with 0:\n", df_fully_cleaned)


if __name__ == "__main__":
    main()
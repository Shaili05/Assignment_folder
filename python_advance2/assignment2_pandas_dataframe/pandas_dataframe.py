"""
Assignment 2: Pandas DataFrame Creation
Covers creating a DataFrame, viewing rows, summary statistics,
filtering rows, and adding a derived column.
"""

import pandas as pd

BONUS_PERCENTAGE: float = 0.10


def create_employee_dataframe() -> pd.DataFrame:
    """
    Create and return a DataFrame containing employee details.

    Returns:
        A DataFrame with columns: Name, Age, Department, Salary.
    """
    employee_data = {
        "Name": ["Rahul", "Priya", "Amit", "Anuj"],
        "Age": [25, 30, 28, 35],
        "Department": ["HR", "IT", "Finance", "IT"],
        "Salary": [30000, 50000, 45000, 60000],
    }
    return pd.DataFrame(employee_data)


def get_first_n_rows(employee_df: pd.DataFrame, row_count: int = 2) -> pd.DataFrame:
    """Return the first `row_count` rows of the DataFrame."""
    return employee_df.head(row_count)


def get_summary_statistics(employee_df: pd.DataFrame) -> pd.DataFrame:
    """Return summary statistics (count, mean, std, min, max, etc.) for the DataFrame."""
    return employee_df.describe()


def filter_by_department(employee_df: pd.DataFrame, department_name: str) -> pd.DataFrame:
    """
    Filter and return employees belonging to a specific department.

    Args:
        employee_df: The employee DataFrame to filter.
        department_name: The department to filter by (e.g., "IT").
    """
    return employee_df[employee_df["Department"] == department_name]


def add_bonus_column(employee_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a 'Bonus' column calculated as Salary * BONUS_PERCENTAGE.

    Args:
        employee_df: The employee DataFrame to update.

    Returns:
        A new DataFrame with the additional 'Bonus' column.
    """
    updated_df = employee_df.copy()
    updated_df["Bonus"] = updated_df["Salary"] * BONUS_PERCENTAGE
    return updated_df


def main() -> None:
    """Run all Pandas DataFrame tasks and print the results."""
    employee_df = create_employee_dataframe()
    print("Full Employee DataFrame:\n", employee_df)

    print("\nFirst 2 Rows:\n", get_first_n_rows(employee_df, 2))

    print("\nSummary Statistics:\n", get_summary_statistics(employee_df))

    print("\nIT Employees:\n", filter_by_department(employee_df, "IT"))

    employee_df_with_bonus = add_bonus_column(employee_df)
    print("\nEmployee DataFrame with Bonus Column:\n", employee_df_with_bonus)


if __name__ == "__main__":
    main()
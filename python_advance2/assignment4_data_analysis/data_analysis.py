"""
Assignment 4: Data Analysis using GroupBy
Covers grouping employee data by department to calculate
average salary, max salary, and employee count per department.
"""

import pandas as pd


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


def get_average_salary_by_department(employee_df: pd.DataFrame) -> pd.Series:
    """Return the average salary grouped by department."""
    return employee_df.groupby("Department")["Salary"].mean()


def get_max_salary_by_department(employee_df: pd.DataFrame) -> pd.Series:
    """Return the maximum salary grouped by department."""
    return employee_df.groupby("Department")["Salary"].max()


def get_employee_count_by_department(employee_df: pd.DataFrame) -> pd.Series:
    """Return the count of employees grouped by department."""
    return employee_df.groupby("Department")["Name"].count()


def main() -> None:
    """Run all Data Analysis tasks and print the results."""
    employee_df = create_employee_dataframe()
    print("Employee DataFrame:\n", employee_df)

    print("\nAverage Salary by Department:\n", get_average_salary_by_department(employee_df))

    print("\nMax Salary by Department:\n", get_max_salary_by_department(employee_df))

    print("\nEmployee Count by Department:\n", get_employee_count_by_department(employee_df))


if __name__ == "__main__":
    main()
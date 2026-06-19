"""
Assignment 6: Seaborn Visualizations
Covers creating a barplot (Department vs Salary), a boxplot (Salary
distribution), and a heatmap (correlation between Age and Salary).
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

OUTPUT_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "charts_output")
FIGURE_SIZE: tuple[int, int] = (8, 5)

sns.set_theme(style="whitegrid")


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


def ensure_output_directory_exists() -> None:
    """Create the chart output directory if it does not already exist."""
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)


def create_department_salary_barplot(employee_df: pd.DataFrame) -> None:
    """
    Create and save a barplot showing salary per department.

    Args:
        employee_df: The employee DataFrame to visualize.
    """
    plt.figure(figsize=FIGURE_SIZE)
    sns.barplot(
        data=employee_df,
        x="Department",
        y="Salary",
        hue="Department",
        palette="viridis",
        legend=False,
    )
    plt.title("Department vs Salary", fontweight="bold", fontsize=14)
    plt.xlabel("Department")
    plt.ylabel("Salary")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIRECTORY, "barplot.png"), dpi=150)
    plt.close()


def create_salary_boxplot(employee_df: pd.DataFrame) -> None:
    """
    Create and save a boxplot showing the distribution of salaries.

    Args:
        employee_df: The employee DataFrame to visualize.
    """
    plt.figure(figsize=FIGURE_SIZE)
    sns.boxplot(data=employee_df, y="Salary", color="lightcoral")
    plt.title("Salary Distribution", fontweight="bold", fontsize=14)
    plt.ylabel("Salary")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIRECTORY, "boxplot.png"), dpi=150)
    plt.close()


def create_age_salary_correlation_heatmap(employee_df: pd.DataFrame) -> None:
    """
    Create and save a heatmap showing correlation between Age and Salary.

    Args:
        employee_df: The employee DataFrame to visualize.
    """
    correlation_matrix = employee_df[["Age", "Salary"]].corr()
    plt.figure(figsize=(5, 4))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Correlation: Age vs Salary", fontweight="bold", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIRECTORY, "heatmap.png"), dpi=150)
    plt.close()


def main() -> None:
    """Run all Seaborn visualization tasks and save the output images."""
    employee_df = create_employee_dataframe()
    ensure_output_directory_exists()

    create_department_salary_barplot(employee_df)
    print("Barplot saved.")

    create_salary_boxplot(employee_df)
    print("Boxplot saved.")

    create_age_salary_correlation_heatmap(employee_df)
    print("Heatmap saved.")

    print(f"\nAll charts saved to: {OUTPUT_DIRECTORY}")


if __name__ == "__main__":
    main()
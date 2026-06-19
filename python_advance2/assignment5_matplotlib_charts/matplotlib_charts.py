"""
Assignment 5: Matplotlib Charts
Covers creating a bar chart, line chart, histogram, and scatter plot
using Matplotlib, styled for visual clarity, and saved as image files.
"""

import os

import matplotlib.pyplot as plt

OUTPUT_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "charts_output")

DEPARTMENTS: list[str] = ["HR", "IT", "Finance"]
EMPLOYEE_COUNTS: list[int] = [5, 12, 7]
SALARY_DATA: list[int] = [30000, 40000, 50000, 60000, 45000]
AGE_DATA: list[int] = [25, 30, 28, 35, 40]
AGE_VS_SALARY_DATA: list[int] = [30000, 50000, 45000, 60000, 55000]

FIGURE_SIZE: tuple[int, int] = (8, 5)
PRIMARY_COLOR: str = "#4C72B0"
SECONDARY_COLOR: str = "#DD8452"
ACCENT_COLOR: str = "#55A868"
HIGHLIGHT_COLOR: str = "#C44E52"

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams["font.size"] = 11
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 12


def ensure_output_directory_exists() -> None:
    """Create the chart output directory if it does not already exist."""
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)


def create_bar_chart(departments: list[str], employee_counts: list[int]) -> None:
    """
    Create and save a bar chart of employee count per department.

    Args:
        departments: List of department names.
        employee_counts: List of employee counts corresponding to departments.
    """
    plt.figure(figsize=FIGURE_SIZE)
    bars = plt.bar(
        departments,
        employee_counts,
        color=[PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR],
        edgecolor="black",
        linewidth=0.8,
        width=0.6,
    )
    for bar in bars:
        bar_height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar_height + 0.2,
            str(int(bar_height)),
            ha="center",
            fontweight="bold",
        )
    plt.title("Employee Count by Department")
    plt.xlabel("Department")
    plt.ylabel("Number of Employees")
    plt.ylim(0, max(employee_counts) + 3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIRECTORY, "bar_chart.png"), dpi=150)
    plt.close()


def create_line_chart(departments: list[str], employee_counts: list[int]) -> None:
    """
    Create and save a line chart of employee count per department.

    Args:
        departments: List of department names.
        employee_counts: List of employee counts corresponding to departments.
    """
    plt.figure(figsize=FIGURE_SIZE)
    plt.plot(
        departments,
        employee_counts,
        marker="o",
        markersize=9,
        linewidth=2.5,
        color=SECONDARY_COLOR,
        markerfacecolor=PRIMARY_COLOR,
        markeredgecolor="black",
    )
    for x_value, y_value in zip(departments, employee_counts):
        plt.annotate(
            str(y_value),
            (x_value, y_value),
            textcoords="offset points",
            xytext=(0, 12),
            ha="center",
            fontweight="bold",
        )
    plt.title("Employee Count Trend by Department")
    plt.xlabel("Department")
    plt.ylabel("Number of Employees")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIRECTORY, "line_chart.png"), dpi=150)
    plt.close()


def create_salary_histogram(salary_data: list[int]) -> None:
    """
    Create and save a histogram of salary distribution.

    Args:
        salary_data: List of salary values.
    """
    plt.figure(figsize=FIGURE_SIZE)
    bin_edges = range(25000, 65001, 5000)
    plt.hist(
        salary_data,
        bins=bin_edges,
        color=ACCENT_COLOR,
        edgecolor="black",
        linewidth=1.2,
        alpha=0.85,
        rwidth=0.9,
    )
    plt.title("Salary Distribution")
    plt.xlabel("Salary (in Rs.)")
    plt.ylabel("Number of Employees")
    plt.xticks(list(bin_edges))
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIRECTORY, "histogram.png"), dpi=150)
    plt.close()
    

def create_age_vs_salary_scatter_plot(age_data: list[int], salary_data: list[int]) -> None:
    """
    Create and save a scatter plot of age versus salary.

    Args:
        age_data: List of age values.
        salary_data: List of corresponding salary values.
    """
    plt.figure(figsize=FIGURE_SIZE)
    plt.scatter(
        age_data,
        salary_data,
        color=HIGHLIGHT_COLOR,
        edgecolor="black",
        s=120,
        alpha=0.85,
    )
    plt.title("Age vs Salary")
    plt.xlabel("Age")
    plt.ylabel("Salary")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIRECTORY, "scatter_plot.png"), dpi=150)
    plt.close()


def main() -> None:
    """Run all Matplotlib charting tasks and save the output images."""
    ensure_output_directory_exists()

    create_bar_chart(DEPARTMENTS, EMPLOYEE_COUNTS)
    print("Bar chart saved.")

    create_line_chart(DEPARTMENTS, EMPLOYEE_COUNTS)
    print("Line chart saved.")

    create_salary_histogram(SALARY_DATA)
    print("Histogram saved.")

    create_age_vs_salary_scatter_plot(AGE_DATA, AGE_VS_SALARY_DATA)
    print("Scatter plot saved.")

    print(f"\nAll charts saved to: {OUTPUT_DIRECTORY}")


if __name__ == "__main__":
    main()
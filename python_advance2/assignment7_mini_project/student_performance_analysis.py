"""
Assignment 7: Mini Project - Student Performance Analysis
End-to-end practice: load student data, derive a Pass/Fail performance
column, and visualize the relationship between study hours and marks.
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

OUTPUT_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "charts_output")
FIGURE_SIZE: tuple[int, int] = (8, 5)
PASS_MARK_THRESHOLD: int = 65

sns.set_theme(style="whitegrid")


def create_student_dataframe() -> pd.DataFrame:
    """
    Create and return a DataFrame containing student marks and study hours.

    Returns:
        A DataFrame with columns: Name, Marks, Hours_Studied.
    """
    student_data = {
        "Name": ["Rahul", "Priya", "Siri", "Anuj"],
        "Marks": [70, 80, 90, 60],
        "Hours_Studied": [2, 3, 5, 1],
    }
    return pd.DataFrame(student_data)


def add_performance_column(student_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a 'Performance' column: 'Pass' if Marks > PASS_MARK_THRESHOLD, else 'Fail'.

    Args:
        student_df: The student DataFrame to update.

    Returns:
        A new DataFrame with the additional 'Performance' column.
    """
    updated_df = student_df.copy()
    updated_df["Performance"] = updated_df["Marks"].apply(
        lambda marks: "Pass" if marks > PASS_MARK_THRESHOLD else "Fail"
    )
    return updated_df


def ensure_output_directory_exists() -> None:
    """Create the chart output directory if it does not already exist."""
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)


def create_hours_vs_marks_line_chart(student_df: pd.DataFrame) -> None:
    """
    Create and save a line chart of hours studied vs marks scored.

    Args:
        student_df: The student DataFrame to visualize.
    """
    sorted_df = student_df.sort_values("Hours_Studied")
    plt.figure(figsize=FIGURE_SIZE)
    plt.plot(
        sorted_df["Hours_Studied"],
        sorted_df["Marks"],
        marker="o",
        markersize=9,
        linewidth=2.5,
        color="#DD8452",
        markerfacecolor="#4C72B0",
        markeredgecolor="black",
    )
    plt.title("Hours Studied vs Marks", fontweight="bold", fontsize=14)
    plt.xlabel("Hours Studied")
    plt.ylabel("Marks")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIRECTORY, "hours_vs_marks_line_chart.png"), dpi=150)
    plt.close()


def create_study_vs_marks_scatter_plot(student_df: pd.DataFrame) -> None:
    """
    Create and save a scatter plot of study hours vs marks.

    Args:
        student_df: The student DataFrame to visualize.
    """
    plt.figure(figsize=FIGURE_SIZE)
    plt.scatter(
        student_df["Hours_Studied"],
        student_df["Marks"],
        color="#C44E52",
        edgecolor="black",
        s=120,
        alpha=0.85,
    )
    plt.title("Study Hours vs Marks", fontweight="bold", fontsize=14)
    plt.xlabel("Hours Studied")
    plt.ylabel("Marks")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIRECTORY, "study_vs_marks_scatter.png"), dpi=150)
    plt.close()


def create_performance_vs_marks_barplot(student_df: pd.DataFrame) -> None:
    """
    Create and save a seaborn barplot of performance category vs marks.

    Args:
        student_df: The student DataFrame to visualize.
    """
    plt.figure(figsize=FIGURE_SIZE)
    sns.barplot(
        data=student_df,
        x="Performance",
        y="Marks",
        hue="Performance",
        palette="viridis",
        legend=False,
    )
    plt.title("Performance vs Marks", fontweight="bold", fontsize=14)
    plt.xlabel("Performance")
    plt.ylabel("Marks")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIRECTORY, "performance_vs_marks_barplot.png"), dpi=150)
    plt.close()


def main() -> None:
    """Run the full student performance mini project workflow."""
    student_df = create_student_dataframe()
    print("Original Student DataFrame:\n", student_df)

    student_df_with_performance = add_performance_column(student_df)
    print("\nStudent DataFrame with Performance Column:\n", student_df_with_performance)

    ensure_output_directory_exists()

    create_hours_vs_marks_line_chart(student_df_with_performance)
    print("\nHours vs Marks line chart saved.")

    create_study_vs_marks_scatter_plot(student_df_with_performance)
    print("Study vs Marks scatter plot saved.")

    create_performance_vs_marks_barplot(student_df_with_performance)
    print("Performance vs Marks barplot saved.")

    print(f"\nAll charts saved to: {OUTPUT_DIRECTORY}")


if __name__ == "__main__":
    main()
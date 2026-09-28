import pandas as pd

df = pd.read_csv("data/raw/raw_reviews.csv")

print("Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())
print("\nFirst 3 rows:")
print(df.head(3))
print("\nMissing values per column:")
print(df.isnull().sum())
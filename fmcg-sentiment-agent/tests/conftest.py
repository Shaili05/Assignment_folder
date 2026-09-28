"""
conftest.py

Shared pytest fixtures. Tests use a small in-memory DataFrame instead of the
real reviews_scrubbed.csv, so they run fast and don't depend on the dataset
being present or up to date.
"""

import pandas as pd
import pytest


@pytest.fixture
def sample_reviews():
    data = [
        {
            "review_id": 0, "rating": 5, "sentiment": "positive",
            "aspects": "packaging, texture_effectiveness",
            "product_name": "Test Moisturizer", "brand_name": "TestBrand",
            "submission_time": "2023-01-05", "review_text": "Great packaging, works well.",
            "is_safety_issue": False, "severity_score": 0.0, "issue_type": "none",
            "severity_level": "none", "matched_terms": "",
        },
        {
            "review_id": 1, "rating": 1, "sentiment": "negative",
            "aspects": "texture_effectiveness",
            "product_name": "Test Moisturizer", "brand_name": "TestBrand",
            "submission_time": "2023-01-10", "review_text": "Caused a burning rash on my skin.",
            "is_safety_issue": True, "severity_score": 0.85, "issue_type": "safety",
            "severity_level": "high", "matched_terms": "burning|rash",
        },
        {
            "review_id": 2, "rating": 2, "sentiment": "negative",
            "aspects": "packaging",
            "product_name": "Test Cleanser", "brand_name": "TestBrand",
            "submission_time": "2023-01-15", "review_text": "The pump arrived broken and leaking.",
            "is_safety_issue": True, "severity_score": 0.35, "issue_type": "quality",
            "severity_level": "low", "matched_terms": "damaged|leaking",
        },
        {
            "review_id": 3, "rating": 4, "sentiment": "positive",
            "aspects": "price, texture_effectiveness",
            "product_name": "Test Cleanser", "brand_name": "TestBrand",
            "submission_time": "2023-02-01", "review_text": "A bit pricey but works nicely.",
            "is_safety_issue": False, "severity_score": 0.0, "issue_type": "none",
            "severity_level": "none", "matched_terms": "",
        },
        {
            "review_id": 4, "rating": 3, "sentiment": "neutral",
            "aspects": "texture_effectiveness",
            "product_name": "Test Moisturizer", "brand_name": "TestBrand",
            "submission_time": "2023-02-10", "review_text": "It's okay, nothing special.",
            "is_safety_issue": False, "severity_score": 0.0, "issue_type": "none",
            "severity_level": "none", "matched_terms": "",
        },
    ]
    df = pd.DataFrame(data)
    df["submission_time"] = pd.to_datetime(df["submission_time"])
    return df

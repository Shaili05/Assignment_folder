import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from main import app
from database import users_collection

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def clean_users():
    """Clean up test users before each test"""
    users_collection.delete_many({"email": {"$in": [
        "testuser@test.com",
        "duplicate@test.com"
    ]}})
    yield
    users_collection.delete_many({"email": {"$in": [
        "testuser@test.com",
        "duplicate@test.com"
    ]}})
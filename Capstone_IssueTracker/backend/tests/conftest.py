import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from main import app
from database import users_collection, db

projects_collection = db["projects"]

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    """Clean up test data before each test"""
    # Clean all test users
    users_collection.delete_many({})
    # Clean all test projects
    projects_collection.delete_many({})
    yield
    users_collection.delete_many({})
    projects_collection.delete_many({})
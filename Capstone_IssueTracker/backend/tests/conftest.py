import sys
import os

# CRITICAL: set the test DB name BEFORE any app modules are imported,
# so database.py connects to the test database instead of the real one.
os.environ["DB_NAME"] = "issue_tracker_test_db"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from main import app
from database import users_collection, db

projects_collection = db["projects"]
issues_collection = db["issues"]
sprints_collection = db["sprints"]

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    users_collection.delete_many({})
    projects_collection.delete_many({})
    issues_collection.delete_many({})
    sprints_collection.delete_many({})
    yield
    users_collection.delete_many({})
    projects_collection.delete_many({})
    issues_collection.delete_many({})
    sprints_collection.delete_many({})
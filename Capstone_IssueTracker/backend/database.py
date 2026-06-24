from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "issue_tracker_db")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Collections
users_collection = db["users"]
projects_collection = db["projects"]
issues_collection = db["issues"]
sprints_collection = db["sprints"]
comments_collection = db["comments"]
activity_collection = db["activity_logs"]
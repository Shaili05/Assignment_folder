from datetime import datetime

def user_helper(user) -> dict:
    """Converts MongoDB document to dictionary"""
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "created_at": user.get("created_at", "")
    }

def create_user_document(name: str, email: str, hashed_password: str, role: str) -> dict:
    """Creates a user document to insert into MongoDB"""
    return {
        "name": name,
        "email": email,
        "password": hashed_password,
        "role": role,
        "created_at": datetime.utcnow()
    }
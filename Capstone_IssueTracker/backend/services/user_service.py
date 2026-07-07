import bcrypt
from database import users_collection
from models.user_model import user_helper, create_user_document
from fastapi import HTTPException
from utils.auth import create_access_token
import base64
import binascii
from schemas.user_schema import UserRegister, UserLogin


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check entered password against stored hash"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def register_user(payload: UserRegister):
    """Register a new user - takes the full schema object"""
    existing_user = users_collection.find_one({"email": payload.email})
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    try:
        decoded_password = base64.b64decode(payload.password).decode('utf-8')
    except (binascii.Error, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail="Invalid password encoding")

    hashed_password = hash_password(decoded_password)
    user_doc = create_user_document(payload.name, payload.email, hashed_password, payload.role.value)
    result = users_collection.insert_one(user_doc)
    new_user = users_collection.find_one({"_id": result.inserted_id})
    return user_helper(new_user)

def get_user_by_email(email: str):
    """Find user by email - returns the user dict, or None if not found"""
    user = users_collection.find_one({"email": email})
    if user:
        return user_helper(user)
    return None
    

def login_user(payload: UserLogin):
    """Login user and return JWT token - takes the full schema object"""
    user = users_collection.find_one({"email": payload.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    try:
        decoded_password = base64.b64decode(payload.password).decode('utf-8')
    except (binascii.Error, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail="Invalid password encoding")

    if not verify_password(decoded_password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    from utils.auth import create_token
    token = create_token({
        "user_id": str(user["_id"]),
        "email": user["email"],
        "role": user["role"]
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"]
    }


def get_all_users():
    """Return all users - admin only, used for role management and member assignment"""
    users = users_collection.find()
    return [
        {"id": str(u["_id"]), "name": u["name"], "email": u["email"], "role": u["role"]}
        for u in users
    ]

def update_user_role(user_id: str, new_role: str, current_user_id: str):
    """Admin promotes/demotes a user's role. Admins cannot change their own role."""
    from bson import ObjectId

    if user_id == current_user_id:
        raise HTTPException(status_code=403, detail="Admins cannot change their own role")

    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": new_role}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    updated = users_collection.find_one({"_id": ObjectId(user_id)})
    return {"id": str(updated["_id"]), "name": updated["name"], "email": updated["email"], "role": updated["role"]}


def delete_user(user_id: str, current_user_id: str):
    """Admin deletes a member/viewer account. Cannot delete admins or yourself."""
    from bson import ObjectId

    if user_id == current_user_id:
        raise HTTPException(status_code=403, detail="You cannot delete your own account")

    try:
        target = users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    if target.get("role") == "admin":
        raise HTTPException(status_code=403, detail="Admin accounts cannot be deleted")

    users_collection.delete_one({"_id": ObjectId(user_id)})
    return {"message": "User deleted successfully"}
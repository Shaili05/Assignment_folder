import bcrypt
from database import users_collection
from models.user_model import user_helper, create_user_document
from fastapi import HTTPException
from utils.auth import create_access_token
import base64

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

def register_user(name: str, email: str, password: str, role: str):
    """Register a new user"""
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    decoded_password = base64.b64decode(password).decode('utf-8')
    hashed_password = hash_password(decoded_password)
    user_doc = create_user_document(name, email, hashed_password, role)
    result = users_collection.insert_one(user_doc)
    new_user = users_collection.find_one({"_id": result.inserted_id})
    return user_helper(new_user)

def get_user_by_email(email: str):
    """Find user by email"""
    user = users_collection.find_one({"email": email})
    if user:
        return

def login_user(email: str, password: str):
    """Login user and return JWT token"""
    # Step 1: Find user by email
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Step 2: Check password against stored hash
    decoded_password = base64.b64decode(password).decode('utf-8')
    if not verify_password(decoded_password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Step 3: Create JWT token with user info inside
    token_data = {
        "user_id": str(user["_id"]),
        "email": user["email"],
        "role": user["role"]
    }
    token = create_access_token(token_data)
    
    # Step 4: Return token to client
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"],
        "name": user["name"]
    }
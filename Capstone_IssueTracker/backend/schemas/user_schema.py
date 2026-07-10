from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    member = "member"
    viewer = "viewer"

# What we accept when registering
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.member

# What we accept when logging in
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# What we send back in response (never send password)
class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str

    
class RoleUpdate(BaseModel):
    role: UserRole

class UserListItem(BaseModel):
    id: str
    name: str
    email: str
    role: str#


class ProfileUpdate(BaseModel):
    name: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
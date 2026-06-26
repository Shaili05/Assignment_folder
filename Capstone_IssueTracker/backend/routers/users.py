from fastapi import APIRouter
from schemas.user_schema import UserRegister, UserLogin, UserResponse
from services.user_service import register_user, login_user

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

@router.post("/register", response_model=UserResponse)
def register(user: UserRegister):
    """Register a new user"""
    return register_user(
        name=user.name,
        email=user.email,
        password=user.password,
        role=user.role.value
    )

@router.post("/login")
def login(user: UserLogin):
    """Login and get JWT token
    
    - Checks email exists in database
    - Verifies password against bcrypt hash
    - Returns JWT token valid for 30 minutes
    """
    return login_user(
        email=user.email,
        password=user.password
    )
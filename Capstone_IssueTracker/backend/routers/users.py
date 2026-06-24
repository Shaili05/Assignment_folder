from fastapi import APIRouter
from schemas.user_schema import UserRegister, UserResponse
from services.user_service import register_user

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
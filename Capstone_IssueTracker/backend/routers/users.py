from fastapi import APIRouter, Depends
from schemas.user_schema import UserRegister, UserLogin, UserResponse
from services.user_service import register_user, login_user
from utils.dependencies import get_current_user, require_admin

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
    """Login with email and password, returns JWT token"""
    return login_user(
        email=user.email,
        password=user.password
    )

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Get current logged-in user info - requires valid token"""
    return {
        "user_id": current_user.get("user_id"),
        "email": current_user.get("email"),
        "role": current_user.get("role")
    }

@router.get("/admin-only")
def admin_only(current_user: dict = Depends(require_admin)):
    """Test endpoint - only admin can access this"""
    return {"message": f"Welcome Admin {current_user.get('email')}"}
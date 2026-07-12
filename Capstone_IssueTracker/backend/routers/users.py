from fastapi import APIRouter, Depends
from schemas.user_schema import UserRegister, UserLogin, UserResponse, RoleUpdate, ProfileUpdate, PasswordChange
from services.user_service import (
    register_user, login_user, get_all_users, update_user_role, delete_user,
    get_user_by_id, update_own_profile, change_own_password
)
from utils.dependencies import get_current_user, require_admin

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

@router.post("/register", response_model=UserResponse)
def register(user: UserRegister):
    """Register a new user"""
    return register_user(user)

@router.post("/login")
def login(user: UserLogin):
    """Login with email and password, returns JWT token"""
    return login_user(user)
@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Get current logged-in user's full profile info"""
    return get_user_by_id(current_user.get("user_id"))

@router.patch("/me")
def update_me(payload: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    """Update own name. Email cannot be changed."""
    return update_own_profile(current_user.get("user_id"), payload.name)

@router.patch("/me/password")
def change_my_password(payload: PasswordChange, current_user: dict = Depends(get_current_user)):
    return change_own_password(current_user.get("user_id"), payload.current_password, payload.new_password)

@router.get("/admin-only")
def admin_only(current_user: dict = Depends(require_admin)):
    """Test endpoint - only admin can access this"""
    return {"message": f"Welcome Admin {current_user.get('email')}"}

@router.get("/")
def list_users(skip: int = 0, limit: int = 0, current_user: dict = Depends(require_admin)):
    """List all users - admin only. Optional pagination: ?skip=0&limit=20"""
    return get_all_users(skip, limit)

@router.patch("/{user_id}/role")
def change_user_role(user_id: str, payload: RoleUpdate, current_user: dict = Depends(require_admin)):
    """Promote/demote a user's role - admin only"""
    return update_user_role(user_id, payload.role.value, current_user.get("user_id"))

@router.delete("/{user_id}")
def remove_user(user_id: str, current_user: dict = Depends(require_admin)):
    """Delete a member/viewer account - admin only. Cannot delete admins or self."""
    return delete_user(user_id, current_user.get("user_id"))
# This file is the auth guard - it checks if the request has a valid JWT token
# and returns the current logged-in user's data

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.auth import decode_token

# This tells FastAPI to look for "Bearer <token>" in the Authorization header
bearer_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    # Extract the token from the header
    token = credentials.credentials

    # Decode and verify the token
    payload = decode_token(token)

    # If token is invalid or expired, decode_token returns None
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    return payload  # payload has user_id, email, role

def require_admin(current_user: dict = Depends(get_current_user)):
    # Check if the logged-in user has admin role
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
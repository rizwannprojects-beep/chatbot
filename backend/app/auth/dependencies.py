from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.auth.security import decode_access_token
from app.database.users_db import get_user_by_id
from app.schemas.auth import UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """
    Extracts and validates JWT token, returning the authenticated user profile.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    user_data = get_user_by_id(user_id)
    if user_data is None:
        raise credentials_exception
        
    return UserResponse(**user_data)

async def require_admin(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """
    Authorization dependency that restricts route access to users with role='admin'.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def require_student(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """
    Authorization dependency ensuring the user is an authenticated student or user.
    """
    return current_user

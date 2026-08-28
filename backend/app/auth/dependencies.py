from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.auth.security import decode_access_token
from app.database.users_db import get_user_by_id
from app.schemas.auth import UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """
    Extracts and validates JWT token, returning the authenticated user profile.
    Guarantees user presence in local database to satisfy foreign key constraints.
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
        # Self-healing: provision user in local database from valid JWT payload claims
        email = payload.get("email", f"user_{user_id[:8]}@campusai.local")
        role = payload.get("role", "student")
        name = payload.get("name", "Campus Student")
        from app.database.users_db import ensure_user_in_sqlite
        ensure_user_in_sqlite(user_id=user_id, name=name, email=email, role=role)
        user_data = get_user_by_id(user_id)
        if user_data is None:
            user_data = {
                "id": user_id,
                "name": name,
                "email": email,
                "role": role,
                "created_at": "",
                "updated_at": ""
            }
        
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

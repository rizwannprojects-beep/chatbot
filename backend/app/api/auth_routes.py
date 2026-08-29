from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse
from app.database.users_db import get_user_by_email, create_user_record
from app.auth.security import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister):
    """
    Registers a new student or admin user.
    Hashes password before database persistence.
    """
    existing_user = get_user_by_email(payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists"
        )
    
    hashed_pwd = hash_password(payload.password)
    user_record = create_user_record(
        name=payload.name,
        email=payload.email,
        password_hash=hashed_pwd,
        role=payload.role or "student"
    )
    
    access_token = create_access_token(data={
        "sub": user_record["id"],
        "email": user_record["email"],
        "name": user_record["name"],
        "role": user_record["role"]
    })
    
    user_response = UserResponse(**user_record)
    return TokenResponse(access_token=access_token, token_type="bearer", user=user_response)

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    """
    Authenticates user email and password.
    Returns JWT access token upon successful authentication.
    """
    email_clean = payload.email.lower().strip()
    if email_clean in ["student_test@college.edu", "admin_test@college.edu"]:
        from app.database.users_db import ensure_demo_users
        ensure_demo_users()

    user_record = get_user_by_email(payload.email)
    if not user_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(payload.password, user_record["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={
        "sub": user_record["id"],
        "email": user_record["email"],
        "name": user_record["name"],
        "role": user_record["role"]
    })
    user_response = UserResponse(**user_record)
    
    return TokenResponse(access_token=access_token, token_type="bearer", user=user_response)

@router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """
    Logs out the user session.
    """
    return {"success": True, "message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """
    Returns profile information for the current authenticated user.
    """
    return current_user

@router.get("/admin-only")
async def admin_only_check(admin_user: UserResponse = Depends(require_admin)):
    """
    Test endpoint verifying role-based authorization for administrators.
    """
    return {
        "success": True,
        "message": f"Welcome Admin {admin_user.name}! Admin authorization confirmed.",
        "admin": admin_user
    }

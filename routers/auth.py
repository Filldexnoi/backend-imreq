from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
import models
import schemas
from services.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_active_user
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = models.User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=schemas.Token)
async def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Login with username and password
    Returns JWT access token
    """
    user = authenticate_user(db, login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=schemas.User)
async def get_current_user_info(
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get current user information
    """
    return current_user

@router.put("/me", response_model=schemas.User)
async def update_current_user(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user information
    """
    # Check email uniqueness if changed
    if user_update.email and user_update.email != current_user.email:
        existing_email = db.query(models.User).filter(
            models.User.email == user_update.email,
            models.User.id != current_user.id
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        current_user.email = user_update.email
    
    # Check username uniqueness if changed
    if user_update.username and user_update.username != current_user.username:
        existing_username = db.query(models.User).filter(
            models.User.username == user_update.username,
            models.User.id != current_user.id
        ).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = user_update.username
    
    # Update other fields
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.password:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.post("/logout")
async def logout(current_user: models.User = Depends(get_current_active_user)):
    """
    Logout (client should discard token)
    """
    return {"message": "Successfully logged out"}
"""Authentication router"""
from datetime import datetime, timezone
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr, validator

from src.database.connection import get_db
from src.database.models.user import User
from src.core.auth import (
    hash_password, 
    verify_password, 
    create_token_pair,
    refresh_access_token,
    verify_token
)
from src.api.dependencies.auth import get_current_user, get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for request/response
class UserCreate(BaseModel):
    """User registration request"""
    username: str
    email: EmailStr
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        return v.strip().lower()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserLogin(BaseModel):
    """User login request"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes in seconds


class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str


class UserResponse(BaseModel):
    """User response model"""
    id: str
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    created_at: str
    last_login: str = None

    class Config:
        from_attributes = True


# Authentication endpoints
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If username or email already exists
    """
    try:
        # Check if user already exists
        stmt = select(User).where(
            (User.username == user_data.username) | 
            (User.email == user_data.email)
        )
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            if existing_user.username == user_data.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        logger.info(f"New user registered: {user_data.username}")
        
        return UserResponse(
            id=str(db_user.id),
            username=db_user.username,
            email=db_user.email,
            is_active=db_user.is_active,
            is_superuser=db_user.is_superuser,
            created_at=db_user.created_at.isoformat(),
            last_login=db_user.last_login.isoformat() if db_user.last_login else None
        )
        
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens
    
    Args:
        user_credentials: Login credentials
        db: Database session
        
    Returns:
        JWT access and refresh tokens
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        # Find user by username
        stmt = select(User).where(User.username == user_credentials.username.lower())
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        # Verify user exists and password is correct
        if not user or not verify_password(user_credentials.password, user.hashed_password):
            logger.warning(f"Failed login attempt for username: {user_credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update last login timestamp
        stmt = update(User).where(User.id == user.id).values(
            last_login=datetime.now(timezone.utc)
        )
        await db.execute(stmt)
        await db.commit()
        
        # Create tokens
        tokens = create_token_pair(user.id, user.username, user.email)
        
        logger.info(f"Successful login for user: {user.username}")
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/login-form", response_model=TokenResponse)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible login endpoint (for OpenAPI docs)
    
    Args:
        form_data: OAuth2 form data
        db: Database session
        
    Returns:
        JWT access and refresh tokens
    """
    # Convert form data to our login model
    user_credentials = UserLogin(
        username=form_data.username,
        password=form_data.password
    )
    
    # Reuse the main login logic
    return await login(user_credentials, db)


@router.post("/refresh", response_model=dict)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    Args:
        token_data: Refresh token data
        db: Database session
        
    Returns:
        New access token
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        new_access_token = refresh_access_token(token_data.refresh_token)
        
        if not new_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        created_at=current_user.created_at.isoformat(),
        last_login=current_user.last_login.isoformat() if current_user.last_login else None
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side token removal)
    
    Note: With JWT, logout is typically handled client-side by removing the token.
    This endpoint exists for consistency and could be extended to maintain a 
    blacklist of invalidated tokens if needed.
    
    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}


@router.get("/validate")
async def validate_token(
    current_user: User = Depends(get_current_active_user)
):
    """
    Validate current token (useful for client-side token verification)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Token validation status and user info
    """
    return {
        "valid": True,
        "user": {
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
            "is_active": current_user.is_active
        }
    }
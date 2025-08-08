"""
Authentication utilities for JWT and password handling
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
import logging

from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt

from src.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary containing user data to encode
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token
    
    Args:
        data: Dictionary containing user data to encode
        
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            logger.warning(f"Token type mismatch. Expected {token_type}, got {payload.get('type')}")
            return None
            
        # Check expiration
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            if datetime.now(timezone.utc) > exp_datetime:
                logger.warning("Token has expired")
                return None
        
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        User ID string or None if invalid
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")  # 'sub' is the standard JWT claim for subject (user ID)
    return None


def create_token_pair(user_id: str, username: str, email: str) -> dict:
    """
    Create both access and refresh tokens for a user
    
    Args:
        user_id: User's unique identifier
        username: User's username
        email: User's email
        
    Returns:
        Dictionary containing both tokens
    """
    token_data = {
        "sub": str(user_id),  # 'sub' is standard for user identifier
        "username": username,
        "email": email
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    Generate a new access token using a refresh token
    
    Args:
        refresh_token: Valid refresh token
        
    Returns:
        New access token or None if refresh token is invalid
    """
    payload = verify_token(refresh_token, token_type="refresh")
    if not payload:
        return None
    
    # Create new access token with same user data
    new_token_data = {
        "sub": payload.get("sub"),
        "username": payload.get("username"),
        "email": payload.get("email")
    }
    
    return create_access_token(new_token_data)
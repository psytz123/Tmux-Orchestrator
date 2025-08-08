"""
Authentication dependencies for FastAPI
"""
from typing import Optional
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.connection import get_db
from src.database.models.user import User
from src.core.auth import verify_token, get_user_id_from_token

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()


class AuthenticationError(HTTPException):
    """Custom authentication error"""
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Custom authorization error"""
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        User object
        
    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Verify the token
    payload = verify_token(token, token_type="access")
    if not payload:
        logger.warning("Invalid or expired token")
        raise AuthenticationError("Invalid or expired token")
    
    # Extract user ID
    user_id = payload.get("sub")
    if not user_id:
        logger.warning("Token missing user ID")
        raise AuthenticationError("Token missing user ID")
    
    # Get user from database
    try:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise AuthenticationError("User not found")
        
        if not user.is_active:
            logger.warning(f"User account disabled: {user_id}")
            raise AuthenticationError("User account disabled")
            
        return user
        
    except Exception as e:
        logger.error(f"Database error during user lookup: {e}")
        raise AuthenticationError("Database error during authentication")


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (alias for get_current_user with explicit active check)
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Active user object
        
    Raises:
        AuthenticationError: If user is not active
    """
    if not current_user.is_active:
        raise AuthenticationError("User account disabled")
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current superuser (admin access required)
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Superuser object
        
    Raises:
        AuthorizationError: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise AuthorizationError("Superuser access required")
    return current_user


async def get_optional_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """
    Get current user if token is provided and valid, otherwise return None
    Useful for endpoints that work both with and without authentication
    
    Args:
        db: Database session
        credentials: Optional HTTP Bearer credentials
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = verify_token(token, token_type="access")
        
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        stmt = select(User).where(User.id == user_id, User.is_active == True)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        return user
        
    except Exception as e:
        logger.debug(f"Optional authentication failed: {e}")
        return None


def require_permissions(*required_permissions: str):
    """
    Decorator factory for requiring specific permissions
    Note: This is a placeholder for future role-based access control
    
    Args:
        required_permissions: List of required permission strings
        
    Returns:
        Dependency function
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        # Placeholder: In a real app, you'd check user roles/permissions here
        # For now, we'll just ensure user is active
        if not current_user.is_active:
            raise AuthorizationError("User account disabled")
        
        # Future: Check if user has required permissions
        # for permission in required_permissions:
        #     if not user_has_permission(current_user, permission):
        #         raise AuthorizationError(f"Missing permission: {permission}")
        
        return current_user
    
    return permission_checker
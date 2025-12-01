from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.apps.services.auth_service import AuthenticationService
from app.infrastructure.repositories.user_inmemory import InMemoryUserRepository
from app.domain.user_aggregate import User
from app.schemas.auth_schemas import CurrentUserResponse

security = HTTPBearer()

# Create shared instances to avoid circular imports
_user_repo = InMemoryUserRepository()
_auth_service = AuthenticationService(_user_repo)


def get_auth_service() -> AuthenticationService:
    """Dependency to get authentication service"""
    return _auth_service


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthenticationService = Depends(get_auth_service)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    user = auth_service.get_current_user(credentials.credentials)
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user
    """
    if not current_user.is_active():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user


def require_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to require admin user
    """
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def to_current_user_response(user: User) -> CurrentUserResponse:
    """Convert User domain object to CurrentUserResponse schema"""
    return CurrentUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        status=user.status,
    )
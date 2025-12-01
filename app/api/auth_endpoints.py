from __future__ import annotations

from fastapi import APIRouter, HTTPException, status, Depends

from app.apps.services.auth_service import AuthenticationService
from app.schemas.auth_schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    CurrentUserResponse,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


def get_auth_service() -> AuthenticationService:
    """Dependency to get authentication service"""
    # Import here to avoid circular imports
    from app.middleware.auth import get_auth_service as get_service
    return get_service()


def to_user_response(user) -> UserResponse:
    """Convert User domain object to UserResponse schema"""
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        status=user.status,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegisterRequest, auth_service: AuthenticationService = Depends(get_auth_service)):
    """Register a new user"""
    try:
        user = auth_service.register_user(
            username=payload.username,
            email=payload.email,
            password=payload.password,
            role=payload.role,
        )
        return to_user_response(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLoginRequest, auth_service: AuthenticationService = Depends(get_auth_service)):
    """Authenticate user and return JWT token"""
    user = auth_service.authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(data={"sub": user.username})
    return TokenResponse(access_token=access_token)
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.domain.user_aggregate import User
from app.schemas.auth_schemas import CurrentUserResponse
from app.middleware.auth import get_current_active_user

# Create router for user-related endpoints that require authentication
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=CurrentUserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return to_current_user_response(current_user)


def to_current_user_response(user: User) -> CurrentUserResponse:
    """Convert User domain object to CurrentUserResponse schema"""
    return CurrentUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        status=user.status,
    )
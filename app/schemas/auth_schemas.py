from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr

from app.domain.value_objects import UserRole, UserStatus


class UserRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.CUSTOMER


class UserLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: UserRole
    status: UserStatus


class CurrentUserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: UserRole
    status: UserStatus
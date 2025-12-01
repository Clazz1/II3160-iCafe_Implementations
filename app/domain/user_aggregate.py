from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.domain.value_objects import UserRole, UserStatus, Contact


@dataclass
class User:
    id: str
    username: str
    email: str
    hashed_password: str
    role: UserRole
    status: UserStatus = UserStatus.ACTIVE
    contact: Optional[Contact] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def activate(self) -> None:
        """Activate the user account"""
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def suspend(self) -> None:
        """Suspend the user account"""
        self.status = UserStatus.SUSPENDED
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate the user account"""
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.utcnow()

    def update_contact(self, contact: Contact) -> None:
        """Update user contact information"""
        self.contact = contact
        self.updated_at = datetime.utcnow()

    def is_active(self) -> bool:
        """Check if user is active"""
        return self.status == UserStatus.ACTIVE

    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == UserRole.ADMIN
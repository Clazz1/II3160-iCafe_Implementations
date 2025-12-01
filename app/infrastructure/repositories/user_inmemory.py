from __future__ import annotations

from typing import Optional

from app.domain.user_aggregate import User
from app.infrastructure.repositories.base import AbstractInMemoryRepository


class InMemoryUserRepository(AbstractInMemoryRepository[User]):
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user in self._items.values():
            if user.username == username:
                return user
        return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        for user in self._items.values():
            if user.email == email:
                return user
        return None
    
    def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        return self.get_by_username(username) is not None
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        return self.get_by_email(email) is not None
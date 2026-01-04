"""Tests for middleware layer"""
from __future__ import annotations

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from app.middleware.auth import (
    get_current_user,
    get_current_active_user,
    require_admin_user,
    to_current_user_response,
    get_auth_service,
    _auth_service,
    _user_repo,
)
from app.domain.value_objects import UserRole, UserStatus


class TestMiddlewareAuth:
    """Tests for authentication middleware"""

    def setup_method(self):
        """Setup fresh state for each test"""
        _user_repo._items.clear()

    def test_get_auth_service(self):
        """Test get_auth_service returns AuthenticationService"""
        service = get_auth_service()
        assert service is not None
        assert service == _auth_service

    def test_to_current_user_response(self):
        """Test to_current_user_response conversion"""
        user = _auth_service.register_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            role=UserRole.CUSTOMER,
        )
        response = to_current_user_response(user)
        assert response.id == user.id
        assert response.username == user.username
        assert response.email == user.email
        assert response.role == user.role
        assert response.status == user.status


class TestMiddlewareDependencies:
    """Tests for FastAPI dependency functions"""

    def setup_method(self):
        """Setup test application with protected routes"""
        _user_repo._items.clear()
        
        self.app = FastAPI()
        
        @self.app.get("/protected")
        def protected_route(user=Depends(get_current_active_user)):
            return {"username": user.username}
        
        @self.app.get("/admin-only")
        def admin_route(user=Depends(require_admin_user)):
            return {"username": user.username, "role": user.role.value}
        
        self.client = TestClient(self.app)
        
        # Register a user
        self.user = _auth_service.register_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            role=UserRole.CUSTOMER,
        )
        self.token = _auth_service.create_access_token(data={"sub": "testuser"})
        
        # Register an admin
        self.admin = _auth_service.register_user(
            username="adminuser",
            email="admin@example.com",
            password="password123",
            role=UserRole.ADMIN,
        )
        self.admin_token = _auth_service.create_access_token(data={"sub": "adminuser"})

    def test_get_current_user_valid_token(self):
        """Test get_current_user with valid token"""
        response = self.client.get(
            "/protected",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"

    def test_get_current_user_no_token(self):
        """Test get_current_user without token"""
        response = self.client.get("/protected")
        assert response.status_code == 403

    def test_get_current_user_invalid_token(self):
        """Test get_current_user with invalid token"""
        response = self.client.get(
            "/protected",
            headers={"Authorization": "Bearer invalid.token"}
        )
        assert response.status_code == 401

    def test_get_current_active_user_inactive(self):
        """Test get_current_active_user with inactive user returns 401
        
        Note: In the current implementation, get_current_user() in auth_service
        already checks if user is active and returns None for inactive users,
        which results in 401 Unauthorized rather than 400 Bad Request.
        """
        self.user.deactivate()
        response = self.client.get(
            "/protected",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        # Returns 401 because get_current_user returns None for inactive users
        assert response.status_code == 401

    def test_require_admin_user_success(self):
        """Test require_admin_user with admin token"""
        response = self.client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["role"] == "ADMIN"

    def test_require_admin_user_non_admin(self):
        """Test require_admin_user with non-admin token"""
        response = self.client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

"""Tests for API endpoints using FastAPI TestClient"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import create_app


class TestAuthEndpoints:
    """Tests for authentication endpoints"""

    def setup_method(self):
        """Setup test client for each test"""
        self.app = create_app()
        self.client = TestClient(self.app)
        # Clear any existing users by restarting the service
        from app.middleware.auth import _user_repo
        _user_repo._items.clear()

    def test_register_success(self):
        """Test successful user registration"""
        response = self.client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "role": "CUSTOMER",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["role"] == "CUSTOMER"

    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        # First registration
        self.client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test1@example.com",
                "password": "password123",
                "role": "CUSTOMER",
            },
        )
        # Second registration with same username
        response = self.client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test2@example.com",
                "password": "password456",
                "role": "CUSTOMER",
            },
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        # First registration
        self.client.post(
            "/auth/register",
            json={
                "username": "testuser1",
                "email": "test@example.com",
                "password": "password123",
                "role": "CUSTOMER",
            },
        )
        # Second registration with same email
        response = self.client.post(
            "/auth/register",
            json={
                "username": "testuser2",
                "email": "test@example.com",
                "password": "password456",
                "role": "CUSTOMER",
            },
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_login_success(self):
        """Test successful login"""
        # Register first
        self.client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "role": "CUSTOMER",
            },
        )
        # Login
        response = self.client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        """Test login with wrong password"""
        # Register first
        self.client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "role": "CUSTOMER",
            },
        )
        # Login with wrong password
        response = self.client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self):
        """Test login with nonexistent user"""
        response = self.client.post(
            "/auth/login",
            json={
                "username": "nonexistent",
                "password": "password123",
            },
        )
        assert response.status_code == 401


class TestProtectedEndpoints:
    """Tests for protected endpoints requiring authentication"""

    def setup_method(self):
        """Setup test client and auth token for each test"""
        self.app = create_app()
        self.client = TestClient(self.app)
        
        # Clear repositories
        from app.middleware.auth import _user_repo
        from app.api.reservation_endpoints import _reservation_repo
        from app.api.billing_endpoints import _session_repo
        from app.api.payment_endpoints import _invoice_repo
        _user_repo._items.clear()
        _reservation_repo._items.clear()
        _session_repo._items.clear()
        _invoice_repo._items.clear()
        
        # Register and login to get token
        self.client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "role": "CUSTOMER",
            },
        )
        response = self.client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "password123",
            },
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_get_current_user(self):
        """Test getting current user info"""
        response = self.client.get("/users/me", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"

    def test_get_current_user_no_auth(self):
        """Test getting current user without authentication returns 401 or 403"""
        response = self.client.get("/users/me")
        # HTTPBearer returns 403 on some platforms, 401 on others
        assert response.status_code in [401, 403]

    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token"""
        response = self.client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401


class TestReservationEndpoints:
    """Tests for reservation endpoints"""

    def setup_method(self):
        """Setup test client and auth token"""
        self.app = create_app()
        self.client = TestClient(self.app)
        
        # Clear repositories
        from app.middleware.auth import _user_repo
        from app.api.reservation_endpoints import _reservation_repo
        _user_repo._items.clear()
        _reservation_repo._items.clear()
        
        # Register and login
        self.client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "role": "CUSTOMER",
            },
        )
        response = self.client.post(
            "/auth/login",
            json={"username": "testuser", "password": "password123"},
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_create_reservation(self):
        """Test creating a reservation"""
        start = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        end = (datetime.utcnow() + timedelta(hours=3)).isoformat()
        
        response = self.client.post(
            "/reservations",
            headers=self.headers,
            json={
                "customer_id": "cust-1",
                "workstation_id": "ws-1",
                "start": start,
                "end": end,
                "package_name": "Basic",
                "package_duration_minutes": 120,
                "package_price_amount": 20000,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == "cust-1"
        assert data["status"] == "CONFIRMED"

    def test_list_reservations(self):
        """Test listing reservations"""
        response = self.client.get("/reservations", headers=self.headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_check_in_reservation(self):
        """Test check-in to a reservation"""
        # Create reservation first
        start = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        end = (datetime.utcnow() + timedelta(hours=3)).isoformat()
        
        create_response = self.client.post(
            "/reservations",
            headers=self.headers,
            json={
                "customer_id": "cust-1",
                "workstation_id": "ws-1",
                "start": start,
                "end": end,
                "package_name": "Basic",
                "package_duration_minutes": 120,
                "package_price_amount": 20000,
            },
        )
        reservation_id = create_response.json()["id"]
        
        # Check-in
        response = self.client.post(
            f"/reservations/{reservation_id}/check-in",
            headers=self.headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "CHECKED_IN"

    def test_check_in_nonexistent(self):
        """Test check-in to nonexistent reservation"""
        response = self.client.post(
            "/reservations/nonexistent-id/check-in",
            headers=self.headers,
        )
        assert response.status_code == 404


class TestSessionEndpoints:
    """Tests for session/billing endpoints"""

    def setup_method(self):
        """Setup test client and auth token"""
        self.app = create_app()
        self.client = TestClient(self.app)
        
        # Clear repositories
        from app.middleware.auth import _user_repo
        from app.api.billing_endpoints import _session_repo
        _user_repo._items.clear()
        _session_repo._items.clear()
        
        # Register and login
        self.client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "role": "CUSTOMER",
            },
        )
        response = self.client.post(
            "/auth/login",
            json={"username": "testuser", "password": "password123"},
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_start_session(self):
        """Test starting a session"""
        response = self.client.post(
            "/sessions",
            headers=self.headers,
            json={
                "customer_id": "cust-1",
                "workstation_id": "ws-1",
                "reservation_id": "res-1",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == "cust-1"
        assert data["status"] == "ACTIVE"

    def test_list_sessions(self):
        """Test listing sessions"""
        response = self.client.get("/sessions", headers=self.headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_finish_session(self):
        """Test finishing a session"""
        # Start session first
        create_response = self.client.post(
            "/sessions",
            headers=self.headers,
            json={
                "customer_id": "cust-1",
                "workstation_id": "ws-1",
            },
        )
        session_id = create_response.json()["id"]
        
        # Finish session
        response = self.client.post(
            f"/sessions/{session_id}/finish",
            headers=self.headers,
            json={
                "tariff_name": "Standard",
                "rate_per_minute": 100,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "FINISHED"
        assert data["bill_id"] is not None

    def test_finish_nonexistent_session(self):
        """Test finishing nonexistent session"""
        response = self.client.post(
            "/sessions/nonexistent-id/finish",
            headers=self.headers,
            json={
                "tariff_name": "Standard",
                "rate_per_minute": 100,
            },
        )
        assert response.status_code == 404


class TestInvoiceEndpoints:
    """Tests for invoice/payment endpoints"""

    def setup_method(self):
        """Setup test client and auth token"""
        self.app = create_app()
        self.client = TestClient(self.app)
        
        # Clear repositories
        from app.middleware.auth import _user_repo
        from app.api.payment_endpoints import _invoice_repo
        _user_repo._items.clear()
        _invoice_repo._items.clear()
        
        # Register and login
        self.client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "role": "CUSTOMER",
            },
        )
        response = self.client.post(
            "/auth/login",
            json={"username": "testuser", "password": "password123"},
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_create_invoice(self):
        """Test creating an invoice"""
        response = self.client.post(
            "/invoices",
            headers=self.headers,
            json={
                "bill_id": "bill-1",
                "customer_id": "cust-1",
                "amount_due": 10000,
                "phone": "08123456789",
                "email": "test@example.com",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["bill_id"] == "bill-1"
        assert data["status"] == "UNPAID"

    def test_list_invoices(self):
        """Test listing invoices"""
        response = self.client.get("/invoices", headers=self.headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_pay_invoice(self):
        """Test paying an invoice"""
        # Create invoice first
        create_response = self.client.post(
            "/invoices",
            headers=self.headers,
            json={
                "bill_id": "bill-1",
                "customer_id": "cust-1",
                "amount_due": 10000,
            },
        )
        invoice_id = create_response.json()["id"]
        
        # Pay invoice
        response = self.client.post(
            f"/invoices/{invoice_id}/pay",
            headers=self.headers,
            json={"method": "CASH"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SETTLED"
        assert data["payment_status"] == "SETTLED"

    def test_pay_nonexistent_invoice(self):
        """Test paying nonexistent invoice"""
        response = self.client.post(
            "/invoices/nonexistent-id/pay",
            headers=self.headers,
            json={"method": "CASH"},
        )
        assert response.status_code == 404

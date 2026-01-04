"""Tests for service layer"""
from __future__ import annotations

import pytest
from datetime import datetime, timedelta

from app.apps.services.auth_service import AuthenticationService
from app.apps.services.reservation_service import ReservationService
from app.apps.services.billing_service import BillingService
from app.apps.services.payment_service import PaymentService

from app.infrastructure.repositories.user_inmemory import InMemoryUserRepository
from app.infrastructure.repositories.reservation_inmemory import InMemoryReservationRepository
from app.infrastructure.repositories.session_inmemory import InMemorySessionRepository
from app.infrastructure.repositories.invoice_inmemory import InMemoryInvoiceRepository

from app.domain.value_objects import UserRole, UserStatus


class TestAuthenticationService:
    """Tests for AuthenticationService"""

    def setup_method(self):
        """Setup fresh repository for each test"""
        self.user_repo = InMemoryUserRepository()
        self.auth_service = AuthenticationService(self.user_repo)

    def test_register_user_success(self):
        """Test successful user registration"""
        user = self.auth_service.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == UserRole.CUSTOMER
        assert user.status == UserStatus.ACTIVE

    def test_register_user_with_admin_role(self):
        """Test registration with admin role"""
        user = self.auth_service.register_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            role=UserRole.ADMIN
        )
        assert user.role == UserRole.ADMIN

    def test_register_user_duplicate_username_raises(self):
        """Test registration with duplicate username raises error"""
        self.auth_service.register_user(
            username="testuser",
            email="test1@example.com",
            password="password123"
        )
        with pytest.raises(ValueError, match="Username already exists"):
            self.auth_service.register_user(
                username="testuser",
                email="test2@example.com",
                password="password456"
            )

    def test_register_user_duplicate_email_raises(self):
        """Test registration with duplicate email raises error"""
        self.auth_service.register_user(
            username="testuser1",
            email="test@example.com",
            password="password123"
        )
        with pytest.raises(ValueError, match="Email already exists"):
            self.auth_service.register_user(
                username="testuser2",
                email="test@example.com",
                password="password456"
            )

    def test_password_hashing(self):
        """Test password is hashed"""
        user = self.auth_service.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        assert user.hashed_password != "password123"
        assert self.auth_service.verify_password("password123", user.hashed_password)

    def test_authenticate_user_success(self):
        """Test successful authentication"""
        self.auth_service.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        user = self.auth_service.authenticate_user("testuser", "password123")
        assert user is not None
        assert user.username == "testuser"

    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password returns None"""
        self.auth_service.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        user = self.auth_service.authenticate_user("testuser", "wrongpassword")
        assert user is None

    def test_authenticate_user_nonexistent(self):
        """Test authentication with nonexistent user returns None"""
        user = self.auth_service.authenticate_user("nonexistent", "password123")
        assert user is None

    def test_authenticate_inactive_user(self):
        """Test authentication of inactive user returns None"""
        user = self.auth_service.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        user.deactivate()
        result = self.auth_service.authenticate_user("testuser", "password123")
        assert result is None

    def test_create_access_token(self):
        """Test JWT token creation"""
        token = self.auth_service.create_access_token(data={"sub": "testuser"})
        assert token is not None
        assert isinstance(token, str)

    def test_create_access_token_with_expiry(self):
        """Test JWT token creation with custom expiry"""
        token = self.auth_service.create_access_token(
            data={"sub": "testuser"},
            expires_delta=timedelta(hours=1)
        )
        assert token is not None

    def test_decode_access_token_valid(self):
        """Test decoding valid token"""
        token = self.auth_service.create_access_token(data={"sub": "testuser"})
        payload = self.auth_service.decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"

    def test_decode_access_token_expired(self):
        """Test decoding expired token returns None"""
        token = self.auth_service.create_access_token(
            data={"sub": "testuser"},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        payload = self.auth_service.decode_access_token(token)
        assert payload is None

    def test_decode_access_token_invalid(self):
        """Test decoding invalid token returns None"""
        payload = self.auth_service.decode_access_token("invalid.token.here")
        assert payload is None

    def test_get_current_user_success(self):
        """Test get_current_user with valid token"""
        self.auth_service.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        token = self.auth_service.create_access_token(data={"sub": "testuser"})
        user = self.auth_service.get_current_user(token)
        assert user is not None
        assert user.username == "testuser"

    def test_get_current_user_invalid_token(self):
        """Test get_current_user with invalid token"""
        user = self.auth_service.get_current_user("invalid.token")
        assert user is None

    def test_get_current_user_no_sub(self):
        """Test get_current_user with token missing sub claim"""
        token = self.auth_service.create_access_token(data={})  # No "sub"
        user = self.auth_service.get_current_user(token)
        assert user is None

    def test_get_current_user_nonexistent_user(self):
        """Test get_current_user for nonexistent user"""
        token = self.auth_service.create_access_token(data={"sub": "nonexistent"})
        user = self.auth_service.get_current_user(token)
        assert user is None

    def test_get_current_user_inactive_user(self):
        """Test get_current_user for inactive user"""
        user = self.auth_service.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        user.deactivate()
        token = self.auth_service.create_access_token(data={"sub": "testuser"})
        result = self.auth_service.get_current_user(token)
        assert result is None


class TestReservationService:
    """Tests for ReservationService"""

    def setup_method(self):
        """Setup fresh repository for each test"""
        self.repo = InMemoryReservationRepository()
        self.service = ReservationService(self.repo)

    def test_create_reservation(self):
        """Test creating a reservation"""
        start = datetime.utcnow() + timedelta(hours=1)
        end = start + timedelta(hours=2)
        
        reservation = self.service.create_reservation(
            customer_id="cust-1",
            workstation_id="ws-1",
            start=start,
            end=end,
            package_name="Basic",
            package_duration_minutes=120,
            package_price_amount=20000,
        )
        
        assert reservation is not None
        assert reservation.customer_id == "cust-1"
        assert reservation.package.name == "Basic"
        # Should be confirmed after creation
        assert reservation.status.value == "CONFIRMED"

    def test_list_reservations_empty(self):
        """Test listing reservations when empty"""
        reservations = self.service.list_reservations()
        assert reservations == []

    def test_list_reservations(self):
        """Test listing reservations"""
        start = datetime.utcnow() + timedelta(hours=1)
        end = start + timedelta(hours=2)
        
        self.service.create_reservation(
            customer_id="cust-1",
            workstation_id="ws-1",
            start=start,
            end=end,
            package_name="Basic",
            package_duration_minutes=120,
            package_price_amount=20000,
        )
        
        reservations = self.service.list_reservations()
        assert len(reservations) == 1

    def test_check_in(self):
        """Test checking in to a reservation"""
        start = datetime.utcnow() + timedelta(hours=1)
        end = start + timedelta(hours=2)
        
        reservation = self.service.create_reservation(
            customer_id="cust-1",
            workstation_id="ws-1",
            start=start,
            end=end,
            package_name="Basic",
            package_duration_minutes=120,
            package_price_amount=20000,
        )
        
        checked_in = self.service.check_in(reservation.id)
        assert checked_in.status.value == "CHECKED_IN"

    def test_check_in_nonexistent_raises(self):
        """Test check_in for nonexistent reservation raises error"""
        with pytest.raises(KeyError):
            self.service.check_in("nonexistent-id")


class TestBillingService:
    """Tests for BillingService"""

    def setup_method(self):
        """Setup fresh repository for each test"""
        self.repo = InMemorySessionRepository()
        self.service = BillingService(self.repo)

    def test_start_session(self):
        """Test starting a session"""
        session = self.service.start_session(
            customer_id="cust-1",
            workstation_id="ws-1",
            reservation_id="res-1",
        )
        
        assert session is not None
        assert session.customer_id == "cust-1"
        assert session.status.value == "ACTIVE"

    def test_start_session_without_reservation(self):
        """Test starting a session without reservation"""
        session = self.service.start_session(
            customer_id="cust-1",
            workstation_id="ws-1",
        )
        assert session.reservation_id is None

    def test_finish_and_bill(self):
        """Test finishing session and generating bill"""
        session = self.service.start_session(
            customer_id="cust-1",
            workstation_id="ws-1",
        )
        
        finished = self.service.finish_and_bill(
            session_id=session.id,
            tariff_name="Standard",
            rate_per_minute=100,
        )
        
        assert finished.status.value == "FINISHED"
        assert finished.bill is not None
        assert finished.bill.status.value == "FINAL"

    def test_finish_and_bill_nonexistent_raises(self):
        """Test finish_and_bill for nonexistent session raises error"""
        with pytest.raises(KeyError):
            self.service.finish_and_bill(
                session_id="nonexistent-id",
                tariff_name="Standard",
                rate_per_minute=100,
            )

    def test_list_sessions_empty(self):
        """Test listing sessions when empty"""
        sessions = self.service.list_sessions()
        assert sessions == []

    def test_list_sessions(self):
        """Test listing sessions"""
        self.service.start_session(
            customer_id="cust-1",
            workstation_id="ws-1",
        )
        sessions = self.service.list_sessions()
        assert len(sessions) == 1


class TestPaymentService:
    """Tests for PaymentService"""

    def setup_method(self):
        """Setup fresh repository for each test"""
        self.repo = InMemoryInvoiceRepository()
        self.service = PaymentService(self.repo)

    def test_create_invoice(self):
        """Test creating an invoice"""
        invoice = self.service.create_invoice(
            bill_id="bill-1",
            customer_id="cust-1",
            amount_due=10000,
            phone="08123456789",
            email="test@example.com",
        )
        
        assert invoice is not None
        assert invoice.bill_id == "bill-1"
        assert invoice.amount_due.amount == 10000
        assert invoice.status.value == "UNPAID"

    def test_create_invoice_without_contact(self):
        """Test creating invoice without phone/email"""
        invoice = self.service.create_invoice(
            bill_id="bill-1",
            customer_id="cust-1",
            amount_due=10000,
            phone=None,
            email=None,
        )
        assert invoice is not None

    def test_pay_invoice(self):
        """Test paying an invoice"""
        invoice = self.service.create_invoice(
            bill_id="bill-1",
            customer_id="cust-1",
            amount_due=10000,
            phone=None,
            email=None,
        )
        
        paid = self.service.pay_invoice(
            invoice_id=invoice.id,
            method="CASH",
        )
        
        assert paid.status.value == "SETTLED"
        assert paid.payment is not None
        assert paid.payment.status.value == "SETTLED"

    def test_pay_invoice_nonexistent_raises(self):
        """Test pay_invoice for nonexistent invoice raises error"""
        with pytest.raises(KeyError):
            self.service.pay_invoice(
                invoice_id="nonexistent-id",
                method="CASH",
            )

    def test_list_invoices_empty(self):
        """Test listing invoices when empty"""
        invoices = self.service.list_invoices()
        assert invoices == []

    def test_list_invoices(self):
        """Test listing invoices"""
        self.service.create_invoice(
            bill_id="bill-1",
            customer_id="cust-1",
            amount_due=10000,
            phone=None,
            email=None,
        )
        invoices = self.service.list_invoices()
        assert len(invoices) == 1

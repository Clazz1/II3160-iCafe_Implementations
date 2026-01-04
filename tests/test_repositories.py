"""Tests for repository layer"""
from __future__ import annotations

import pytest

from app.infrastructure.repositories.base import AbstractInMemoryRepository
from app.infrastructure.repositories.user_inmemory import InMemoryUserRepository
from app.infrastructure.repositories.reservation_inmemory import InMemoryReservationRepository
from app.infrastructure.repositories.session_inmemory import InMemorySessionRepository
from app.infrastructure.repositories.invoice_inmemory import InMemoryInvoiceRepository

from app.domain.user_aggregate import User
from app.domain.reservation_aggregate import Reservation, Package
from app.domain.billing_aggregate import Session
from app.domain.payment_aggregate import Invoice
from app.domain.value_objects import (
    UserRole, UserStatus, TimeSlot, Money, Contact,
)
from datetime import datetime, timedelta


class TestAbstractInMemoryRepository:
    """Tests for AbstractInMemoryRepository base class"""

    def test_add_and_get(self):
        """Test adding and retrieving entity"""
        repo = InMemoryUserRepository()
        user = User(
            id="user-1",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
            role=UserRole.CUSTOMER,
            status=UserStatus.ACTIVE,
        )
        repo.add(user)
        retrieved = repo.get("user-1")
        assert retrieved == user

    def test_get_nonexistent(self):
        """Test getting nonexistent entity returns None"""
        repo = InMemoryUserRepository()
        retrieved = repo.get("nonexistent")
        assert retrieved is None

    def test_list_empty(self):
        """Test listing empty repository"""
        repo = InMemoryUserRepository()
        items = repo.list()
        assert items == []

    def test_list(self):
        """Test listing entities"""
        repo = InMemoryUserRepository()
        user1 = User(
            id="user-1",
            username="testuser1",
            email="test1@example.com",
            hashed_password="hashed",
            role=UserRole.CUSTOMER,
            status=UserStatus.ACTIVE,
        )
        user2 = User(
            id="user-2",
            username="testuser2",
            email="test2@example.com",
            hashed_password="hashed",
            role=UserRole.CUSTOMER,
            status=UserStatus.ACTIVE,
        )
        repo.add(user1)
        repo.add(user2)
        items = repo.list()
        assert len(items) == 2

    def test_update(self):
        """Test updating entity"""
        repo = InMemoryUserRepository()
        user = User(
            id="user-1",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
            role=UserRole.CUSTOMER,
            status=UserStatus.ACTIVE,
        )
        repo.add(user)
        user.suspend()
        repo.update(user)
        retrieved = repo.get("user-1")
        assert retrieved.status == UserStatus.SUSPENDED

    def test_update_nonexistent_raises(self):
        """Test updating nonexistent entity raises KeyError"""
        repo = InMemoryUserRepository()
        user = User(
            id="user-1",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
            role=UserRole.CUSTOMER,
            status=UserStatus.ACTIVE,
        )
        with pytest.raises(KeyError):
            repo.update(user)


class TestInMemoryUserRepository:
    """Tests for InMemoryUserRepository"""

    def setup_method(self):
        """Setup fresh repository for each test"""
        self.repo = InMemoryUserRepository()

    def test_get_by_username(self):
        """Test get_by_username"""
        user = User(
            id="user-1",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
            role=UserRole.CUSTOMER,
            status=UserStatus.ACTIVE,
        )
        self.repo.add(user)
        retrieved = self.repo.get_by_username("testuser")
        assert retrieved == user

    def test_get_by_username_nonexistent(self):
        """Test get_by_username returns None for nonexistent"""
        retrieved = self.repo.get_by_username("nonexistent")
        assert retrieved is None

    def test_get_by_email(self):
        """Test get_by_email"""
        user = User(
            id="user-1",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
            role=UserRole.CUSTOMER,
            status=UserStatus.ACTIVE,
        )
        self.repo.add(user)
        retrieved = self.repo.get_by_email("test@example.com")
        assert retrieved == user

    def test_get_by_email_nonexistent(self):
        """Test get_by_email returns None for nonexistent"""
        retrieved = self.repo.get_by_email("nonexistent@example.com")
        assert retrieved is None

    def test_username_exists(self):
        """Test username_exists returns True when exists"""
        user = User(
            id="user-1",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
            role=UserRole.CUSTOMER,
            status=UserStatus.ACTIVE,
        )
        self.repo.add(user)
        assert self.repo.username_exists("testuser") is True

    def test_username_not_exists(self):
        """Test username_exists returns False when not exists"""
        assert self.repo.username_exists("nonexistent") is False

    def test_email_exists(self):
        """Test email_exists returns True when exists"""
        user = User(
            id="user-1",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
            role=UserRole.CUSTOMER,
            status=UserStatus.ACTIVE,
        )
        self.repo.add(user)
        assert self.repo.email_exists("test@example.com") is True

    def test_email_not_exists(self):
        """Test email_exists returns False when not exists"""
        assert self.repo.email_exists("nonexistent@example.com") is False


class TestInMemoryReservationRepository:
    """Tests for InMemoryReservationRepository"""

    def setup_method(self):
        """Setup fresh repository for each test"""
        self.repo = InMemoryReservationRepository()

    def test_add_and_get_reservation(self):
        """Test adding and getting reservation"""
        start = datetime.utcnow()
        end = start + timedelta(hours=2)
        
        reservation = Reservation(
            id="res-1",
            customer_id="cust-1",
            workstation_id="ws-1",
            time_slot=TimeSlot(start=start, end=end),
            package=Package(
                id="pkg-1",
                name="Basic",
                description=None,
                duration_minutes=120,
                base_price_amount=20000,
            ),
        )
        self.repo.add(reservation)
        retrieved = self.repo.get("res-1")
        assert retrieved == reservation


class TestInMemorySessionRepository:
    """Tests for InMemorySessionRepository"""

    def setup_method(self):
        """Setup fresh repository for each test"""
        self.repo = InMemorySessionRepository()

    def test_add_and_get_session(self):
        """Test adding and getting session"""
        session = Session(
            id="session-1",
            reservation_id="res-1",
            customer_id="cust-1",
            workstation_id="ws-1",
        )
        self.repo.add(session)
        retrieved = self.repo.get("session-1")
        assert retrieved == session


class TestInMemoryInvoiceRepository:
    """Tests for InMemoryInvoiceRepository"""

    def setup_method(self):
        """Setup fresh repository for each test"""
        self.repo = InMemoryInvoiceRepository()

    def test_add_and_get_invoice(self):
        """Test adding and getting invoice"""
        invoice = Invoice(
            id="inv-1",
            bill_id="bill-1",
            customer_id="cust-1",
            amount_due=Money(amount=10000),
            contact=Contact(phone="08123456789"),
        )
        self.repo.add(invoice)
        retrieved = self.repo.get("inv-1")
        assert retrieved == invoice

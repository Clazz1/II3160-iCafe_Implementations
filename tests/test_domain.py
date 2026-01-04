"""Tests for domain layer - aggregates and value objects"""
from __future__ import annotations

import pytest
from datetime import datetime, timedelta

from app.domain.value_objects import (
    TimeSlot, Money, Contact, 
    ReservationStatus, QueueStatus, SessionStatus, 
    BillStatus, InvoiceStatus, PaymentStatus,
    UserRole, UserStatus
)
from app.domain.user_aggregate import User
from app.domain.reservation_aggregate import Reservation, Package, QueueTicket
from app.domain.billing_aggregate import Session, Bill, TariffPlan
from app.domain.payment_aggregate import Invoice, Payment
from app.domain.exceptions import InvalidStateTransition, DomainError


class TestValueObjects:
    """Tests for value objects"""

    def test_timeslot_valid(self):
        """Test valid TimeSlot creation"""
        start = datetime.utcnow()
        end = start + timedelta(hours=2)
        slot = TimeSlot(start=start, end=end)
        assert slot.start == start
        assert slot.end == end
        assert slot.duration_minutes == 120

    def test_timeslot_invalid_end_before_start(self):
        """Test TimeSlot raises error when end <= start"""
        start = datetime.utcnow()
        end = start - timedelta(hours=1)
        with pytest.raises(ValueError, match="end must be greater than start"):
            TimeSlot(start=start, end=end)

    def test_timeslot_invalid_same_time(self):
        """Test TimeSlot raises error when end == start"""
        now = datetime.utcnow()
        with pytest.raises(ValueError):
            TimeSlot(start=now, end=now)

    def test_money_valid(self):
        """Test valid Money creation"""
        money = Money(amount=10000, currency="IDR")
        assert money.amount == 10000
        assert money.currency == "IDR"

    def test_money_default_currency(self):
        """Test Money default currency is IDR"""
        money = Money(amount=5000)
        assert money.currency == "IDR"

    def test_money_negative_amount_raises(self):
        """Test Money with negative amount raises error"""
        with pytest.raises(ValueError, match="cannot be negative"):
            Money(amount=-100)

    def test_money_add(self):
        """Test Money addition"""
        m1 = Money(amount=1000)
        m2 = Money(amount=500)
        result = m1.add(m2)
        assert result.amount == 1500

    def test_money_add_currency_mismatch(self):
        """Test Money addition with different currencies raises error"""
        m1 = Money(amount=1000, currency="IDR")
        m2 = Money(amount=500, currency="USD")
        with pytest.raises(ValueError, match="Currency mismatch"):
            m1.add(m2)

    def test_money_subtract(self):
        """Test Money subtraction"""
        m1 = Money(amount=1000)
        m2 = Money(amount=300)
        result = m1.subtract(m2)
        assert result.amount == 700

    def test_money_subtract_currency_mismatch(self):
        """Test Money subtraction with different currencies raises error"""
        m1 = Money(amount=1000, currency="IDR")
        m2 = Money(amount=500, currency="USD")
        with pytest.raises(ValueError, match="Currency mismatch"):
            m1.subtract(m2)

    def test_money_subtract_negative_result_raises(self):
        """Test Money subtraction resulting in negative raises error"""
        m1 = Money(amount=100)
        m2 = Money(amount=500)
        with pytest.raises(ValueError, match="negative"):
            m1.subtract(m2)

    def test_contact_creation(self):
        """Test Contact creation"""
        contact = Contact(phone="08123456789")
        assert contact.phone == "08123456789"
        assert contact.email is None


class TestUserAggregate:
    """Tests for User aggregate"""

    def create_user(self, **kwargs) -> User:
        defaults = {
            "id": "user-1",
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": "hashed123",
            "role": UserRole.CUSTOMER,
            "status": UserStatus.ACTIVE,
        }
        defaults.update(kwargs)
        return User(**defaults)

    def test_user_creation(self):
        """Test User creation with valid data"""
        user = self.create_user()
        assert user.id == "user-1"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == UserRole.CUSTOMER
        assert user.status == UserStatus.ACTIVE

    def test_user_is_active(self):
        """Test is_active returns True for ACTIVE status"""
        user = self.create_user(status=UserStatus.ACTIVE)
        assert user.is_active() is True

    def test_user_is_not_active_when_suspended(self):
        """Test is_active returns False for SUSPENDED status"""
        user = self.create_user(status=UserStatus.SUSPENDED)
        assert user.is_active() is False

    def test_user_is_not_active_when_inactive(self):
        """Test is_active returns False for INACTIVE status"""
        user = self.create_user(status=UserStatus.INACTIVE)
        assert user.is_active() is False

    def test_user_is_admin(self):
        """Test is_admin returns True for ADMIN role"""
        user = self.create_user(role=UserRole.ADMIN)
        assert user.is_admin() is True

    def test_user_is_not_admin(self):
        """Test is_admin returns False for CUSTOMER role"""
        user = self.create_user(role=UserRole.CUSTOMER)
        assert user.is_admin() is False

    def test_user_activate(self):
        """Test activate method changes status to ACTIVE"""
        user = self.create_user(status=UserStatus.SUSPENDED)
        user.activate()
        assert user.status == UserStatus.ACTIVE

    def test_user_suspend(self):
        """Test suspend method changes status to SUSPENDED"""
        user = self.create_user(status=UserStatus.ACTIVE)
        user.suspend()
        assert user.status == UserStatus.SUSPENDED

    def test_user_deactivate(self):
        """Test deactivate method changes status to INACTIVE"""
        user = self.create_user(status=UserStatus.ACTIVE)
        user.deactivate()
        assert user.status == UserStatus.INACTIVE

    def test_user_update_contact(self):
        """Test update_contact method"""
        user = self.create_user()
        contact = Contact(phone="08123456789")
        user.update_contact(contact)
        assert user.contact == contact


class TestQueueTicket:
    """Tests for QueueTicket"""

    def test_queue_ticket_creation(self):
        """Test QueueTicket creation"""
        ticket = QueueTicket(id="ticket-1", number=1)
        assert ticket.id == "ticket-1"
        assert ticket.number == 1
        assert ticket.status == QueueStatus.WAITING

    def test_queue_ticket_mark_called(self):
        """Test mark_called transitions from WAITING to CALLED"""
        ticket = QueueTicket(id="ticket-1", number=1)
        ticket.mark_called()
        assert ticket.status == QueueStatus.CALLED

    def test_queue_ticket_mark_called_from_non_waiting_raises(self):
        """Test mark_called from non-WAITING status raises error"""
        ticket = QueueTicket(id="ticket-1", number=1, status=QueueStatus.CALLED)
        with pytest.raises(InvalidStateTransition):
            ticket.mark_called()

    def test_queue_ticket_cancel(self):
        """Test cancel method"""
        ticket = QueueTicket(id="ticket-1", number=1)
        ticket.cancel()
        assert ticket.status == QueueStatus.CANCELLED

    def test_queue_ticket_cancel_already_cancelled(self):
        """Test cancel on already cancelled ticket is idempotent"""
        ticket = QueueTicket(id="ticket-1", number=1, status=QueueStatus.CANCELLED)
        ticket.cancel()  # Should not raise
        assert ticket.status == QueueStatus.CANCELLED


class TestReservationAggregate:
    """Tests for Reservation aggregate"""

    def create_reservation(self, **kwargs) -> Reservation:
        start = datetime.utcnow()
        end = start + timedelta(hours=2)
        defaults = {
            "id": "res-1",
            "customer_id": "cust-1",
            "workstation_id": "ws-1",
            "time_slot": TimeSlot(start=start, end=end),
            "package": Package(
                id="pkg-1",
                name="Basic",
                description="Basic package",
                duration_minutes=120,
                base_price_amount=20000,
            ),
        }
        defaults.update(kwargs)
        return Reservation(**defaults)

    def test_reservation_creation(self):
        """Test Reservation creation"""
        res = self.create_reservation()
        assert res.id == "res-1"
        assert res.status == ReservationStatus.PENDING

    def test_reservation_confirm(self):
        """Test confirm transitions from PENDING to CONFIRMED"""
        res = self.create_reservation()
        res.confirm()
        assert res.status == ReservationStatus.CONFIRMED

    def test_reservation_confirm_from_non_pending_raises(self):
        """Test confirm from non-PENDING status raises error"""
        res = self.create_reservation()
        res.confirm()
        with pytest.raises(InvalidStateTransition):
            res.confirm()

    def test_reservation_check_in(self):
        """Test check_in transitions from CONFIRMED to CHECKED_IN"""
        res = self.create_reservation()
        res.confirm()
        res.check_in()
        assert res.status == ReservationStatus.CHECKED_IN
        assert res.checked_in_at is not None

    def test_reservation_check_in_from_non_confirmed_raises(self):
        """Test check_in from non-CONFIRMED status raises error"""
        res = self.create_reservation()
        with pytest.raises(InvalidStateTransition):
            res.check_in()

    def test_reservation_complete(self):
        """Test complete transitions from CHECKED_IN to COMPLETED"""
        res = self.create_reservation()
        res.confirm()
        res.check_in()
        res.complete()
        assert res.status == ReservationStatus.COMPLETED
        assert res.completed_at is not None

    def test_reservation_complete_from_non_checked_in_raises(self):
        """Test complete from non-CHECKED_IN status raises error"""
        res = self.create_reservation()
        res.confirm()
        with pytest.raises(InvalidStateTransition):
            res.complete()

    def test_reservation_cancel(self):
        """Test cancel method"""
        res = self.create_reservation()
        res.cancel()
        assert res.status == ReservationStatus.CANCELLED
        assert res.cancelled_at is not None

    def test_reservation_cancel_completed_raises(self):
        """Test cancel on COMPLETED reservation raises error"""
        res = self.create_reservation()
        res.confirm()
        res.check_in()
        res.complete()
        with pytest.raises(InvalidStateTransition):
            res.cancel()

    def test_reservation_cancel_with_queue_ticket(self):
        """Test cancel also cancels queue ticket"""
        res = self.create_reservation()
        ticket = QueueTicket(id="ticket-1", number=1)
        res.attach_queue_ticket(ticket)
        res.cancel()
        assert res.queue_ticket.status == QueueStatus.CANCELLED

    def test_reservation_mark_no_show(self):
        """Test mark_no_show from CONFIRMED"""
        res = self.create_reservation()
        res.confirm()
        res.mark_no_show()
        assert res.status == ReservationStatus.NO_SHOW
        assert res.no_show_at is not None

    def test_reservation_mark_no_show_from_pending(self):
        """Test mark_no_show from PENDING"""
        res = self.create_reservation()
        res.mark_no_show()
        assert res.status == ReservationStatus.NO_SHOW

    def test_reservation_mark_no_show_from_invalid_status_raises(self):
        """Test mark_no_show from invalid status raises error"""
        res = self.create_reservation()
        res.confirm()
        res.check_in()
        with pytest.raises(InvalidStateTransition):
            res.mark_no_show()

    def test_reservation_attach_queue_ticket(self):
        """Test attach_queue_ticket"""
        res = self.create_reservation()
        ticket = QueueTicket(id="ticket-1", number=1)
        res.attach_queue_ticket(ticket)
        assert res.queue_ticket == ticket


class TestBillingAggregate:
    """Tests for Session and Bill aggregates"""

    def create_session(self, **kwargs) -> Session:
        defaults = {
            "id": "session-1",
            "reservation_id": "res-1",
            "customer_id": "cust-1",
            "workstation_id": "ws-1",
        }
        defaults.update(kwargs)
        return Session(**defaults)

    def test_session_creation(self):
        """Test Session creation"""
        session = self.create_session()
        assert session.id == "session-1"
        assert session.status == SessionStatus.ACTIVE

    def test_session_finish(self):
        """Test finish transitions from ACTIVE to FINISHED"""
        session = self.create_session()
        session.finish()
        assert session.status == SessionStatus.FINISHED
        assert session.ended_at is not None

    def test_session_finish_from_non_active_raises(self):
        """Test finish from non-ACTIVE status raises error"""
        session = self.create_session()
        session.finish()
        with pytest.raises(InvalidStateTransition):
            session.finish()

    def test_session_duration_minutes(self):
        """Test duration_minutes calculation"""
        session = self.create_session()
        # Duration is calculated from now if not finished
        duration = session.duration_minutes
        assert duration >= 0

    def test_session_generate_bill(self):
        """Test generate_bill creates Bill"""
        session = self.create_session()
        session.finish()
        
        tariff = TariffPlan(
            id="tariff-1",
            name="Standard",
            rate_per_minute=Money(amount=100),
            overtime_rate_per_minute=Money(amount=150),
        )
        
        bill = session.generate_bill(tariff=tariff, bill_id="bill-1")
        assert bill is not None
        assert bill.id == "bill-1"
        assert session.bill == bill
        assert bill.status == BillStatus.FINAL

    def test_bill_finalize_idempotent(self):
        """Test Bill.finalize is idempotent"""
        bill = Bill(
            id="bill-1",
            session_id="session-1",
            subtotal=Money(amount=1000),
            discount=Money(amount=0),
            total=Money(amount=1000),
            status=BillStatus.FINAL,
        )
        bill.finalize()  # Should not raise
        assert bill.status == BillStatus.FINAL


class TestPaymentAggregate:
    """Tests for Invoice and Payment aggregates"""

    def create_invoice(self, **kwargs) -> Invoice:
        defaults = {
            "id": "inv-1",
            "bill_id": "bill-1",
            "customer_id": "cust-1",
            "amount_due": Money(amount=10000),
            "contact": Contact(phone="08123456789"),
        }
        defaults.update(kwargs)
        return Invoice(**defaults)

    def create_payment(self, **kwargs) -> Payment:
        defaults = {
            "id": "pay-1",
            "invoice_id": "inv-1",
            "amount": Money(amount=10000),
            "method": "CASH",
        }
        defaults.update(kwargs)
        return Payment(**defaults)

    def test_invoice_creation(self):
        """Test Invoice creation"""
        invoice = self.create_invoice()
        assert invoice.id == "inv-1"
        assert invoice.status == InvoiceStatus.UNPAID

    def test_payment_creation(self):
        """Test Payment creation"""
        payment = self.create_payment()
        assert payment.id == "pay-1"
        assert payment.status == PaymentStatus.PENDING

    def test_payment_mark_settled(self):
        """Test mark_settled transitions to SETTLED"""
        payment = self.create_payment()
        payment.mark_settled()
        assert payment.status == PaymentStatus.SETTLED
        assert payment.completed_at is not None

    def test_payment_mark_settled_idempotent(self):
        """Test mark_settled is idempotent"""
        payment = self.create_payment(status=PaymentStatus.SETTLED)
        payment.mark_settled()
        assert payment.status == PaymentStatus.SETTLED

    def test_payment_mark_failed(self):
        """Test mark_failed transitions to FAILED"""
        payment = self.create_payment()
        payment.mark_failed()
        assert payment.status == PaymentStatus.FAILED
        assert payment.completed_at is not None

    def test_payment_mark_failed_idempotent(self):
        """Test mark_failed is idempotent"""
        payment = self.create_payment(status=PaymentStatus.FAILED)
        payment.mark_failed()
        assert payment.status == PaymentStatus.FAILED

    def test_invoice_register_payment(self):
        """Test register_payment on Invoice"""
        invoice = self.create_invoice()
        payment = self.create_payment()
        invoice.register_payment(payment)
        assert invoice.payment == payment

    def test_invoice_register_payment_duplicate_raises(self):
        """Test register_payment twice raises error"""
        invoice = self.create_invoice()
        payment1 = self.create_payment()
        payment2 = self.create_payment(id="pay-2")
        invoice.register_payment(payment1)
        with pytest.raises(InvalidStateTransition, match="sudah punya Payment"):
            invoice.register_payment(payment2)

    def test_invoice_register_payment_wrong_amount_raises(self):
        """Test register_payment with wrong amount raises error"""
        invoice = self.create_invoice(amount_due=Money(amount=10000))
        payment = self.create_payment(amount=Money(amount=5000))
        with pytest.raises(InvalidStateTransition, match="tidak sesuai"):
            invoice.register_payment(payment)

    def test_invoice_mark_settled(self):
        """Test mark_settled on Invoice"""
        invoice = self.create_invoice()
        invoice.mark_settled()
        assert invoice.status == InvoiceStatus.SETTLED
        assert invoice.paid_at is not None

    def test_invoice_mark_settled_idempotent(self):
        """Test mark_settled is idempotent"""
        invoice = self.create_invoice()
        invoice.mark_settled()
        invoice.mark_settled()
        assert invoice.status == InvoiceStatus.SETTLED

    def test_invoice_mark_failed(self):
        """Test mark_failed on Invoice"""
        invoice = self.create_invoice()
        invoice.mark_failed()
        assert invoice.status == InvoiceStatus.FAILED

    def test_invoice_mark_failed_idempotent(self):
        """Test mark_failed is idempotent"""
        invoice = self.create_invoice()
        invoice.mark_failed()
        invoice.mark_failed()
        assert invoice.status == InvoiceStatus.FAILED


class TestExceptions:
    """Tests for domain exceptions"""

    def test_domain_error(self):
        """Test DomainError can be raised"""
        with pytest.raises(DomainError):
            raise DomainError("Test error")

    def test_invalid_state_transition(self):
        """Test InvalidStateTransition is a DomainError"""
        with pytest.raises(DomainError):
            raise InvalidStateTransition("Invalid transition")

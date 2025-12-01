from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class QueueStatus(str, Enum):
    WAITING = "WAITING"
    CALLED = "CALLED"
    CANCELLED = "CANCELLED"


class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"
    TIMEOUT = "TIMEOUT"
    ABORTED = "ABORTED"


class BillStatus(str, Enum):
    DRAFT = "DRAFT"
    FINAL = "FINAL"


class InvoiceStatus(str, Enum):
    UNPAID = "UNPAID"
    SETTLED = "SETTLED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SETTLED = "SETTLED"
    FAILED = "FAILED"


class UserRole(str, Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


# ===== VALUE OBJECTS =====

@dataclass(frozen=True)
class TimeSlot:
    start: datetime
    end: datetime

    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError("TimeSlot.end must be greater than start")

    @property
    def duration_minutes(self) -> int:
        return int((self.end - self.start).total_seconds() // 60)


@dataclass(frozen=True)
class Money:
    amount: int  # misal rupiah
    currency: str = "IDR"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def subtract(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        if other.amount > self.amount:
            raise ValueError("Resulting amount would be negative")
        return Money(amount=self.amount - other.amount, currency=self.currency)


@dataclass(frozen=True)
class Contact:
    phone: Optional[str] = None
    email: Optional[str] = None

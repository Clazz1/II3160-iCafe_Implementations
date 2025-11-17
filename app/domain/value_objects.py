from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class WorkstationType(str, Enum):
    PC = "PC"
    ROOM = "ROOM"
    VIP = "VIP"


class WorkstationStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    RESERVED = "RESERVED"
    OFFLINE = "OFFLINE"
    BROKEN = "BROKEN"


class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"


class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"
    ABORTED = "ABORTED"


class PaymentStatus(str, Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"
    REFUNDED = "REFUNDED"
    FAILED = "FAILED"


class QueueStatus(str, Enum):
    WAITING = "WAITING"
    CALLED = "CALLED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class TimeSlot:
    start: datetime
    end: datetime

    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError("end must be greater than start")

    @property
    def duration_minutes(self) -> int:
        return int((self.end - self.start).total_seconds() // 60)


@dataclass(frozen=True)
class Duration:
    minutes: int

    def __post_init__(self):
        if self.minutes <= 0:
            raise ValueError("Duration must be positive")

    @classmethod
    def from_timedelta(cls, delta: timedelta) -> "Duration":
        minutes = int(delta.total_seconds() // 60)
        return cls(minutes=minutes)


@dataclass(frozen=True)
class Money:
    amount: int  # misal dalam rupiah
    currency: str = "IDR"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

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
class PackageSelection:
    package_code: str
    name: str
    base_duration: Duration
    base_price: Money
    benefits: Optional[str] = None


@dataclass(frozen=True)
class BillingDetail:
    base_price: Money
    extra_duration: Duration
    extra_charge: Money
    discount: Money
    total: Money


@dataclass(frozen=True)
class RequestedResource:
    type: WorkstationType
    count: int = 1
    preferences: Optional[str] = None

    def __post_init__(self):
        if self.count <= 0:
            raise ValueError("Resource count must be positive")

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .exceptions import InvalidStateTransition
from .value_objects import TimeSlot, ReservationStatus, QueueStatus


@dataclass
class Package:
    id: str
    name: str
    description: Optional[str]
    duration_minutes: int
    base_price_amount: int  # simplifikasi, bisa dihubungkan ke Money/ TariffPlan


@dataclass
class QueueTicket:
    id: str
    number: int
    status: QueueStatus = QueueStatus.WAITING
    created_at: datetime = field(default_factory=datetime.utcnow)

    def mark_called(self):
        if self.status is not QueueStatus.WAITING:
            raise InvalidStateTransition("Hanya ticket WAITING yang bisa dipanggil")
        self.status = QueueStatus.CALLED

    def cancel(self):
        if self.status is QueueStatus.CANCELLED:
            return
        self.status = QueueStatus.CANCELLED


@dataclass
class Reservation:
    id: str
    customer_id: str
    workstation_id: Optional[str]
    time_slot: TimeSlot
    package: Package

    status: ReservationStatus = ReservationStatus.PENDING
    queue_ticket: Optional[QueueTicket] = None

    created_at: datetime = field(default_factory=datetime.utcnow)
    checked_in_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    no_show_at: Optional[datetime] = None

    def confirm(self):
        if self.status is not ReservationStatus.PENDING:
            raise InvalidStateTransition(f"Tidak bisa CONFIRM dari {self.status}")
        self.status = ReservationStatus.CONFIRMED

    def attach_queue_ticket(self, ticket: QueueTicket):
        self.queue_ticket = ticket

    def check_in(self, now: Optional[datetime] = None):
        if self.status is not ReservationStatus.CONFIRMED:
            raise InvalidStateTransition(f"Tidak bisa CHECK_IN dari {self.status}")
        self.status = ReservationStatus.CHECKED_IN
        self.checked_in_at = now or datetime.utcnow()

    def complete(self, now: Optional[datetime] = None):
        if self.status is not ReservationStatus.CHECKED_IN:
            raise InvalidStateTransition(f"Tidak bisa COMPLETE dari {self.status}")
        self.status = ReservationStatus.COMPLETED
        self.completed_at = now or datetime.utcnow()

    def cancel(self, now: Optional[datetime] = None):
        if self.status in {ReservationStatus.COMPLETED, ReservationStatus.CANCELLED}:
            raise InvalidStateTransition("Reservasi sudah selesai/ batal")
        self.status = ReservationStatus.CANCELLED
        self.cancelled_at = now or datetime.utcnow()
        if self.queue_ticket:
            self.queue_ticket.cancel()

    def mark_no_show(self, now: Optional[datetime] = None):
        if self.status not in {ReservationStatus.CONFIRMED, ReservationStatus.PENDING}:
            raise InvalidStateTransition("NO_SHOW hanya untuk reservasi aktif")
        self.status = ReservationStatus.NO_SHOW
        self.no_show_at = now or datetime.utcnow()
        if self.queue_ticket:
            self.queue_ticket.cancel()

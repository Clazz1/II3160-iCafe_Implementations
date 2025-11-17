from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .exceptions import InvalidStateTransition
from .value_objects import Money, SessionStatus, BillStatus


@dataclass
class TariffPlan:
    id: str
    name: str
    rate_per_minute: Money        # harga per menit
    overtime_rate_per_minute: Money  # bisa beda tarif lembur
    description: Optional[str] = None


@dataclass
class Bill:
    id: str
    session_id: str
    subtotal: Money
    discount: Money
    total: Money
    status: BillStatus = BillStatus.DRAFT

    def finalize(self):
        if self.status is BillStatus.FINAL:
            return
        self.status = BillStatus.FINAL


@dataclass
class Session:
    id: str
    reservation_id: Optional[str]
    customer_id: str
    workstation_id: str

    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    status: SessionStatus = SessionStatus.ACTIVE

    bill: Optional[Bill] = None

    def finish(self, end_time: Optional[datetime] = None):
        if self.status is not SessionStatus.ACTIVE:
            raise InvalidStateTransition(f"Tidak bisa FINISH dari {self.status}")
        self.ended_at = end_time or datetime.utcnow()
        self.status = SessionStatus.FINISHED

    @property
    def duration_minutes(self) -> int:
        end = self.ended_at or datetime.utcnow()
        return int((end - self.started_at).total_seconds() // 60)

    def generate_bill(self, tariff: TariffPlan, bill_id: str) -> Bill:
        minutes = self.duration_minutes
        subtotal_amount = tariff.rate_per_minute.amount * minutes
        subtotal = Money(amount=subtotal_amount, currency=tariff.rate_per_minute.currency)
        discount = Money(amount=0, currency=subtotal.currency)
        total = subtotal

        bill = Bill(
            id=bill_id,
            session_id=self.id,
            subtotal=subtotal,
            discount=discount,
            total=total,
        )
        bill.finalize()
        self.bill = bill
        return bill

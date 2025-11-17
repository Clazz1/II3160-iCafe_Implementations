from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .exceptions import InvalidStateTransition
from .value_objects import Money, InvoiceStatus, PaymentStatus, Contact


@dataclass
class Payment:
    id: str
    invoice_id: str
    amount: Money
    method: str  # QRIS / E_WALLET / CARD / CASH
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def mark_settled(self, now: Optional[datetime] = None):
        if self.status is PaymentStatus.SETTLED:
            return
        self.status = PaymentStatus.SETTLED
        self.completed_at = now or datetime.utcnow()

    def mark_failed(self, now: Optional[datetime] = None):
        if self.status is PaymentStatus.FAILED:
            return
        self.status = PaymentStatus.FAILED
        self.completed_at = now or datetime.utcnow()


@dataclass
class Invoice:
    id: str
    bill_id: str
    customer_id: str
    amount_due: Money
    contact: Contact

    status: InvoiceStatus = InvoiceStatus.UNPAID
    created_at: datetime = field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None

    payment: Optional[Payment] = None

    def register_payment(self, payment: Payment):
        if self.payment is not None:
            raise InvalidStateTransition("Invoice sudah punya Payment")
        if payment.amount.amount != self.amount_due.amount:
            # simplifikasi: harus lunas full
            raise InvalidStateTransition("Jumlah pembayaran tidak sesuai")
        self.payment = payment

    def mark_settled(self, now: Optional[datetime] = None):
        if self.status is InvoiceStatus.SETTLED:
            return
        self.status = InvoiceStatus.SETTLED
        self.paid_at = now or datetime.utcnow()

    def mark_failed(self):
        if self.status is InvoiceStatus.FAILED:
            return
        self.status = InvoiceStatus.FAILED

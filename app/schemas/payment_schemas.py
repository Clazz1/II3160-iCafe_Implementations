from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.domain.value_objects import InvoiceStatus, PaymentStatus


class InvoiceCreateRequest(BaseModel):
    bill_id: str
    customer_id: str
    amount_due: int
    phone: Optional[str] = None
    email: Optional[str] = None


class PayInvoiceRequest(BaseModel):
    method: str  # QRIS / E_WALLET / CARD / CASH


class InvoiceResponse(BaseModel):
    id: str
    bill_id: str
    customer_id: str
    amount_due: int
    status: InvoiceStatus
    payment_status: Optional[PaymentStatus] = None
    created_at: datetime
    paid_at: Optional[datetime]

    class Config:
        orm_mode = True

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.apps.services.payment_service import PaymentService
from app.infrastructure.repositories.invoice_inmemory import InMemoryInvoiceRepository
from app.schemas.payment_schemas import (
    InvoiceCreateRequest,
    PayInvoiceRequest,
    InvoiceResponse,
)

router = APIRouter(prefix="/invoices", tags=["payment / invoices"])

_invoice_repo = InMemoryInvoiceRepository()
_payment_service = PaymentService(_invoice_repo)


def to_response(inv) -> InvoiceResponse:
    payment_status = inv.payment.status if inv.payment else None

    return InvoiceResponse(
        id=inv.id,
        bill_id=inv.bill_id,
        customer_id=inv.customer_id,
        amount_due=inv.amount_due.amount,
        status=inv.status,
        payment_status=payment_status,
        created_at=inv.created_at,
        paid_at=inv.paid_at,
    )


@router.post("", response_model=InvoiceResponse)
def create_invoice(payload: InvoiceCreateRequest):
    inv = _payment_service.create_invoice(
        bill_id=payload.bill_id,
        customer_id=payload.customer_id,
        amount_due=payload.amount_due,
        phone=payload.phone,
        email=payload.email,
    )
    return to_response(inv)


@router.post("/{invoice_id}/pay", response_model=InvoiceResponse)
def pay_invoice(invoice_id: str, payload: PayInvoiceRequest):
    try:
        inv = _payment_service.pay_invoice(invoice_id=invoice_id, method=payload.method)
    except KeyError:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return to_response(inv)


@router.get("", response_model=list[InvoiceResponse])
def list_invoices():
    return [to_response(i) for i in _payment_service.list_invoices()]

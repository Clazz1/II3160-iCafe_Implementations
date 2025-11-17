from __future__ import annotations

import uuid

from app.domain.payment_aggregate import Invoice, Payment
from app.domain.value_objects import Money, Contact, PaymentStatus
from app.infrastructure.repositories.invoice_inmemory import InMemoryInvoiceRepository


class PaymentService:
    def __init__(self, repo: InMemoryInvoiceRepository) -> None:
        self.repo = repo

    def create_invoice(
        self,
        bill_id: str,
        customer_id: str,
        amount_due: int,
        phone: str | None,
        email: str | None,
    ) -> Invoice:
        invoice = Invoice(
            id=str(uuid.uuid4()),
            bill_id=bill_id,
            customer_id=customer_id,
            amount_due=Money(amount=amount_due),
            contact=Contact(phone=phone, email=email),
        )
        self.repo.add(invoice)
        return invoice

    def pay_invoice(
        self,
        invoice_id: str,
        method: str,
    ) -> Invoice:
        invoice = self.repo.get(invoice_id)
        if not invoice:
            raise KeyError("Invoice not found")

        payment = Payment(
            id=str(uuid.uuid4()),
            invoice_id=invoice.id,
            amount=invoice.amount_due,
            method=method,
            status=PaymentStatus.PENDING,
        )
        payment.mark_settled()
        invoice.register_payment(payment)
        invoice.mark_settled()
        self.repo.update(invoice)
        return invoice

    def list_invoices(self):
        return self.repo.list()

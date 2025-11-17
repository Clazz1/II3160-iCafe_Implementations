from __future__ import annotations

from app.domain.payment_aggregate import Invoice
from .base import AbstractInMemoryRepository


class InMemoryInvoiceRepository(AbstractInMemoryRepository[Invoice]):
    pass

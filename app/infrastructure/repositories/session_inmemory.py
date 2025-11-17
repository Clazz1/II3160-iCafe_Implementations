from __future__ import annotations

from app.domain.billing_aggregate import Session
from .base import AbstractInMemoryRepository


class InMemorySessionRepository(AbstractInMemoryRepository[Session]):
    pass

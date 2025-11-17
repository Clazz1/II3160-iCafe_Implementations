from __future__ import annotations

from app.domain.reservation_aggregate import Reservation
from .base import AbstractInMemoryRepository


class InMemoryReservationRepository(AbstractInMemoryRepository[Reservation]):
    pass

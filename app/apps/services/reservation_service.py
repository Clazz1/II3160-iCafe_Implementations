from __future__ import annotations

import uuid
from datetime import datetime

from app.domain.reservation_aggregate import Reservation, Package
from app.domain.value_objects import TimeSlot
from app.infrastructure.repositories.reservation_inmemory import (
    InMemoryReservationRepository,
)


class ReservationService:
    def __init__(self, repo: InMemoryReservationRepository) -> None:
        self.repo = repo

    def create_reservation(
        self,
        customer_id: str,
        workstation_id: str | None,
        start: datetime,
        end: datetime,
        package_name: str,
        package_duration_minutes: int,
        package_price_amount: int,
    ) -> Reservation:
        time_slot = TimeSlot(start=start, end=end)
        package = Package(
            id=str(uuid.uuid4()),
            name=package_name,
            description=None,
            duration_minutes=package_duration_minutes,
            base_price_amount=package_price_amount,
        )
        reservation = Reservation(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            workstation_id=workstation_id,
            time_slot=time_slot,
            package=package,
        )
        reservation.confirm()
        self.repo.add(reservation)
        return reservation

    def list_reservations(self):
        return self.repo.list()

    def check_in(self, reservation_id: str) -> Reservation:
        reservation = self.repo.get(reservation_id)
        if not reservation:
            raise KeyError("Reservation not found")
        reservation.check_in()
        self.repo.update(reservation)
        return reservation

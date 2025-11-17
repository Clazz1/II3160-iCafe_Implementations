from __future__ import annotations

import uuid
from typing import List

from app.domain.billing_aggregate import Session, TariffPlan
from app.domain.value_objects import Money
from app.infrastructure.repositories.session_inmemory import InMemorySessionRepository


class BillingService:
    def __init__(self, repo: InMemorySessionRepository) -> None:
        self.repo = repo

    def start_session(
        self,
        customer_id: str,
        workstation_id: str,
        reservation_id: str | None = None,
    ) -> Session:
        session = Session(
            id=str(uuid.uuid4()),
            reservation_id=reservation_id,
            customer_id=customer_id,
            workstation_id=workstation_id,
        )
        self.repo.add(session)
        return session

    def finish_and_bill(
        self,
        session_id: str,
        tariff_name: str,
        rate_per_minute: int,
    ) -> Session:
        session = self.repo.get(session_id)
        if not session:
            raise KeyError("Session not found")

        session.finish()

        tariff = TariffPlan(
            id=str(uuid.uuid4()),
            name=tariff_name,
            rate_per_minute=Money(amount=rate_per_minute),
            overtime_rate_per_minute=Money(amount=rate_per_minute),
        )

        session.generate_bill(tariff=tariff, bill_id=str(uuid.uuid4()))
        self.repo.update(session)
        return session

    def list_sessions(self) -> List[Session]:
        return self.repo.list()

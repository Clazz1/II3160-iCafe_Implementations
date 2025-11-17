from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.apps.services.billing_service import BillingService
from app.infrastructure.repositories.session_inmemory import InMemorySessionRepository
from app.schemas.billing_schemas import (
    SessionCreateRequest,
    SessionFinishRequest,
    SessionResponse,
)

router = APIRouter(prefix="/sessions", tags=["billing / sessions"])

_session_repo = InMemorySessionRepository()
_billing_service = BillingService(_session_repo)


def to_response(s) -> SessionResponse:
    bill_id = s.bill.id if s.bill else None
    bill_total = s.bill.total.amount if s.bill else None
    bill_status = s.bill.status if s.bill else None

    return SessionResponse(
        id=s.id,
        reservation_id=s.reservation_id,
        customer_id=s.customer_id,
        workstation_id=s.workstation_id,
        started_at=s.started_at,
        ended_at=s.ended_at,
        status=s.status,
        bill_id=bill_id,
        bill_total=bill_total,
        bill_status=bill_status,
    )


@router.post("", response_model=SessionResponse)
def start_session(payload: SessionCreateRequest):
    s = _billing_service.start_session(
        customer_id=payload.customer_id,
        workstation_id=payload.workstation_id,
        reservation_id=payload.reservation_id,
    )
    return to_response(s)


@router.post("/{session_id}/finish", response_model=SessionResponse)
def finish_session(session_id: str, payload: SessionFinishRequest):
    try:
        s = _billing_service.finish_and_bill(
            session_id=session_id,
            tariff_name=payload.tariff_name,
            rate_per_minute=payload.rate_per_minute,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    return to_response(s)


@router.get("", response_model=list[SessionResponse])
def list_sessions():
    return [to_response(s) for s in _billing_service.list_sessions()]

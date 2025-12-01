from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends

from app.apps.services.reservation_service import ReservationService
from app.infrastructure.repositories.reservation_inmemory import (
    InMemoryReservationRepository,
)
from app.schemas.reservation_schemas import (
    ReservationCreateRequest,
    ReservationResponse,
)
from app.middleware.auth import get_current_active_user
from app.domain.user_aggregate import User

router = APIRouter(prefix="/reservations", tags=["reservations"])

_reservation_repo = InMemoryReservationRepository()
_reservation_service = ReservationService(_reservation_repo)


def to_response(r) -> ReservationResponse:
    return ReservationResponse(
        id=r.id,
        customer_id=r.customer_id,
        workstation_id=r.workstation_id,
        status=r.status,
        start=r.time_slot.start,
        end=r.time_slot.end,
        package_name=r.package.name,
        package_duration_minutes=r.package.duration_minutes,
        package_price_amount=r.package.base_price_amount,
    )


@router.post("", response_model=ReservationResponse)
def create_reservation(
    payload: ReservationCreateRequest,
    current_user: User = Depends(get_current_active_user)
):
    reservation = _reservation_service.create_reservation(
        customer_id=payload.customer_id,
        workstation_id=payload.workstation_id,
        start=payload.start,
        end=payload.end,
        package_name=payload.package_name,
        package_duration_minutes=payload.package_duration_minutes,
        package_price_amount=payload.package_price_amount,
    )
    return to_response(reservation)


@router.get("", response_model=list[ReservationResponse])
def list_reservations(current_user: User = Depends(get_current_active_user)):
    return [to_response(r) for r in _reservation_service.list_reservations()]


@router.post("/{reservation_id}/check-in", response_model=ReservationResponse)
def check_in(
    reservation_id: str, 
    current_user: User = Depends(get_current_active_user)
):
    try:
        r = _reservation_service.check_in(reservation_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return to_response(r)

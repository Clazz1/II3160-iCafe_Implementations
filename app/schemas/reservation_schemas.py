from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.domain.value_objects import ReservationStatus


class ReservationCreateRequest(BaseModel):
    customer_id: str
    workstation_id: Optional[str] = None
    start: datetime
    end: datetime
    package_name: str
    package_duration_minutes: int
    package_price_amount: int


class ReservationResponse(BaseModel):
    id: str
    customer_id: str
    workstation_id: Optional[str]
    status: ReservationStatus
    start: datetime
    end: datetime
    package_name: str
    package_duration_minutes: int
    package_price_amount: int

    class Config:
        orm_mode = True

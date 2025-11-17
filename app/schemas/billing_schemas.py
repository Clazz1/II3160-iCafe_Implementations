from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.domain.value_objects import SessionStatus, BillStatus


class SessionCreateRequest(BaseModel):
    customer_id: str
    workstation_id: str
    reservation_id: Optional[str] = None


class SessionFinishRequest(BaseModel):
    tariff_name: str
    rate_per_minute: int


class SessionResponse(BaseModel):
    id: str
    reservation_id: Optional[str]
    customer_id: str
    workstation_id: str
    started_at: datetime
    ended_at: Optional[datetime]
    status: SessionStatus
    bill_id: Optional[str]
    bill_total: Optional[int]
    bill_status: Optional[BillStatus]

    class Config:
        orm_mode = True

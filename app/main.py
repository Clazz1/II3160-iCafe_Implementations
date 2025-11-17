from __future__ import annotations

from fastapi import FastAPI

from app.api.reservation_endpoints import router as reservation_router
from app.api.billing_endpoints import router as billing_router
from app.api.payment_endpoints import router as payment_router


def create_app() -> FastAPI:
    app = FastAPI(title="iCafe Platform API", version="0.1.0")
    app.include_router(reservation_router)
    app.include_router(billing_router)
    app.include_router(payment_router)
    return app


app = create_app()

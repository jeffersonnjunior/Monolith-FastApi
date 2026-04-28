from fastapi import APIRouter

from app.api.v1.bank import router as bank_router
from app.api.v1.health import router as health_router

router = APIRouter()
router.include_router(health_router, tags=["health"])
router.include_router(bank_router)

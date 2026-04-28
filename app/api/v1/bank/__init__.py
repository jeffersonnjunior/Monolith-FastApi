from fastapi import APIRouter

from app.api.v1.bank.routes import router as bank_router

router = APIRouter(prefix="/bank")
router.include_router(bank_router)

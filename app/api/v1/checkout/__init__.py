from fastapi import APIRouter

from app.api.v1.checkout.routes import router as checkout_router

router = APIRouter(prefix="/checkout")
router.include_router(checkout_router)

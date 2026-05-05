from fastapi import APIRouter, Depends, Header

from app.core.deps import get_checkout_service
from app.core.exceptions import CheckoutIdempotencyKeyRequired
from app.schemas import CheckoutRequest, CheckoutResponse
from app.services.checkout import CheckoutService

router = APIRouter(tags=["checkout"])


@router.post("/payments/checkout", response_model=CheckoutResponse)
async def checkout_payment(
    payload: CheckoutRequest,
    idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"),
    service: CheckoutService = Depends(get_checkout_service),
) -> CheckoutResponse:
    if not idempotency_key:
        raise CheckoutIdempotencyKeyRequired()

    return await service.checkout(
        user_id=payload.user_id,
        order_amount=payload.order_amount,
        idempotency_key=idempotency_key,
    )

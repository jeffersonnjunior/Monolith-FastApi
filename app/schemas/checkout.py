from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CheckoutRequest(BaseModel):
    user_id: UUID
    order_amount: Decimal = Field(gt=0)


class CheckoutResponse(BaseModel):
    checkout_id: UUID
    user_id: UUID
    amount: Decimal
    status: str
    failure_reason: str | None
    processed_at: datetime

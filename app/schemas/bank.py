from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CreateAccountRequest(BaseModel):
    owner_name: str
    document: str
    agency: str
    account_number: str
    initial_balance: Decimal = Field(default=Decimal("0"), ge=0)


class AccountResponse(BaseModel):
    id: UUID
    owner_name: str
    document: str
    agency: str
    account_number: str
    balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AmountRequest(BaseModel):
    amount: Decimal = Field(gt=0)


class TransferRequest(BaseModel):
    from_account_id: UUID
    to_account_id: UUID
    amount: Decimal = Field(gt=0)


class TransferResponse(BaseModel):
    id: UUID
    from_account_id: UUID
    to_account_id: UUID
    amount: Decimal
    created_at: datetime


class StatementResponse(BaseModel):
    account_id: UUID
    balance: Decimal
    total_transferred_today: Decimal

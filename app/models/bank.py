from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID


@dataclass(slots=True)
class BankAccount:
    id: UUID
    owner_name: str
    document: str
    agency: str
    account_number: str
    balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class BankTransfer:
    id: UUID
    from_account_id: UUID
    to_account_id: UUID
    amount: Decimal
    created_at: datetime


def utc_now() -> datetime:
    return datetime.now(UTC)

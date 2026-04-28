from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date
from decimal import Decimal
from uuid import UUID

import anyio

from app.models import BankAccount, BankTransfer


class BankAccountDAO:
    def __init__(self) -> None:
        self._accounts: dict[UUID, BankAccount] = {}
        self._lock = anyio.Lock()

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        async with self._lock:
            yield

    async def add(self, account: BankAccount) -> None:
        self._accounts[account.id] = account

    async def get(self, account_id: UUID) -> BankAccount | None:
        return self._accounts.get(account_id)

    async def save(self, account: BankAccount) -> None:
        self._accounts[account.id] = account

    async def exists_active_by_agency_and_number(self, agency: str, account_number: str) -> bool:
        return any(
            acc.is_active and acc.agency == agency and acc.account_number == account_number
            for acc in self._accounts.values()
        )


class BankTransferDAO:
    def __init__(self) -> None:
        self._transfers: list[BankTransfer] = []

    async def add(self, transfer: BankTransfer) -> None:
        self._transfers.append(transfer)

    async def get_daily_total_from_account(self, account_id: UUID, reference_date: date) -> Decimal:
        total = Decimal("0")
        for transfer in self._transfers:
            if (
                transfer.from_account_id == account_id
                and transfer.created_at.date() == reference_date
            ):
                total += transfer.amount
        return total

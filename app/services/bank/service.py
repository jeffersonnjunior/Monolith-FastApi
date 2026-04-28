from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.core.exceptions import (
    BankAccountInactive,
    BankAccountNotFound,
    DailyTransferLimitExceeded,
    DuplicateBankAccount,
    InsufficientFunds,
    InvalidAmount,
)
from app.dao import BankAccountDAO, BankTransferDAO
from app.models import BankAccount, BankTransfer

DAILY_TRANSFER_LIMIT = Decimal("10000.00")


class BankService:
    def __init__(self, account_dao: BankAccountDAO, transfer_dao: BankTransferDAO) -> None:
        self._account_dao = account_dao
        self._transfer_dao = transfer_dao

    async def create_account(
        self,
        owner_name: str,
        document: str,
        agency: str,
        account_number: str,
        initial_balance: Decimal = Decimal("0"),
    ) -> BankAccount:
        if initial_balance < Decimal("0"):
            raise InvalidAmount("Initial balance must be greater than or equal to zero.")

        async with self._account_dao.transaction():
            if await self._account_dao.exists_active_by_agency_and_number(agency, account_number):
                raise DuplicateBankAccount("An active account with this agency and number already exists.")

            now = datetime.now(UTC)
            account = BankAccount(
                id=uuid4(),
                owner_name=owner_name,
                document=document,
                agency=agency,
                account_number=account_number,
                balance=initial_balance,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            await self._account_dao.add(account)
            return account

    async def deposit(self, account_id: UUID, amount: Decimal) -> BankAccount:
        self._validate_positive_amount(amount)
        async with self._account_dao.transaction():
            account = await self._require_active_account(account_id)
            account.balance += amount
            account.updated_at = datetime.now(UTC)
            await self._account_dao.save(account)
            return account

    async def withdraw(self, account_id: UUID, amount: Decimal) -> BankAccount:
        self._validate_positive_amount(amount)
        async with self._account_dao.transaction():
            account = await self._require_active_account(account_id)
            if account.balance < amount:
                raise InsufficientFunds("Insufficient funds.")
            account.balance -= amount
            account.updated_at = datetime.now(UTC)
            await self._account_dao.save(account)
            return account

    async def transfer(self, from_account_id: UUID, to_account_id: UUID, amount: Decimal) -> BankTransfer:
        self._validate_positive_amount(amount)
        if from_account_id == to_account_id:
            raise InvalidAmount("Source and destination accounts must be different.")

        async with self._account_dao.transaction():
            from_account = await self._require_active_account(from_account_id)
            to_account = await self._require_active_account(to_account_id)

            if from_account.balance < amount:
                raise InsufficientFunds("Insufficient funds.")

            daily_total = await self._transfer_dao.get_daily_total_from_account(
                from_account_id,
                datetime.now(UTC).date(),
            )
            if daily_total + amount > DAILY_TRANSFER_LIMIT:
                raise DailyTransferLimitExceeded("Daily transfer limit exceeded.")

            now = datetime.now(UTC)
            from_account.balance -= amount
            from_account.updated_at = now
            to_account.balance += amount
            to_account.updated_at = now
            await self._account_dao.save(from_account)
            await self._account_dao.save(to_account)

            transfer = BankTransfer(
                id=uuid4(),
                from_account_id=from_account_id,
                to_account_id=to_account_id,
                amount=amount,
                created_at=now,
            )
            await self._transfer_dao.add(transfer)
            return transfer

    async def get_statement(self, account_id: UUID) -> tuple[Decimal, Decimal]:
        account = await self._require_account(account_id)
        total_transferred_today = await self._transfer_dao.get_daily_total_from_account(
            account_id,
            datetime.now(UTC).date(),
        )
        return account.balance, total_transferred_today

    async def _require_account(self, account_id: UUID) -> BankAccount:
        account = await self._account_dao.get(account_id)
        if account is None:
            raise BankAccountNotFound("Bank account not found.")
        return account

    async def _require_active_account(self, account_id: UUID) -> BankAccount:
        account = await self._require_account(account_id)
        if not account.is_active:
            raise BankAccountInactive("Bank account is inactive.")
        return account

    @staticmethod
    def _validate_positive_amount(amount: Decimal) -> None:
        if amount <= Decimal("0"):
            raise InvalidAmount("Amount must be greater than zero.")

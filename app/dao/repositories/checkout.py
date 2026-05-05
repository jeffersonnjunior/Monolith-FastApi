from decimal import Decimal
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import PaymentCheckout, UserBalance


class CheckoutRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_idempotency_key(self, idempotency_key: str) -> PaymentCheckout | None:
        result = await self._session.execute(
            select(PaymentCheckout).where(PaymentCheckout.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()

    async def add(self, checkout: PaymentCheckout) -> None:
        self._session.add(checkout)
        await self._session.flush()

    async def save(self, checkout: PaymentCheckout) -> None:
        self._session.add(checkout)
        await self._session.flush()


class UserBalanceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_for_user(self, user_id: UUID) -> UserBalance | None:
        result = await self._session.execute(select(UserBalance).where(UserBalance.user_id == user_id))
        return result.scalar_one_or_none()

    async def create_if_missing(self, user_id: UUID, initial_balance: Decimal = Decimal("0")) -> UserBalance:
        existing = await self.get_for_user(user_id)
        if existing is not None:
            return existing

        new_balance = UserBalance(user_id=user_id, balance=initial_balance, version_id=1)
        self._session.add(new_balance)
        await self._session.flush()
        return new_balance

    async def discount_with_version(
        self,
        *,
        user_id: UUID,
        amount: Decimal,
        expected_version: int,
    ) -> bool:
        result = await self._session.execute(
            update(UserBalance)
            .where(UserBalance.user_id == user_id, UserBalance.version_id == expected_version)
            .values(
                balance=UserBalance.balance - amount,
                version_id=UserBalance.version_id + 1,
            )
        )
        await self._session.flush()
        return result.rowcount == 1

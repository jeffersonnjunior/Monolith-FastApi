from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.cache import IdempotencyCache, get_idempotency_cache
from app.core.deps.db import get_session
from app.dao.repositories import CheckoutRepository, UserBalanceRepository
from app.services.checkout import CheckoutService


def get_checkout_service(
    session: AsyncSession = Depends(get_session),
    cache: IdempotencyCache = Depends(get_idempotency_cache),
) -> CheckoutService:
    checkout_repo = CheckoutRepository(session=session)
    user_balance_repo = UserBalanceRepository(session=session)
    return CheckoutService(
        session=session,
        idempotency_cache=cache,
        checkout_repo=checkout_repo,
        user_balance_repo=user_balance_repo,
    )

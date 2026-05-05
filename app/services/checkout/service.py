from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.cache import IdempotencyCache, IdempotencyCacheEntry
from app.core.exceptions import (
    CheckoutConcurrencyConflict,
    CheckoutIdempotencyInProgress,
    CheckoutInsufficientBalance,
    InvalidCheckoutStateTransition,
)
from app.dao.repositories import CheckoutRepository, UserBalanceRepository
from app.models import CheckoutStatus, PaymentCheckout
from app.schemas import CheckoutResponse


class CheckoutStateMachine:
    _allowed_transitions: dict[CheckoutStatus, set[CheckoutStatus]] = {
        CheckoutStatus.CREATED: {CheckoutStatus.PROCESSING},
        CheckoutStatus.PROCESSING: {CheckoutStatus.COMPLETED, CheckoutStatus.FAILED},
        CheckoutStatus.COMPLETED: set(),
        CheckoutStatus.FAILED: set(),
    }

    def transition(self, checkout: PaymentCheckout, target: CheckoutStatus) -> None:
        source = CheckoutStatus(checkout.status)
        allowed_targets = self._allowed_transitions.get(source, set())
        if target not in allowed_targets:
            raise InvalidCheckoutStateTransition(source=source.value, target=target.value)
        checkout.status = target.value
        checkout.updated_at = datetime.now(UTC)


class CheckoutService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        idempotency_cache: IdempotencyCache,
        checkout_repo: CheckoutRepository,
        user_balance_repo: UserBalanceRepository,
    ) -> None:
        self._session = session
        self._idempotency_cache = idempotency_cache
        self._checkout_repo = checkout_repo
        self._user_balance_repo = user_balance_repo
        self._fsm = CheckoutStateMachine()

    async def checkout(self, *, user_id: UUID, order_amount: Decimal, idempotency_key: str) -> CheckoutResponse:
        cached_entry = await self._idempotency_cache.get(idempotency_key)
        if cached_entry is not None:
            if cached_entry.status == CheckoutStatus.PROCESSING.value:
                processing_checkout = await self._checkout_repo.get_by_idempotency_key(idempotency_key)
                if processing_checkout is None or processing_checkout.status == CheckoutStatus.PROCESSING.value:
                    raise CheckoutIdempotencyInProgress()
                return await self._cache_and_build_response(processing_checkout)
            return CheckoutResponse.model_validate(cached_entry.payload)

        existing_checkout = await self._checkout_repo.get_by_idempotency_key(idempotency_key)
        if existing_checkout is not None:
            return await self._handle_existing_checkout(existing_checkout)

        await self._idempotency_cache.set(
            idempotency_key,
            IdempotencyCacheEntry(
                status=CheckoutStatus.PROCESSING.value,
                payload={},
            ),
        )

        pending_error: Exception | None = None
        try:
            async with self._session.begin():
                checkout = PaymentCheckout(
                    id=uuid4(),
                    user_id=user_id,
                    idempotency_key=idempotency_key,
                    amount=order_amount,
                    status=CheckoutStatus.CREATED.value,
                    failure_reason=None,
                )
                await self._checkout_repo.add(checkout)
                self._fsm.transition(checkout, CheckoutStatus.PROCESSING)

                user_balance = await self._user_balance_repo.create_if_missing(user_id=user_id)
                if user_balance.balance < order_amount:
                    checkout.failure_reason = "Insufficient balance."
                    self._fsm.transition(checkout, CheckoutStatus.FAILED)
                    await self._checkout_repo.save(checkout)
                    pending_error = CheckoutInsufficientBalance()

                if pending_error is None:
                    updated = await self._user_balance_repo.discount_with_version(
                        user_id=user_id,
                        amount=order_amount,
                        expected_version=user_balance.version_id,
                    )
                    if not updated:
                        checkout.failure_reason = "Balance update conflict."
                        self._fsm.transition(checkout, CheckoutStatus.FAILED)
                        await self._checkout_repo.save(checkout)
                        pending_error = CheckoutConcurrencyConflict()

                if pending_error is None:
                    self._fsm.transition(checkout, CheckoutStatus.COMPLETED)
                    await self._checkout_repo.save(checkout)
        except IntegrityError:
            existing = await self._checkout_repo.get_by_idempotency_key(idempotency_key)
            if existing is None:
                raise CheckoutConcurrencyConflict() from None
            return await self._handle_existing_checkout(existing)

        final_checkout = await self._checkout_repo.get_by_idempotency_key(idempotency_key)
        if final_checkout is None:
            raise CheckoutConcurrencyConflict()

        response = self._build_response(final_checkout)
        await self._idempotency_cache.set(
            idempotency_key,
            IdempotencyCacheEntry(status=final_checkout.status, payload=response.model_dump(mode="json")),
        )
        if pending_error is not None:
            raise pending_error
        return response

    @staticmethod
    def _build_response(checkout: PaymentCheckout) -> CheckoutResponse:
        return CheckoutResponse(
            checkout_id=checkout.id,
            user_id=checkout.user_id,
            amount=Decimal(checkout.amount),
            status=checkout.status,
            failure_reason=checkout.failure_reason,
            processed_at=checkout.updated_at,
        )

    async def _handle_existing_checkout(self, checkout: PaymentCheckout) -> CheckoutResponse:
        if checkout.status == CheckoutStatus.PROCESSING.value:
            raise CheckoutIdempotencyInProgress()
        return await self._cache_and_build_response(checkout)

    async def _cache_and_build_response(self, checkout: PaymentCheckout) -> CheckoutResponse:
        response = self._build_response(checkout)
        await self._idempotency_cache.set(
            checkout.idempotency_key,
            IdempotencyCacheEntry(status=checkout.status, payload=response.model_dump(mode="json")),
        )
        return response

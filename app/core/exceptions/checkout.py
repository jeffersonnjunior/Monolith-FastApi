from fastapi import HTTPException, status


class CheckoutBusinessException(HTTPException):
    def __init__(self, *, status_code: int, detail: str) -> None:
        super().__init__(status_code=status_code, detail=detail)


class InvalidCheckoutStateTransition(CheckoutBusinessException):
    def __init__(self, source: str, target: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Invalid checkout state transition: {source} -> {target}.",
        )


class CheckoutIdempotencyInProgress(CheckoutBusinessException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="This idempotency key is already being processed.",
        )


class CheckoutIdempotencyKeyRequired(CheckoutBusinessException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Idempotency-Key header is required.",
        )


class CheckoutInsufficientBalance(CheckoutBusinessException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance to complete checkout.",
        )


class CheckoutConcurrencyConflict(CheckoutBusinessException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Concurrency conflict while updating user balance. Retry the request.",
        )

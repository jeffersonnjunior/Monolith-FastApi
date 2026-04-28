from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from uuid import UUID

from app.core.deps import get_bank_service
from app.core.exceptions import (
    BankAccountInactive,
    BankAccountNotFound,
    DailyTransferLimitExceeded,
    DuplicateBankAccount,
    InsufficientFunds,
    InvalidAmount,
)
from app.schemas import (
    AccountResponse,
    AmountRequest,
    CreateAccountRequest,
    StatementResponse,
    TransferRequest,
    TransferResponse,
)
from app.services.bank import BankService

router = APIRouter(tags=["bank"])


def _domain_error_response(exc: Exception) -> JSONResponse:
    status_code = status.HTTP_400_BAD_REQUEST
    if isinstance(exc, BankAccountNotFound):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, (InsufficientFunds, DailyTransferLimitExceeded)):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: CreateAccountRequest,
    service: BankService = Depends(get_bank_service),
) -> AccountResponse | JSONResponse:
    try:
        account = await service.create_account(
            owner_name=payload.owner_name,
            document=payload.document,
            agency=payload.agency,
            account_number=payload.account_number,
            initial_balance=payload.initial_balance,
        )
        return AccountResponse.model_validate(account, from_attributes=True)
    except (DuplicateBankAccount, InvalidAmount) as exc:
        return _domain_error_response(exc)


@router.post("/accounts/{account_id}/deposit", response_model=AccountResponse)
async def deposit(
    account_id: UUID,
    payload: AmountRequest,
    service: BankService = Depends(get_bank_service),
) -> AccountResponse | JSONResponse:
    try:
        account = await service.deposit(account_id=account_id, amount=payload.amount)
        return AccountResponse.model_validate(account, from_attributes=True)
    except (BankAccountNotFound, BankAccountInactive, InvalidAmount) as exc:
        return _domain_error_response(exc)


@router.post("/accounts/{account_id}/withdraw", response_model=AccountResponse)
async def withdraw(
    account_id: UUID,
    payload: AmountRequest,
    service: BankService = Depends(get_bank_service),
) -> AccountResponse | JSONResponse:
    try:
        account = await service.withdraw(account_id=account_id, amount=payload.amount)
        return AccountResponse.model_validate(account, from_attributes=True)
    except (BankAccountNotFound, BankAccountInactive, InvalidAmount, InsufficientFunds) as exc:
        return _domain_error_response(exc)


@router.post("/transfers", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
async def transfer(
    payload: TransferRequest,
    service: BankService = Depends(get_bank_service),
) -> TransferResponse | JSONResponse:
    try:
        transfer_result = await service.transfer(
            from_account_id=payload.from_account_id,
            to_account_id=payload.to_account_id,
            amount=payload.amount,
        )
        return TransferResponse.model_validate(transfer_result, from_attributes=True)
    except (
        BankAccountNotFound,
        BankAccountInactive,
        InvalidAmount,
        InsufficientFunds,
        DailyTransferLimitExceeded,
    ) as exc:
        return _domain_error_response(exc)


@router.get("/accounts/{account_id}/statement", response_model=StatementResponse)
async def statement(
    account_id: UUID,
    service: BankService = Depends(get_bank_service),
) -> StatementResponse | JSONResponse:
    try:
        balance, total_transferred_today = await service.get_statement(account_id=account_id)
        return StatementResponse(
            account_id=account_id,
            balance=balance,
            total_transferred_today=total_transferred_today,
        )
    except BankAccountNotFound as exc:
        return _domain_error_response(exc)

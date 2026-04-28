from app.dao import BankAccountDAO, BankTransferDAO
from app.services.bank import BankService

_account_dao = BankAccountDAO()
_transfer_dao = BankTransferDAO()
_bank_service = BankService(account_dao=_account_dao, transfer_dao=_transfer_dao)


def get_bank_service() -> BankService:
    return _bank_service

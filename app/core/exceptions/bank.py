class DomainError(Exception):
    """Base error for domain rules."""


class BankAccountNotFound(DomainError):
    pass


class BankAccountInactive(DomainError):
    pass


class InsufficientFunds(DomainError):
    pass


class DailyTransferLimitExceeded(DomainError):
    pass


class InvalidAmount(DomainError):
    pass


class DuplicateBankAccount(DomainError):
    pass

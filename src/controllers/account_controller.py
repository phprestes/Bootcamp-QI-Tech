from constants import MAX_ACCOUNTS_PER_CUSTOMER
from controllers.base_controller import BaseController
from dtos import AccountDTO
from errors import AccountHasBalance, AccountLimitReached, InvalidStatusTransition, NotFoundAccount, NotFoundCustomer
from models import Account, AccountStatus
from repositories import AccountRepository, CustomerRepository


# Máquina de estados: docs/04-dados/estados.md.
ALLOWED_TRANSITIONS = {
    AccountStatus.ACTIVE: {AccountStatus.BLOCKED, AccountStatus.CLOSED},
    AccountStatus.BLOCKED: {AccountStatus.ACTIVE},
    AccountStatus.CLOSED: set(),
}


class AccountController(BaseController):
    def __init__(self) -> None:
        super().__init__(__name__)
        self.account_repository = AccountRepository(self.context)
        self.customer_repository = CustomerRepository(self.context)

    def create(self, customer_key: str) -> dict:
        """O cliente fica travado da contagem até o commit: duas aberturas simultâneas não furam o limite."""
        customer = self.customer_repository.get_by_key_for_update(customer_key)

        if customer is None:
            raise NotFoundCustomer(customer_key)

        if self.account_repository.count_not_closed_by_customer(customer) >= MAX_ACCOUNTS_PER_CUSTOMER:
            raise AccountLimitReached(MAX_ACCOUNTS_PER_CUSTOMER)

        account = self.account_repository.create(customer)

        account_dto = AccountDTO.only_obj_key(account)
        self.logger.info("Conta aberta")
        self.session.commit()

        return account_dto

    def get_by_key(self, account_key: str) -> dict:
        return AccountDTO.obj_to_dict(self._get_account(account_key))

    def get_list_by_customer(self, customer_key: str, limit: int, offset: int) -> dict:
        customer = self.customer_repository.get_by_key(customer_key)

        if customer is None:
            raise NotFoundCustomer(customer_key)

        accounts = self.account_repository.list_page_by_customer(customer, limit, offset)

        return {
            "data": AccountDTO.list_obj_to_list_dict(accounts[:limit]),
            "is_last_page": len(accounts) <= limit,
        }

    def change_status(self, account_key: str, to_status: str, reason: str = None) -> dict:
        """Conta travada: um depósito concorrente não muda o saldo entre a checagem e o encerramento."""
        account = self.account_repository.get_by_key_for_update(account_key)

        if account is None:
            raise NotFoundAccount(account_key)

        from_status = account.status.enumerator

        if to_status not in ALLOWED_TRANSITIONS[from_status]:
            raise InvalidStatusTransition(from_status, to_status)

        if to_status == AccountStatus.CLOSED and account.balance != 0:
            raise AccountHasBalance()

        self.account_repository.update_status(account, to_status, reason)

        account_dto = AccountDTO.only_obj_key(account)
        self.logger.info(f"Conta passou de {from_status} para {to_status}")
        self.session.commit()

        return account_dto

    def _get_account(self, account_key: str) -> Account:
        account = self.account_repository.get_by_key(account_key)

        if account is None:
            raise NotFoundAccount(account_key)

        return account

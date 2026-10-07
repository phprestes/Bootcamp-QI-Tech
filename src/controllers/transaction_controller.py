from sqlalchemy.exc import IntegrityError

from constants import TRANSFER_FEE_CENTS
from controllers.base_controller import BaseController
from dtos import TransactionDTO
from errors import (
    AccountNotActive,
    InsufficientBalance,
    NotFoundAccount,
    NotFoundDestinationAccount,
    NotFoundTransaction,
    RequestControlKeyConflict,
    SameAccountTransfer,
)
from models import Account, AccountStatus, Transaction, TransactionType
from repositories import AccountRepository, TransactionRepository


DEPOSIT = "DEPOSIT"
TRANSFER = "TRANSFER"

# Tipo do pedido → tipo do lançamento principal, usado para reconhecer a repetição.
MAIN_ENTRY_TYPE = {
    DEPOSIT: TransactionType.DEPOSIT,
    TRANSFER: TransactionType.TRANSFER_OUT,
}


class TransactionController(BaseController):
    """Depósito, transferência com tarifa e extrato. Principal desafio: docs/05-fluxos/transferencia.md."""

    def __init__(self) -> None:
        super().__init__(__name__)
        self.account_repository = AccountRepository(self.context)
        self.transaction_repository = TransactionRepository(self.context)

    def create(self, account_key: str, transaction_data: dict) -> tuple:
        """Devolve (dto, created). `created` falso quer dizer repetição idempotente (ADR 0006)."""
        request_control_key = transaction_data["request_control_key"]

        existing = self.transaction_repository.get_by_request_control_key(request_control_key)
        if existing is not None:
            return self._replay(existing, account_key, transaction_data), False

        try:
            if transaction_data["type"] == DEPOSIT:
                return self._deposit(account_key, transaction_data), True

            return self._transfer(account_key, transaction_data), True
        except IntegrityError as error:
            # Mesma chave nova em duas requisições simultâneas: a segunda perde no UNIQUE e vira repetição.
            if "request_control_key" not in str(error.orig):
                raise
            self.session.rollback()
            existing = self.transaction_repository.get_by_request_control_key(request_control_key)
            return self._replay(existing, account_key, transaction_data), False

    def get_statement(self, account_key: str, limit: int, offset: int, type_enumerator: str = None) -> dict:
        account = self._get_account(account_key)

        transactions = self.transaction_repository.list_page_by_account(account, limit, offset, type_enumerator)

        return {
            "data": TransactionDTO.list_obj_to_list_dict(transactions[:limit]),
            "is_last_page": len(transactions) <= limit,
        }

    def get_by_key(self, account_key: str, transaction_key: str) -> dict:
        account = self._get_account(account_key)

        transaction = self.transaction_repository.get_by_key_and_account(transaction_key, account)

        if transaction is None:
            raise NotFoundTransaction(transaction_key)

        return TransactionDTO.obj_to_dict(transaction)

    def _deposit(self, account_key: str, transaction_data: dict) -> dict:
        account = self.account_repository.get_by_key_for_update(account_key)

        if account is None:
            raise NotFoundAccount(account_key)

        self._ensure_active(account)

        amount = transaction_data["amount"]
        deposit = self.transaction_repository.create(
            account,
            TransactionType.DEPOSIT,
            amount,
            request_control_key=transaction_data["request_control_key"],
        )
        self.account_repository.change_balance(account, amount)
        self.session.flush()

        transaction_dto = TransactionDTO.operation_to_dict(deposit, fee=0, balance_after=account.balance)
        self.logger.info("Depósito registrado")
        self.session.commit()

        return transaction_dto

    def _transfer(self, account_key: str, transaction_data: dict) -> dict:
        """Três lançamentos e dois saldos num commit só, com as contas travadas em ordem de id."""
        destination_key = transaction_data["destination_account_key"]
        amount = transaction_data["amount"]

        origin = self._get_account(account_key)

        if destination_key == account_key:
            raise SameAccountTransfer()

        destination = self.account_repository.get_by_key(destination_key)
        if destination is None:
            raise NotFoundDestinationAccount(destination_key)

        self.account_repository.lock_in_id_order([origin, destination])

        # Revalida depois da trava: o que foi lido antes dela pode ter mudado.
        self._ensure_active(origin)
        self._ensure_active(destination)

        if origin.balance < amount + TRANSFER_FEE_CENTS:
            self.logger.info("Transferência recusada: saldo insuficiente")
            raise InsufficientBalance()

        transfer_out = self.transaction_repository.create(
            origin,
            TransactionType.TRANSFER_OUT,
            amount,
            counterpart_account=destination,
            request_control_key=transaction_data["request_control_key"],
        )
        self.transaction_repository.create(
            destination,
            TransactionType.TRANSFER_IN,
            amount,
            counterpart_account=origin,
            origin_transaction=transfer_out,
        )
        self.transaction_repository.create(
            origin,
            TransactionType.FEE,
            TRANSFER_FEE_CENTS,
            origin_transaction=transfer_out,
        )

        self.account_repository.change_balance(origin, -(amount + TRANSFER_FEE_CENTS))
        self.account_repository.change_balance(destination, amount)
        self.session.flush()

        transaction_dto = TransactionDTO.operation_to_dict(
            transfer_out, fee=TRANSFER_FEE_CENTS, balance_after=origin.balance
        )
        self.logger.info("Transferência registrada")
        self.session.commit()

        return transaction_dto

    def _replay(self, existing: Transaction, account_key: str, transaction_data: dict) -> dict:
        """Mesma chave e mesmo pedido: devolve a resposta original, reconstruída do extrato. Pedido diferente: 409."""
        request_control_key = transaction_data["request_control_key"]
        counterpart = existing.counterpart_account

        same_request = (
            existing.account.account_key == account_key
            and existing.type.enumerator == MAIN_ENTRY_TYPE[transaction_data["type"]]
            and existing.amount == transaction_data["amount"]
            and (counterpart.account_key if counterpart is not None else None)
            == transaction_data.get("destination_account_key")
        )

        if not same_request:
            raise RequestControlKeyConflict(request_control_key)

        fee = self.transaction_repository.get_fee_of(existing)
        last_entry = fee if fee is not None else existing
        balance_after = self.transaction_repository.balance_up_to(existing.account, last_entry.id)

        self.logger.info("Pedido repetido: devolvendo a transação original")

        return TransactionDTO.operation_to_dict(
            existing, fee=fee.amount if fee is not None else 0, balance_after=balance_after
        )

    def _ensure_active(self, account: Account) -> None:
        """Compara pelo status_id, que a trava acabou de reler; a relação carregada antes dela pode estar velha."""
        status = self.session.get(AccountStatus, account.status_id).enumerator

        if status != AccountStatus.ACTIVE:
            raise AccountNotActive(account.account_key, status)

    def _get_account(self, account_key: str) -> Account:
        account = self.account_repository.get_by_key(account_key)

        if account is None:
            raise NotFoundAccount(account_key)

        return account

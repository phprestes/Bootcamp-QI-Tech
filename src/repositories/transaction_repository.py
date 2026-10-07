from uuid import uuid4

from sqlalchemy import case, func

from database import Context
from models import Account, Transaction, TransactionType


class TransactionRepository:
    """Só cria e lê: lançamento é append-only (R4)."""

    def __init__(self, context: Context) -> None:
        self.session = context.db_session

    def create(
        self,
        account: Account,
        type_enumerator: str,
        amount: int,
        counterpart_account: Account = None,
        origin_transaction: Transaction = None,
        request_control_key: str = None,
    ) -> Transaction:
        transaction = Transaction()
        transaction.transaction_key = str(uuid4())
        transaction.account = account
        transaction.type = self.get_type(type_enumerator)
        transaction.amount = amount
        transaction.counterpart_account = counterpart_account
        transaction.origin_transaction = origin_transaction
        transaction.request_control_key = request_control_key

        self.session.add(transaction)
        self.session.flush()

        return transaction

    def balance_up_to(self, account: Account, last_transaction_id: int) -> int:
        """Saldo reconstruído do extrato até um lançamento; serve para repetir a resposta original."""
        signed_amount = case(
            (TransactionType.enumerator.in_(TransactionType.CREDIT_TYPES), Transaction.amount),
            else_=-Transaction.amount,
        )

        balance = (
            self.session.query(func.coalesce(func.sum(signed_amount), 0))
            .join(TransactionType, Transaction.type_id == TransactionType.id)
            .filter(Transaction.account_id == account.id)
            .filter(Transaction.id <= last_transaction_id)
            .scalar()
        )

        return int(balance)

    def get_type(self, enumerator: str) -> TransactionType:
        return self.session.query(TransactionType).filter(TransactionType.enumerator == enumerator).one()

    def get_by_request_control_key(self, request_control_key: str) -> Transaction:
        return (
            self.session.query(Transaction)
            .filter(Transaction.request_control_key == request_control_key)
            .first()
        )

    def get_fee_of(self, transaction: Transaction) -> Transaction:
        return (
            self.session.query(Transaction)
            .join(TransactionType, Transaction.type_id == TransactionType.id)
            .filter(Transaction.origin_transaction_id == transaction.id)
            .filter(TransactionType.enumerator == TransactionType.FEE)
            .first()
        )

    def get_by_key_and_account(self, transaction_key: str, account: Account) -> Transaction:
        """Filtra pelo dono: lançamento de outra conta é tratado como inexistente (R8)."""
        return (
            self.session.query(Transaction)
            .filter(Transaction.transaction_key == transaction_key)
            .filter(Transaction.account_id == account.id)
            .first()
        )

    def list_page_by_account(self, account: Account, limit: int, offset: int, type_enumerator: str = None) -> list:
        query = self.session.query(Transaction).filter(Transaction.account_id == account.id)

        if type_enumerator is not None:
            query = query.join(TransactionType, Transaction.type_id == TransactionType.id).filter(
                TransactionType.enumerator == type_enumerator
            )

        query = query.order_by(Transaction.created_at.desc(), Transaction.id.desc())

        return query.limit(limit + 1).offset(offset).all()

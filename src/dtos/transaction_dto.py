from typing import List

from models import Transaction, TransactionType


class TransactionDTO:
    @staticmethod
    def obj_to_dict(transaction: Transaction) -> dict:
        """Linha do extrato; `direction` é derivado do tipo, não é coluna."""
        counterpart = transaction.counterpart_account

        return {
            "transaction_key": transaction.transaction_key,
            "type": transaction.type.enumerator,
            "direction": "CREDIT" if transaction.type.enumerator in TransactionType.CREDIT_TYPES else "DEBIT",
            "amount": transaction.amount,
            "counterpart_account_key": counterpart.account_key if counterpart is not None else None,
            "created_at": transaction.created_at.isoformat(),
        }

    @staticmethod
    def list_obj_to_list_dict(transactions: List[Transaction]) -> List[dict]:
        return [TransactionDTO.obj_to_dict(transaction) for transaction in transactions]

    @staticmethod
    def operation_to_dict(transaction: Transaction, fee: int, balance_after: int) -> dict:
        """Resposta do POST: o lançamento principal, a tarifa cobrada e o saldo logo depois da operação."""
        return {
            "transaction_key": transaction.transaction_key,
            "type": transaction.type.enumerator,
            "amount": transaction.amount,
            "fee": fee,
            "balance": balance_after,
        }

from typing import List

from models import Account


class AccountDTO:
    @staticmethod
    def obj_to_dict(account: Account) -> dict:
        """Versão completa, com a trilha de estados; a listagem usa a simplificada."""
        dto = AccountDTO.obj_to_simplified_dict(account)
        dto["status_events"] = []

        for event in account.status_events:
            dto["status_events"].append(
                {
                    "from_status": event.from_status.enumerator if event.from_status is not None else None,
                    "to_status": event.to_status.enumerator,
                    "reason": event.reason,
                    "created_at": event.created_at.isoformat(),
                }
            )

        return dto

    @staticmethod
    def obj_to_simplified_dict(account: Account) -> dict:
        return {
            "account_key": account.account_key,
            "customer_key": account.customer.customer_key,
            "status": account.status.enumerator,
            "balance": account.balance,
            "created_at": account.created_at.isoformat(),
        }

    @staticmethod
    def list_obj_to_list_dict(accounts: List[Account]) -> List[dict]:
        return [AccountDTO.obj_to_simplified_dict(account) for account in accounts]

    @staticmethod
    def only_obj_key(account: Account) -> dict:
        return {
            "account_key": account.account_key,
            "status": account.status.enumerator,
            "balance": account.balance,
        }

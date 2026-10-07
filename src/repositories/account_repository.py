from uuid import uuid4

from sqlalchemy import func

from database import Context
from models import Account, AccountStatus, AccountStatusEvent, Customer


class AccountRepository:
    def __init__(self, context: Context) -> None:
        self.session = context.db_session

    def create(self, customer: Customer) -> Account:
        account = Account()
        account.account_key = str(uuid4())
        account.customer = customer
        account.balance = 0

        self.session.add(account)
        self.update_status(account, AccountStatus.ACTIVE, reason="account opened")
        self.session.flush()

        return account

    def update_status(self, account: Account, to_status_enumerator: str, reason: str = None) -> None:
        """Estado novo e evento entram juntos; o commit é do controller."""
        to_status = self.get_status(to_status_enumerator)

        event = AccountStatusEvent()
        event.from_status = account.status
        event.to_status = to_status
        event.reason = reason

        account.status = to_status
        account.status_events.append(event)
        account.updated_at = func.now()

    def change_balance(self, account: Account, delta: int) -> None:
        account.balance = account.balance + delta
        account.updated_at = func.now()

    def get_status(self, enumerator: str) -> AccountStatus:
        return self.session.query(AccountStatus).filter(AccountStatus.enumerator == enumerator).one()

    def get_by_key(self, account_key: str) -> Account:
        return self.session.query(Account).filter(Account.account_key == account_key).first()

    def get_by_key_for_update(self, account_key: str) -> Account:
        return self.session.query(Account).filter(Account.account_key == account_key).with_for_update().first()

    def lock_in_id_order(self, accounts: list) -> list:
        """Trava sempre do menor para o maior id: A→B e B→A simultâneas não entram em deadlock."""
        ids = sorted(account.id for account in accounts)

        locked = (
            self.session.query(Account)
            .filter(Account.id.in_(ids))
            .order_by(Account.id)
            .with_for_update()
            .populate_existing()
            .all()
        )

        return locked

    def count_not_closed_by_customer(self, customer: Customer) -> int:
        return (
            self.session.query(func.count(Account.id))
            .join(AccountStatus, Account.status_id == AccountStatus.id)
            .filter(Account.customer_id == customer.id)
            .filter(AccountStatus.enumerator != AccountStatus.CLOSED)
            .scalar()
        )

    def list_page_by_customer(self, customer: Customer, limit: int, offset: int) -> list:
        query = (
            self.session.query(Account)
            .filter(Account.customer_id == customer.id)
            .order_by(Account.created_at.desc(), Account.id.desc())
        )

        return query.limit(limit + 1).offset(offset).all()

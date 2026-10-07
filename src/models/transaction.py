from sqlalchemy import CHAR, BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import relationship

from models.base import Base
from models.account import Account
from models.transaction_type import TransactionType


class Transaction(Base):
    """Append-only (R4): nenhum repository atualiza nem apaga lançamentos."""

    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True)
    transaction_key = Column(CHAR(36), nullable=False)
    account_id = Column(Integer, ForeignKey(Account.id), nullable=False)
    type_id = Column(Integer, ForeignKey(TransactionType.id), nullable=False)
    amount = Column(BigInteger, nullable=False)
    counterpart_account_id = Column(Integer, ForeignKey(Account.id), nullable=True)
    origin_transaction_id = Column(Integer, ForeignKey("transaction.id"), nullable=True)
    request_control_key = Column(CHAR(36), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("transaction_key"),
        UniqueConstraint("request_control_key"),
        CheckConstraint("amount > 0", name="amount_positive"),
    )

    account = relationship("Account", foreign_keys=[account_id], lazy="selectin")
    type = relationship("TransactionType", foreign_keys=[type_id], lazy="selectin")
    counterpart_account = relationship("Account", foreign_keys=[counterpart_account_id], lazy="selectin")
    origin_transaction = relationship("Transaction", remote_side=[id], foreign_keys=[origin_transaction_id])

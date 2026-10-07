from sqlalchemy import CHAR, BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import relationship

from models.base import Base
from models.account_status import AccountStatus
from models.customer import Customer


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True)
    account_key = Column(CHAR(36), nullable=False)
    customer_id = Column(Integer, ForeignKey(Customer.id), nullable=False)
    status_id = Column(Integer, ForeignKey(AccountStatus.id), nullable=False)
    balance = Column(BigInteger, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("account_key"),
        CheckConstraint("balance >= 0", name="balance_non_negative"),
    )

    customer = relationship("Customer", foreign_keys=[customer_id], lazy="selectin")
    status = relationship("AccountStatus", foreign_keys=[status_id], lazy="selectin")
    status_events = relationship(
        "AccountStatusEvent",
        back_populates="account",
        order_by="asc(AccountStatusEvent.id)",
    )

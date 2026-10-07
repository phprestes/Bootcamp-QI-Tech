from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from models.base import Base
from models.account import Account
from models.account_status import AccountStatus


class AccountStatusEvent(Base):
    """Append-only (R4): uma linha por mudança de estado, inclusive a abertura."""

    __tablename__ = "account_status_event"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey(Account.id), nullable=False)
    from_status_id = Column(Integer, ForeignKey(AccountStatus.id), nullable=True)
    to_status_id = Column(Integer, ForeignKey(AccountStatus.id), nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    account = relationship("Account", foreign_keys=[account_id], back_populates="status_events")
    from_status = relationship("AccountStatus", foreign_keys=[from_status_id], lazy="selectin")
    to_status = relationship("AccountStatus", foreign_keys=[to_status_id], lazy="selectin")

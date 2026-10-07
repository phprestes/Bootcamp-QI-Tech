from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint, func

from models.base import Base


class AccountStatus(Base):
    """A lista de estados mora no banco; a regra de transição mora no AccountController."""

    __tablename__ = "account_status"

    id = Column(Integer, primary_key=True)
    enumerator = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("enumerator"),)

    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    CLOSED = "CLOSED"

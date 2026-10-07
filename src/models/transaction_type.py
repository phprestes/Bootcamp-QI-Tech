from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint, func

from models.base import Base


class TransactionType(Base):
    """O tipo define o sinal do lançamento na conta da linha (ADR 0003)."""

    __tablename__ = "transaction_type"

    id = Column(Integer, primary_key=True)
    enumerator = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("enumerator"),)

    DEPOSIT = "DEPOSIT"
    TRANSFER_OUT = "TRANSFER_OUT"
    TRANSFER_IN = "TRANSFER_IN"
    FEE = "FEE"

    CREDIT_TYPES = (DEPOSIT, TRANSFER_IN)

import uuid
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Numeric, Index, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import enum

class TransactionType(str, enum.Enum):
    debit = "debit"
    credit = "credit"

class TransactionCategory(str, enum.Enum):
    food = "food"
    transport = "transport"
    shopping = "shopping"
    entertainment = "entertainment"
    utilities = "utilities"
    health = "health"
    education = "education"
    rent = "rent"
    salary = "salary"
    investment = "investment"
    transfer = "transfer"
    other = "other"

class TransactionSource(str, enum.Enum):
    sms = "sms"
    pdf_upload = "pdf_upload"
    manual = "manual"

class Transaction(Base):
    __tablename__ = "transactions"

    __table_args__ = (
        Index("ix_transactions_user_id_date", "user_id", "transaction_date"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Numeric(18, 2), nullable=False) # Store using decimal/fixed-point representation
    type = Column(SQLAlchemyEnum(TransactionType), nullable=False)
    category = Column(SQLAlchemyEnum(TransactionCategory), nullable=False, default=TransactionCategory.other, index=True)
    sub_category = Column(String, nullable=True)
    description = Column(String, nullable=True)
    merchant_name = Column(String, nullable=True)
    upi_id = Column(String, nullable=True)
    reference_id = Column(String, nullable=True)
    source = Column(SQLAlchemyEnum(TransactionSource), nullable=False, index=True)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    confidence_score = Column(Numeric(5, 2), nullable=True)
    needs_review = Column(Boolean, default=False, nullable=False)


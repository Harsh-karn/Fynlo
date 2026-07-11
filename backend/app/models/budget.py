import uuid
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric, Boolean, Index, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
from app.models.transaction import TransactionCategory
import enum

class BudgetPeriod(str, enum.Enum):
    weekly = "weekly"
    monthly = "monthly"

class Budget(Base):
    __tablename__ = "budgets"

    __table_args__ = (
        Index("ix_budgets_user_id_category", "user_id", "category"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    category = Column(SQLAlchemyEnum(TransactionCategory), nullable=False, index=True)
    limit_amount = Column(Numeric(18, 2), nullable=False) # Store as fixed-point Decimal

    period = Column(SQLAlchemyEnum(BudgetPeriod), nullable=False, default=BudgetPeriod.monthly)
    alert_at_percent = Column(Integer, default=80)
    
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

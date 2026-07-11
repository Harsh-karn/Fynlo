import uuid
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric, Enum as SQLAlchemyEnum
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category = Column(SQLAlchemyEnum(TransactionCategory), nullable=False)
    limit_amount = Column(Numeric(18, 2), nullable=False) # Store as fixed-point Decimal

    period = Column(SQLAlchemyEnum(BudgetPeriod), nullable=False, default=BudgetPeriod.monthly)
    alert_at_percent = Column(Integer, default=80)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

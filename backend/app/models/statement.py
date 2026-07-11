import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Index, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import enum

class StatementStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class Statement(Base):
    __tablename__ = "statements"

    __table_args__ = (
        Index("ix_statements_user_id_status", "user_id", "status"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    bank_name = Column(String, nullable=True)
    status = Column(SQLAlchemyEnum(StatementStatus), nullable=False, default=StatementStatus.pending, index=True)
    transactions_extracted = Column(Integer, default=0)
    
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

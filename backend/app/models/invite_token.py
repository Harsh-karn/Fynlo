import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class InviteToken(Base):
    __tablename__ = "invite_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=True) # Optional specific target email
    is_used = Column(Boolean, default=False, nullable=False)
    used_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

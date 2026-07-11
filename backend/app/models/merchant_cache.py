import uuid
from sqlalchemy import Column, String, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class MerchantCategoryCache(Base):
    __tablename__ = "merchant_category_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False)
    sub_category = Column(String, nullable=True)
    confidence = Column(Numeric(5, 2), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

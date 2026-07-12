import uuid
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    currency = Column(String, default="INR")
    monthly_budget = Column(Numeric(18, 2), nullable=True) # Stored as fixed-point Decimal


    # Account lockout fields
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    # AI usage and limits
    ai_token_usage = Column(Integer, default=0, nullable=False)
    ai_usage_limit = Column(Integer, default=50000, nullable=False) # e.g., 50k tokens per user (adjustable per tier)
    fallback_to_regex = Column(Boolean, default=True, nullable=False)

    # Privacy and Data Processing Consent (DPDP compliance)
    data_consent_given = Column(Boolean, default=False, nullable=False)
    data_consent_timestamp = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Billing and Subscription
    is_pro = Column(Boolean, default=False, nullable=False)
    razorpay_customer_id = Column(String, nullable=True)
    razorpay_subscription_id = Column(String, nullable=True)

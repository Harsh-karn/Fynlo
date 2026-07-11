from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone_number: Optional[str] = None
    currency: str = "INR"

class UserCreate(UserBase):
    password: str = Field(min_length=8)
    invite_token: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    currency: Optional[str] = None
    monthly_budget: Optional[Decimal] = None
    data_consent_given: Optional[bool] = None

class UserResponse(UserBase):
    id: UUID
    monthly_budget: Optional[Decimal] = None
    data_consent_given: bool
    data_consent_timestamp: Optional[datetime] = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[UUID] = None

class TokenRefreshRequest(BaseModel):
    refresh_token: str


from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Optional

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URL: str
    SECRET_KEY: str = "your-jwt-secret-256-bit" # Default for dev
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    REDIS_URL: str = "redis://localhost:6379/0"
    CLOUDINARY_URL: Optional[str] = None
    FRONTEND_URL: str = "http://localhost:3000"
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def validate_production_config(self) -> 'Settings':
        if self.ENVIRONMENT.lower() == "production":
            if self.SECRET_KEY == "your-jwt-secret-256-bit":
                raise ValueError("SECRET_KEY must be changed from default in production mode")
            if len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters in production mode")
            if not self.DATABASE_URL.startswith(("postgresql://", "postgres://")):
                raise ValueError("DATABASE_URL must be a PostgreSQL connection string in production mode")
        return self

settings = Settings()


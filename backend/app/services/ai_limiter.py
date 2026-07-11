from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User
from typing import Tuple

class AILimiterService:
    @staticmethod
    def check_ai_allowance(db: Session, user_id: UUID) -> Tuple[bool, str]:
        """
        Check if the user is allowed to use AI features based on their cost/token limits.
        Returns a tuple: (is_allowed: bool, reason: str)
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "User not found"
            
        if user.ai_token_usage >= user.ai_usage_limit:
            if user.fallback_to_regex:
                return False, "Token limit exceeded. Gracefully degrading to regex parsing."
            else:
                return False, "Token limit exceeded and fallback to regex is disabled."
                
        return True, "Allowed"

    @staticmethod
    def track_ai_usage(db: Session, user_id: UUID, tokens_used: int) -> None:
        """
        Record AI usage for a user. Should be called after successful LLM invocation.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.ai_token_usage += tokens_used
            db.add(user)
            db.commit()

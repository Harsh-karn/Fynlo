from decimal import Decimal
from app.config import settings

# This would typically send an email. For this implementation, we will just print to console.
# To actually send emails, we would use fastapi-mail as mentioned in the requirements.
class BudgetCheckerService:
    @classmethod
    def check_budget_and_alert(cls, email: str, category: str, usage_percent: float, threshold: int, spend: Decimal, limit: Decimal):
        if usage_percent >= threshold:
            print(f"ALERT: User {email} has used {usage_percent:.1f}% of their {category} budget. Spend: {spend:.2f}, Limit: {limit:.2f}")
            # Here we would enqueue an email task or send it directly.

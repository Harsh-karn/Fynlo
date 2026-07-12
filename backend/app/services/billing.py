import razorpay
import hmac
import hashlib
from app.config import settings
from app.models.user import User
from sqlalchemy.orm import Session
from fastapi import HTTPException

# Initialize Razorpay Client
razorpay_client = None
if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class BillingService:
    PLAN_ID_PRO = "plan_pro_299_inr"  # This should be the Plan ID from Razorpay Dashboard
    
    @classmethod
    def get_or_create_customer(cls, db: Session, user: User) -> str:
        """Get existing Razorpay Customer ID or create a new one."""
        if not razorpay_client:
            raise HTTPException(status_code=503, detail="Billing service is not configured")
            
        if user.razorpay_customer_id:
            return user.razorpay_customer_id
            
        try:
            customer_data = {
                "name": user.name,
                "email": user.email,
                "contact": user.phone_number or ""
            }
            customer = razorpay_client.customer.create(data=customer_data)
            user.razorpay_customer_id = customer['id']
            db.commit()
            return customer['id']
        except Exception as e:
            print(f"Razorpay customer creation failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize billing profile")

    @classmethod
    def create_subscription(cls, db: Session, user: User) -> dict:
        """Create a new subscription for the user."""
        if not razorpay_client:
            raise HTTPException(status_code=503, detail="Billing service is not configured")
            
        customer_id = cls.get_or_create_customer(db, user)
        
        try:
            sub_data = {
                "plan_id": cls.PLAN_ID_PRO,
                "customer_id": customer_id,
                "total_count": 120, # E.g., 10 years
                "customer_notify": 1
            }
            subscription = razorpay_client.subscription.create(data=sub_data)
            return {
                "subscription_id": subscription['id'],
                "status": subscription['status'],
                "short_url": subscription.get('short_url')
            }
        except Exception as e:
            print(f"Razorpay subscription creation failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to create subscription")

    @classmethod
    def verify_webhook_signature(cls, payload: bytes, signature: str) -> bool:
        """Verify the webhook signature from Razorpay."""
        if not settings.RAZORPAY_WEBHOOK_SECRET:
            return False
            
        try:
            expected_sig = hmac.new(
                bytes(settings.RAZORPAY_WEBHOOK_SECRET, 'utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected_sig, signature)
        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False

    @classmethod
    def handle_webhook_event(cls, db: Session, event: dict):
        """Process incoming webhook events."""
        event_type = event.get('event')
        payload = event.get('payload', {})
        
        if event_type == 'subscription.charged':
            sub_obj = payload.get('subscription', {}).get('entity', {})
            sub_id = sub_obj.get('id')
            if sub_id:
                user = db.query(User).filter(User.razorpay_subscription_id == sub_id).first()
                if user:
                    user.is_pro = True
                    # Reset usage if needed, or update limits
                    db.commit()
                    
        elif event_type in ['subscription.cancelled', 'subscription.halted']:
            sub_obj = payload.get('subscription', {}).get('entity', {})
            sub_id = sub_obj.get('id')
            if sub_id:
                user = db.query(User).filter(User.razorpay_subscription_id == sub_id).first()
                if user:
                    user.is_pro = False
                    db.commit()

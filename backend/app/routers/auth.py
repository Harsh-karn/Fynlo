from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import uuid, csv, io, json
from datetime import datetime, timedelta, timezone
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.models.invite_token import InviteToken
from app.models.statement import Statement
from app.models.budget import Budget
from app.models.sms_device import SmsDevice
from app.schemas.user import UserCreate, UserResponse, UserUpdate, Token, TokenRefreshRequest
from app.utils.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.utils.dependencies import get_current_user

# Max failed attempts before temporary lockout

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

# Import the shared limiter from main (avoids duplicate instances)
from app.limiter import limiter
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])



@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, user_in: UserCreate, db: Session = Depends(get_db)):
    # Validate Invite Token if required
    invite_token_obj = None
    if settings.REQUIRE_INVITE_TOKEN:
        if not user_in.invite_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration requires a valid invite token.",
            )
        invite_token_obj = db.query(InviteToken).filter(
            InviteToken.token == user_in.invite_token,
            InviteToken.is_used == False
        ).first()
        if not invite_token_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or already used invite token.",
            )
        if invite_token_obj.expires_at and invite_token_obj.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This invite token has expired.",
            )
        if invite_token_obj.email and invite_token_obj.email.lower() != user_in.email.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This invite token is restricted to a different email address.",
            )

    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        password_hash=hashed_password,
        name=user_in.name,
        phone_number=user_in.phone_number,
        currency=user_in.currency
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Consume invite token
    if invite_token_obj:
        invite_token_obj.is_used = True
        invite_token_obj.used_by_id = db_user.id
        db.add(invite_token_obj)
        db.commit()

    return db_user


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()

    # Account lockout check
    if user and user.locked_until:
        lock_dt = user.locked_until
        # Make lock_dt timezone-aware if it isn't already
        if lock_dt.tzinfo is None:
            lock_dt = lock_dt.replace(tzinfo=timezone.utc)
        if lock_dt > datetime.now(timezone.utc):
            remaining = int((lock_dt - datetime.now(timezone.utc)).total_seconds() / 60) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Account temporarily locked due to repeated failed login attempts. Try again in {remaining} minute(s).",
            )
        else:
            # Lockout expired — reset counters
            user.failed_login_attempts = 0
            user.locked_until = None
            db.add(user)
            db.commit()

    if not user or not verify_password(form_data.password, user.password_hash):
        # Increment failed attempts if the user exists
        if user:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            db.add(user)
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Successful login — reset failed attempt counter
    if user.failed_login_attempts:
        user.failed_login_attempts = 0
        user.locked_until = None
        db.add(user)
        db.commit()

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
def refresh_token_route(refresh_in: TokenRefreshRequest, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_in.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id_str is None or token_type != "refresh":
            raise credentials_exception
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_user_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_user_me(user_in: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/export")
def export_user_data(
    format: str = Query("csv", regex="^(csv|json)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export all user data (transactions, profile) as CSV or JSON.
    Required by India's DPDP Act — right to data portability.
    """
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.is_deleted == False
    ).order_by(Transaction.transaction_date.desc()).all()

    if format == "json":
        data = {
            "profile": {
                "id": str(current_user.id),
                "name": current_user.name,
                "email": current_user.email,
                "phone_number": current_user.phone_number,
                "currency": current_user.currency,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            },
            "transactions": [
                {
                    "id": str(t.id),
                    "amount_paise": t.amount,
                    "amount_inr": round(t.amount / 100, 2),
                    "type": t.type.value if t.type else None,
                    "category": t.category.value if t.category else None,
                    "description": t.description,
                    "merchant_name": t.merchant_name,
                    "upi_id": t.upi_id,
                    "reference_id": t.reference_id,
                    "source": t.source.value if t.source else None,
                    "transaction_date": t.transaction_date.isoformat() if t.transaction_date else None,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                }
                for t in transactions
            ],
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }
        json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        return StreamingResponse(
            io.BytesIO(json_bytes),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=fynlo_data_{current_user.email}.json"}
        )

    # Default: CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "transaction_id", "date", "type", "category", "merchant",
        "description", "amount_inr", "upi_id", "reference_id", "source"
    ])
    for t in transactions:
        writer.writerow([
            str(t.id),
            t.transaction_date.strftime("%Y-%m-%d %H:%M") if t.transaction_date else "",
            t.type.value if t.type else "",
            t.category.value if t.category else "",
            t.merchant_name or "",
            t.description or "",
            round(t.amount / 100, 2),
            t.upi_id or "",
            t.reference_id or "",
            t.source.value if t.source else "",
        ])
    csv_bytes = output.getvalue().encode("utf-8")
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=fynlo_transactions_{current_user.email}.csv"}
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permanently delete the authenticated user's account and ALL associated data.
    Required by India's DPDP Act — right to erasure (Article 12).
    This action is irreversible.
    """
    user_id = current_user.id

    # Cascade delete all user-owned data
    db.query(Transaction).filter(Transaction.user_id == user_id).delete(synchronize_session=False)
    db.query(Statement).filter(Statement.user_id == user_id).delete(synchronize_session=False)
    db.query(Budget).filter(Budget.user_id == user_id).delete(synchronize_session=False)
    db.query(SmsDevice).filter(SmsDevice.user_id == user_id).delete(synchronize_session=False)
    db.query(InviteToken).filter(InviteToken.used_by_id == user_id).delete(synchronize_session=False)

    # Delete the user record itself
    db.delete(current_user)
    db.commit()
    return None

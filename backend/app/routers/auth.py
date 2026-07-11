from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import uuid
from datetime import datetime
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.invite_token import InviteToken
from app.schemas.user import UserCreate, UserResponse, UserUpdate, Token, TokenRefreshRequest
from app.utils.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
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
        if invite_token_obj.expires_at and invite_token_obj.expires_at < datetime.utcnow():
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
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction, TransactionCategory, TransactionType, TransactionSource
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate, TransactionListResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])

@router.get("/", response_model=TransactionListResponse)
def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[TransactionCategory] = None,
    type: Optional[TransactionType] = None,
    source: Optional[TransactionSource] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.is_deleted == False
    )

    if category:
        query = query.filter(Transaction.category == category)
    if type:
        query = query.filter(Transaction.type == type)
    if source:
        query = query.filter(Transaction.source == source)
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Transaction.merchant_name.ilike(search_filter),
                Transaction.description.ilike(search_filter),
                Transaction.upi_id.ilike(search_filter)
            )
        )

    total = query.count()
    items = query.order_by(Transaction.transaction_date.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_transaction = Transaction(
        **transaction_in.model_dump(),
        user_id=current_user.id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id,
        Transaction.is_deleted == False
    ).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: UUID,
    transaction_in: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id,
        Transaction.is_deleted == False
    ).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    update_data = transaction_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction.is_deleted = True
    transaction.deleted_at = datetime.utcnow()
    db.add(transaction)
    db.commit()
    return None

@router.post("/bulk", response_model=List[TransactionResponse], status_code=status.HTTP_201_CREATED)
def bulk_create_transactions(
    transactions_in: List[TransactionCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # This endpoint is used internally by SMS/PDF parsers
    db_transactions = [
        Transaction(**tx.model_dump(), user_id=current_user.id)
        for tx in transactions_in
    ]
    db.add_all(db_transactions)
    db.commit()
    for tx in db_transactions:
        db.refresh(tx)
    return db_transactions

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import UUID
from datetime import datetime, date
import calendar

from app.database import get_db
from app.models.user import User
from app.models.budget import Budget, BudgetPeriod
from app.models.transaction import Transaction, TransactionType
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/budgets", tags=["budgets"])

def get_monthly_spend(db: Session, user_id: UUID, category: str) -> int:
    now = datetime.utcnow()
    # first day of month
    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # last day of month
    _, last_day = calendar.monthrange(now.year, now.month)
    end_date = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
    
    spend = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.category == category,
        Transaction.type == TransactionType.debit,
        Transaction.is_deleted == False,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).scalar()
    
    return spend or 0

@router.get("/", response_model=List[BudgetResponse])
def get_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id, Budget.is_deleted == False).all()
    
    response_list = []
    for b in budgets:
        # Calculate current spend. For simplicity we assume monthly period for now.
        spend = get_monthly_spend(db, current_user.id, b.category)
        usage = (spend / b.limit_amount) * 100 if b.limit_amount > 0 else 0
        
        b_dict = {
            "id": b.id,
            "user_id": b.user_id,
            "category": b.category,
            "limit_amount": b.limit_amount,
            "period": b.period,
            "alert_at_percent": b.alert_at_percent,
            "created_at": b.created_at,
            "updated_at": b.updated_at,
            "current_spend": spend,
            "usage_percent": min(usage, 100.0) # Cap at 100% or allow over 100%? Usually good to show > 100%
        }
        b_dict["usage_percent"] = usage # Show overages
        response_list.append(b_dict)
        
    return response_list

@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget_in: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if budget for category already exists
    existing = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category == budget_in.category,
        Budget.is_deleted == False
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Budget for this category already exists")
        
    budget = Budget(**budget_in.model_dump(), user_id=current_user.id)
    db.add(budget)
    db.commit()
    db.refresh(budget)
    
    # Response
    spend = get_monthly_spend(db, current_user.id, budget.category)
    usage = (spend / budget.limit_amount) * 100 if budget.limit_amount > 0 else 0
    
    response_dict = {**budget.__dict__, "current_spend": spend, "usage_percent": usage}
    return response_dict

@router.patch("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: UUID,
    budget_in: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == current_user.id, Budget.is_deleted == False).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
        
    update_data = budget_in.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(budget, k, v)
        
    db.add(budget)
    db.commit()
    db.refresh(budget)
    
    spend = get_monthly_spend(db, current_user.id, budget.category)
    usage = (spend / budget.limit_amount) * 100 if budget.limit_amount > 0 else 0
    
    response_dict = {**budget.__dict__, "current_spend": spend, "usage_percent": usage}
    return response_dict

@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == current_user.id, Budget.is_deleted == False).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
        
    budget.is_deleted = True
    budget.deleted_at = datetime.utcnow()
    db.add(budget)
    db.commit()
    return None

@router.get("/alerts")
def get_budget_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id, Budget.is_deleted == False).all()
    alerts = []
    
    for b in budgets:
        spend = get_monthly_spend(db, current_user.id, b.category)
        usage = (spend / b.limit_amount) * 100 if b.limit_amount > 0 else 0
        
        if usage >= b.alert_at_percent:
            alerts.append({
                "category": b.category,
                "limit_amount": b.limit_amount,
                "current_spend": spend,
                "usage_percent": usage,
                "alert_threshold": b.alert_at_percent
            })
            
    return alerts

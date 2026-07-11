from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.services.analytics import AnalyticsService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/summary")
def get_summary(
    date: str, # Format: YYYY-MM
    period: str = "monthly",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        year, month = map(int, date.split('-'))
    except ValueError:
        year, month = datetime.utcnow().year, datetime.utcnow().month
        
    return AnalyticsService.get_summary(db, current_user.id, year, month)

@router.get("/category-breakdown")
def get_category_breakdown(
    date: str,
    period: str = "monthly",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        year, month = map(int, date.split('-'))
    except ValueError:
        year, month = datetime.utcnow().year, datetime.utcnow().month
        
    return AnalyticsService.get_category_breakdown(db, current_user.id, year, month)

# Add remaining endpoints /trends, /daily, /merchants/top, /cashflow as needed
@router.get("/trends")
def get_trends(
    months: int = 6,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return AnalyticsService.get_trends(db, current_user.id, months)

@router.get("/daily")
def get_daily(
    date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        year, month = map(int, date.split('-'))
    except ValueError:
        year, month = datetime.utcnow().year, datetime.utcnow().month
    return AnalyticsService.get_daily_spending(db, current_user.id, year, month)

@router.get("/merchants/top")
def get_top_merchants(
    date: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        year, month = map(int, date.split('-'))
    except ValueError:
        year, month = datetime.utcnow().year, datetime.utcnow().month
    return AnalyticsService.get_top_merchants(db, current_user.id, year, month, limit)

@router.get("/cashflow")
def get_cashflow(
    date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        year, month = map(int, date.split('-'))
    except ValueError:
        year, month = datetime.utcnow().year, datetime.utcnow().month
    return AnalyticsService.get_cashflow(db, current_user.id, year, month)


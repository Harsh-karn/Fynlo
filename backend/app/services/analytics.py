from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime
import calendar
from app.models.transaction import Transaction, TransactionType

class AnalyticsService:
    @classmethod
    def get_summary(cls, db: Session, user_id: UUID, year: int, month: int) -> Dict[str, Any]:
        start_date, end_date = cls._get_month_bounds(year, month)
        
        base_query = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        )
        
        income = base_query.filter(Transaction.type == TransactionType.credit).scalar() or 0
        expense = base_query.filter(Transaction.type == TransactionType.debit).scalar() or 0
        
        # Top category
        top_cat_query = db.query(Transaction.category, func.sum(Transaction.amount).label('total'))\
            .filter(
                Transaction.user_id == user_id,
                Transaction.is_deleted == False,
                Transaction.type == TransactionType.debit,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )\
            .group_by(Transaction.category)\
            .order_by(func.sum(Transaction.amount).desc())\
            .first()
            
        top_category = top_cat_query[0] if top_cat_query else None
        
        # Avg daily spend
        _, num_days = calendar.monthrange(year, month)
        avg_daily = expense / num_days if num_days > 0 else 0
        
        return {
            "total_income": income,
            "total_expense": expense,
            "net_savings": income - expense,
            "top_category": top_category,
            "avg_daily_spend": int(avg_daily)
        }

    @classmethod
    def get_category_breakdown(cls, db: Session, user_id: UUID, year: int, month: int) -> List[Dict[str, Any]]:
        start_date, end_date = cls._get_month_bounds(year, month)
        
        # Total expense
        total_expense = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
            Transaction.type == TransactionType.debit,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).scalar() or 0
        
        if total_expense == 0:
            return []
            
        results = db.query(Transaction.category, func.sum(Transaction.amount).label('total'))\
            .filter(
                Transaction.user_id == user_id,
                Transaction.is_deleted == False,
                Transaction.type == TransactionType.debit,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )\
            .group_by(Transaction.category)\
            .order_by(func.sum(Transaction.amount).desc())\
            .all()
            
        breakdown = []
        for cat, amount in results:
            breakdown.append({
                "category": cat,
                "amount": amount,
                "percentage": round((amount / total_expense) * 100, 2)
            })
            
        return breakdown

    @classmethod
    def get_trends(cls, db: Session, user_id: UUID, months_count: int = 6) -> List[Dict[str, Any]]:
        current_year = datetime.utcnow().year
        current_month = datetime.utcnow().month
        
        trends = []
        for i in range(months_count):
            m = current_month - i
            y = current_year
            while m <= 0:
                m += 12
                y -= 1
                
            start_date, end_date = cls._get_month_bounds(y, m)
            
            base_query = db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.is_deleted == False,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )
            
            income = base_query.filter(Transaction.type == TransactionType.credit).scalar() or 0
            expense = base_query.filter(Transaction.type == TransactionType.debit).scalar() or 0
            
            month_label = calendar.month_abbr[m] + " " + str(y)[-2:]
            
            trends.append({
                "month": month_label,
                "income": float(income),
                "expense": float(expense)
            })
            
        return trends[::-1]

    @classmethod
    def get_daily_spending(cls, db: Session, user_id: UUID, year: int, month: int) -> List[Dict[str, Any]]:
        start_date, end_date = cls._get_month_bounds(year, month)
        
        results = db.query(
            func.date(Transaction.transaction_date).label('day'),
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
            Transaction.type == TransactionType.debit,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).group_by(func.date(Transaction.transaction_date))\
         .order_by(func.date(Transaction.transaction_date))\
         .all()
         
        return [{"date": str(day), "amount": float(total)} for day, total in results]

    @classmethod
    def get_top_merchants(cls, db: Session, user_id: UUID, year: int, month: int, limit: int = 10) -> List[Dict[str, Any]]:
        start_date, end_date = cls._get_month_bounds(year, month)
        
        results = db.query(
            Transaction.merchant_name,
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
            Transaction.type == TransactionType.debit,
            Transaction.merchant_name != None,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).group_by(Transaction.merchant_name)\
         .order_by(func.sum(Transaction.amount).desc())\
         .limit(limit)\
         .all()
         
        return [{"merchant": name, "amount": float(total)} for name, total in results]

    @classmethod
    def get_cashflow(cls, db: Session, user_id: UUID, year: int, month: int) -> List[Dict[str, Any]]:
        start_date, end_date = cls._get_month_bounds(year, month)
        
        transactions = db.query(
            Transaction.transaction_date,
            Transaction.type,
            Transaction.amount
        ).filter(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).order_by(Transaction.transaction_date).all()
        
        daily_changes = {}
        _, last_day = calendar.monthrange(year, month)
        
        for day in range(1, last_day + 1):
            date_str = f"{year}-{month:02d}-{day:02d}"
            daily_changes[date_str] = 0.0
            
        for tx_date, tx_type, amount in transactions:
            date_str = tx_date.strftime("%Y-%m-%d")
            if date_str in daily_changes:
                if tx_type == TransactionType.credit:
                    daily_changes[date_str] += float(amount)
                else:
                    daily_changes[date_str] -= float(amount)
                    
        running_balance = 0.0
        cashflow = []
        for date_str in sorted(daily_changes.keys()):
            running_balance += daily_changes[date_str]
            cashflow.append({
                "date": date_str,
                "balance": running_balance
            })
            
        return cashflow

    @classmethod
    def get_notifications(cls, db: Session, user_id: UUID) -> List[Dict[str, Any]]:
        notifications = []
        now = datetime.utcnow()
        year, month = now.year, now.month
        
        # Monthly Spend Summary
        start_date, end_date = cls._get_month_bounds(year, month)
        monthly_expense = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
            Transaction.type == TransactionType.debit,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).scalar() or 0
        
        if monthly_expense > 0:
            notifications.append({
                "id": f"monthly_{year}_{month}",
                "title": "Monthly Spending Update",
                "message": f"You have spent ₹{monthly_expense:,.2f} so far this month.",
                "type": "info",
                "date": now.isoformat(),
                "read": False
            })
            
        # Top Category Alert
        top_cat_query = db.query(Transaction.category, func.sum(Transaction.amount).label('total'))\
            .filter(
                Transaction.user_id == user_id,
                Transaction.is_deleted == False,
                Transaction.type == TransactionType.debit,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )\
            .group_by(Transaction.category)\
            .order_by(func.sum(Transaction.amount).desc())\
            .first()
            
        if top_cat_query and top_cat_query[1] > 0:
            notifications.append({
                "id": f"top_cat_{year}_{month}",
                "title": "Top Spending Category",
                "message": f"Your highest spend is in {top_cat_query[0].value.capitalize()} (₹{top_cat_query[1]:,.2f}).",
                "type": "warning" if top_cat_query[1] > monthly_expense * Decimal('0.5') else "info",
                "date": now.isoformat(),
                "read": False
            })

        return notifications

    @classmethod
    def _get_month_bounds(cls, year: int, month: int):
        start_date = datetime(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = datetime(year, month, last_day, 23, 59, 59, 999999)
        return start_date, end_date


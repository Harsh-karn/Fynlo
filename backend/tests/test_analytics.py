from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.models.transaction import Transaction, TransactionType
from app.utils.security import get_password_hash

client = TestClient(app)

def test_analytics_endpoints(db_session):
    # 1. Create a test user
    hashed_pwd = get_password_hash("password123")
    user = User(
        email="test_analytics@fynlo.com",
        password_hash=hashed_pwd,
        name="Analytics User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 2. Login to get access token
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "test_analytics@fynlo.com", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 3. Insert test transactions
    now = datetime.utcnow()
    # Transaction 1: Current month debit
    t1 = Transaction(
        user_id=user.id,
        amount=1500,
        type=TransactionType.debit,
        category="food",
        merchant_name="Zomato",
        transaction_date=now,
        source="manual"
    )
    # Transaction 2: Current month credit
    t2 = Transaction(
        user_id=user.id,
        amount=5000,
        type=TransactionType.credit,
        category="salary",
        merchant_name="Employer",
        transaction_date=now,
        source="manual"
    )
    # Transaction 3: Last month debit
    last_month = now - timedelta(days=32)
    t3 = Transaction(
        user_id=user.id,
        amount=3000,
        type=TransactionType.debit,
        category="shopping",
        merchant_name="Amazon",
        transaction_date=last_month,
        source="manual"
    )
    db_session.add_all([t1, t2, t3])
    db_session.commit()

    # 4. Test /summary
    date_str = now.strftime("%Y-%m")
    summary_res = client.get(f"/api/v1/analytics/summary?date={date_str}", headers=auth_headers)
    assert summary_res.status_code == 200
    summary_data = summary_res.json()
    assert summary_data["total_income"] == 5000
    assert summary_data["total_expense"] == 1500
    assert summary_data["net_savings"] == 3500

    # 5. Test /category-breakdown
    breakdown_res = client.get(f"/api/v1/analytics/category-breakdown?date={date_str}", headers=auth_headers)
    assert breakdown_res.status_code == 200
    breakdown_data = breakdown_res.json()
    assert len(breakdown_data) == 1
    assert breakdown_data[0]["category"] == "food"
    assert breakdown_data[0]["amount"] == 1500

    # 6. Test /trends
    trends_res = client.get("/api/v1/analytics/trends?months=6", headers=auth_headers)
    assert trends_res.status_code == 200
    trends_data = trends_res.json()
    assert len(trends_data) == 6
    # Find current month in trends
    current_month_label = now.strftime("%b %y")
    current_trend = next((item for item in trends_data if item["month"] == current_month_label), None)
    assert current_trend is not None
    assert current_trend["income"] == 5000
    assert current_trend["expense"] == 1500

    # 7. Test /daily
    daily_res = client.get(f"/api/v1/analytics/daily?date={date_str}", headers=auth_headers)
    assert daily_res.status_code == 200
    daily_data = daily_res.json()
    assert len(daily_data) >= 1

    # 8. Test /merchants/top
    merchants_res = client.get(f"/api/v1/analytics/merchants/top?date={date_str}", headers=auth_headers)
    assert merchants_res.status_code == 200
    merchants_data = merchants_res.json()
    assert len(merchants_data) == 1
    assert merchants_data[0]["merchant"] == "Zomato"
    assert merchants_data[0]["amount"] == 1500

    # 9. Test /cashflow
    cashflow_res = client.get(f"/api/v1/analytics/cashflow?date={date_str}", headers=auth_headers)
    assert cashflow_res.status_code == 200
    cashflow_data = cashflow_res.json()
    assert len(cashflow_data) >= 28

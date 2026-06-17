from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, transactions, sms, statements, budgets, analytics

app = FastAPI(
    title="Fynlo API",
    description="Backend API for Fynlo UPI expense tracking app",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(sms.router)
app.include_router(statements.router)
app.include_router(budgets.router)
app.include_router(analytics.router)

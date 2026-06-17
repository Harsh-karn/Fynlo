from celery import Celery
from app.config import settings
from app.database import SessionLocal
from app.models.statement import Statement, StatementStatus
from app.models.transaction import Transaction
from app.services.pdf_parser import PDFParserService
from app.services.ai_categorizer import AICategorizerService
import base64

celery_app = Celery(
    "flowmoney_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task
def send_budget_alert_email(email: str, category: str, usage_percent: float):
    print(f"Simulating sending budget alert email to {email} for category {category}. Usage: {usage_percent}%")
    return True

@celery_app.task
def process_statement_task(statement_id_str: str, file_b64: str, user_id_str: str, bank_name: str = None):
    db = SessionLocal()
    try:
        statement = db.query(Statement).filter(Statement.id == statement_id_str).first()
        if not statement:
            return
            
        statement.status = StatementStatus.processing
        db.commit()
        
        # Decode PDF bytes
        file_bytes = base64.b64decode(file_b64)
        
        # 1. Parse PDF
        raw_txs = PDFParserService.parse_pdf(file_bytes, bank_name)
        
        if not raw_txs:
            statement.status = StatementStatus.completed
            statement.transactions_extracted = 0
            db.commit()
            return
            
        # 2. Categorize in Batches of 20
        inserted_count = 0
        BATCH_SIZE = 20
        
        for i in range(0, len(raw_txs), BATCH_SIZE):
            batch = raw_txs[i:i+BATCH_SIZE]
            
            # Format for categorizer
            cat_input = []
            for tx in batch:
                cat_input.append({
                    "description": tx["description"],
                    "merchant_or_upi": tx.get("merchant_name") or tx.get("upi_id") or "",
                    "amount": tx["amount"],
                    "debit_or_credit": tx["type"]
                })
                
            categories = AICategorizerService.categorize_transaction_batch(cat_input)
            
            for j, tx_data in enumerate(batch):
                cat_data = categories[j] if j < len(categories) else {}
                
                # Check duplicate by reference id
                if tx_data.get("reference_id"):
                    exists = db.query(Transaction).filter(
                        Transaction.user_id == user_id_str,
                        Transaction.reference_id == tx_data["reference_id"]
                    ).first()
                    if exists:
                        continue
                        
                new_tx = Transaction(
                    user_id=user_id_str,
                    amount=tx_data["amount"],
                    type=tx_data["type"],
                    category=cat_data.get("category", "other"),
                    sub_category=cat_data.get("sub_category"),
                    merchant_name=cat_data.get("merchant_normalized"),
                    description=tx_data["description"],
                    reference_id=tx_data.get("reference_id"),
                    source="pdf_upload",
                    transaction_date=tx_data["transaction_date"]
                )
                db.add(new_tx)
                inserted_count += 1
                
        statement.transactions_extracted = inserted_count
        statement.status = StatementStatus.completed
        db.commit()
        
    except Exception as e:
        print(f"Error in process_statement_task: {e}")
        statement = db.query(Statement).filter(Statement.id == statement_id_str).first()
        if statement:
            statement.status = StatementStatus.failed
            db.commit()
    finally:
        db.close()

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import os

from app.database import get_db
from app.models.user import User
from app.models.statement import Statement, StatementStatus
from app.models.transaction import Transaction
from app.schemas.statement import StatementResponse, StatementListResponse
from app.schemas.transaction import TransactionResponse
from app.utils.dependencies import get_current_user


# In a real app, this would use Celery. 
# For now, we'll use FastAPI BackgroundTasks for simplicity and demonstration,
# and later refactor to Celery tasks in Phase 3.
from app.services.pdf_parser import PDFParserService
from app.services.ai_categorizer import AICategorizerService
from app.workers.tasks import process_statement_task
import base64

router = APIRouter(prefix="/api/v1/statements", tags=["statements"])

@router.post("/upload", response_model=StatementResponse, status_code=status.HTTP_201_CREATED)
async def upload_statement(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate MIME type
    ALLOWED_MIME_TYPES = ["application/pdf", "text/csv", "application/csv", "text/comma-separated-values"]
    if file.content_type not in ALLOWED_MIME_TYPES and not (file.filename.endswith('.pdf') or file.filename.endswith('.csv')):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF and CSV files are supported")
        
    file_bytes = await file.read()
    
    # Enforce file size limit (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024 # 10MB
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum limit of 10MB"
        )
    
    # In production, upload file to Cloudinary/S3 and get URL.
    # For now, we mock the URL.
    file_url = f"mock://{file.filename}"
    
    statement = Statement(
        user_id=current_user.id,
        file_name=file.filename,
        file_url=file_url,
        status=StatementStatus.pending
    )
    db.add(statement)
    db.commit()
    db.refresh(statement)
    
    # Process in background with Celery
    file_b64 = base64.b64encode(file_bytes).decode('utf-8')
    process_statement_task.delay(str(statement.id), file_b64, str(current_user.id), statement.bank_name)
    
    return statement

@router.get("/", response_model=StatementListResponse)
def get_statements(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Statement).filter(Statement.user_id == current_user.id)
    total = query.count()
    items = query.order_by(Statement.uploaded_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/{statement_id}/status", response_model=StatementResponse)
def get_statement_status(
    statement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    statement = db.query(Statement).filter(Statement.id == statement_id, Statement.user_id == current_user.id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    return statement

@router.delete("/{statement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_statement(
    statement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    statement = db.query(Statement).filter(Statement.id == statement_id, Statement.user_id == current_user.id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
        
    db.delete(statement)
    db.commit()
    return None

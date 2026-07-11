import pytest
from unittest.mock import patch, MagicMock
from app.workers.tasks import process_statement_task, send_budget_alert_email
from app.models.statement import Statement, StatementStatus
from app.models.transaction import Transaction
from celery.exceptions import Retry

def test_send_budget_alert_email_success():
    res = send_budget_alert_email.apply(args=["test@example.com", "food", 85.0])
    assert res.result is True

@patch("app.workers.tasks.SessionLocal")
def test_process_statement_task_statement_not_found(mock_session_class):
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.return_value = None

    process_statement_task("non-existent-id", "aGVsbG8=", "user-id")
    
    mock_session.commit.assert_not_called()

@patch("app.workers.tasks.SessionLocal")
@patch("app.workers.tasks.PDFParserService.parse_pdf")
def test_process_statement_task_empty_pdf(mock_parse_pdf, mock_session_class):
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session
    
    statement = Statement(id="stmt-123", status=StatementStatus.pending)
    
    def query_side_effect(model):
        q = MagicMock()
        if model == Statement:
            q.filter.return_value.first.return_value = statement
        else:
            q.filter.return_value.first.return_value = None
        return q
    mock_session.query.side_effect = query_side_effect
    
    mock_parse_pdf.return_value = []

    process_statement_task("stmt-123", "aGVsbG8=", "user-id")
    
    assert statement.status == StatementStatus.completed
    assert statement.transactions_extracted == 0
    mock_session.commit.assert_called()

@patch("app.workers.tasks.SessionLocal")
@patch("app.workers.tasks.PDFParserService.parse_pdf")
@patch("app.workers.tasks.AICategorizerService.categorize_transaction_batch")
def test_process_statement_task_success(mock_categorize, mock_parse_pdf, mock_session_class):
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session
    
    statement = Statement(id="stmt-123", status=StatementStatus.pending)
    
    def query_side_effect(model):
        q = MagicMock()
        if model == Statement:
            q.filter.return_value.first.return_value = statement
        else:
            q.filter.return_value.first.return_value = None
        return q
    mock_session.query.side_effect = query_side_effect
    
    mock_parse_pdf.return_value = [
        {
            "description": "UPI-ZOMATO-123",
            "amount": 250.0,
            "type": "debit",
            "transaction_date": "2026-07-11T12:00:00",
            "reference_id": "ref123"
        }
    ]
    mock_categorize.return_value = [
        {
            "category": "food",
            "sub_category": "restaurant",
            "merchant_normalized": "Zomato"
        }
    ]

    process_statement_task("stmt-123", "aGVsbG8=", "user-id")
    
    assert statement.status == StatementStatus.completed
    assert statement.transactions_extracted == 1
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called()

@patch("app.workers.tasks.SessionLocal")
@patch("app.workers.tasks.PDFParserService.parse_pdf")
@patch("app.workers.tasks.send_to_dead_letter_queue")
def test_process_statement_task_non_retryable_error(mock_dlq, mock_parse_pdf, mock_session_class):
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session
    
    statement = Statement(id="stmt-123", status=StatementStatus.pending)
    mock_session.query.return_value.filter.return_value.first.return_value = statement
    
    mock_parse_pdf.side_effect = ValueError("Invalid PDF format")

    process_statement_task("stmt-123", "aGVsbG8=", "user-id")
    
    assert statement.status == StatementStatus.failed
    mock_session.commit.assert_called()
    mock_dlq.assert_called_once()

@patch("app.workers.tasks.SessionLocal")
@patch("app.workers.tasks.PDFParserService.parse_pdf")
@patch("app.workers.tasks.send_to_dead_letter_queue")
def test_process_statement_task_retry_and_dlq_on_failure(mock_dlq, mock_parse_pdf, mock_session_class):
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session
    
    statement = Statement(id="stmt-123", status=StatementStatus.pending)
    mock_session.query.return_value.filter.return_value.first.return_value = statement
    
    mock_parse_pdf.side_effect = Exception("Transient connection timeout")

    with patch("app.workers.tasks.process_statement_task.retry") as mock_retry:
        mock_retry.side_effect = Retry("Retry task", exc=mock_parse_pdf.side_effect)
        
        with pytest.raises(Retry):
            process_statement_task("stmt-123", "aGVsbG8=", "user-id")
            
        mock_retry.assert_called_once()
        mock_dlq.assert_not_called()

from datetime import datetime
from app.services.sms_parser import SMSParserService
from app.models.transaction import TransactionType

def test_sbi_debit_parsing():
    raw_sms = "INR 500.00 debited from A/c XX1234 on 15-01-25 to VPA zomato@okaxis Ref No 123456789. Call 18001234 for dispute."
    received_at = datetime(2026, 7, 11, 20, 0, 0)
    result = SMSParserService.parse_sms(raw_sms, received_at)
    
    assert result is not None
    assert result["is_upi_transaction"] is True
    assert result["amount"] == 50000  # ₹500.00 -> 50000 paise
    assert result["type"] == TransactionType.debit
    assert result["upi_id"] == "zomato@okaxis"
    assert result["merchant_name"] == "zomato@okaxis"
    assert result["reference_id"] == "123456789"
    assert result["transaction_date"] == datetime(2025, 1, 15, 0, 0, 0)

def test_sbi_credit_parsing():
    raw_sms = "Rs.5000.00 credited to A/c XX1234 on 15/01/2025 from VPA rahul@okaxis Ref No 11223344"
    received_at = datetime(2026, 7, 11, 20, 0, 0)
    result = SMSParserService.parse_sms(raw_sms, received_at)
    
    assert result is not None
    assert result["amount"] == 500000  # ₹5000.00 -> 500000 paise
    assert result["type"] == TransactionType.credit
    assert result["upi_id"] == "rahul@okaxis"
    assert result["reference_id"] == "11223344"
    assert result["transaction_date"] == datetime(2025, 1, 15, 0, 0, 0)

def test_hdfc_debit_parsing():
    raw_sms = "Rs.250 Paid to SWIGGY via UPI. UPI Ref:987654321. If not done by you call 1800XXXX"
    received_at = datetime(2026, 7, 11, 20, 0, 0)
    result = SMSParserService.parse_sms(raw_sms, received_at)
    
    assert result is not None
    assert result["amount"] == 25000
    assert result["type"] == TransactionType.debit
    assert result["merchant_name"] == "SWIGGY"
    assert result["reference_id"] == "987654321"

def test_icici_parsing():
    raw_sms = "Your a/c XXXX1234 is credited with INR 5000.00 on 15/01/2025 by UPI-IMPS from Rahul Kumar Ref 112233445566"
    received_at = datetime(2026, 7, 11, 20, 0, 0)
    result = SMSParserService.parse_sms(raw_sms, received_at)
    
    assert result is not None
    assert result["amount"] == 500000
    assert result["type"] == TransactionType.credit
    assert result["merchant_name"] == "Rahul Kumar"
    assert result["reference_id"] == "112233445566"
    assert result["transaction_date"] == datetime(2025, 1, 15, 0, 0, 0)

def test_phonepe_parsing():
    raw_sms = "PhonePe: Rs 1200.00 sent to Flipkart. UPI Ref: 123456789012"
    received_at = datetime(2026, 7, 11, 20, 0, 0)
    result = SMSParserService.parse_sms(raw_sms, received_at)
    
    assert result is not None
    assert result["amount"] == 120000
    assert result["type"] == TransactionType.debit
    assert result["merchant_name"] == "Flipkart"
    assert result["reference_id"] == "123456789012"

def test_gpay_parsing():
    raw_sms = "GPay: Payment of Rs.450 to Ola successfully processed. Ref: 9876543210"
    received_at = datetime(2026, 7, 11, 20, 0, 0)
    result = SMSParserService.parse_sms(raw_sms, received_at)
    
    assert result is not None
    assert result["amount"] == 45000
    assert result["type"] == TransactionType.debit
    assert result["merchant_name"] == "Ola"
    assert result["reference_id"] == "9876543210"

def test_paytm_parsing():
    raw_sms = "Paytm: Sent Rs. 150 to Zomato. Ref: 123456789"
    received_at = datetime(2026, 7, 11, 20, 0, 0)
    result = SMSParserService.parse_sms(raw_sms, received_at)
    
    assert result is not None
    assert result["amount"] == 15000
    assert result["type"] == TransactionType.debit
    assert result["merchant_name"] == "Zomato"
    assert result["reference_id"] == "123456789"

def test_generic_fallback_parsing():
    raw_sms = "Paid ₹300 on ticket booking at Movie counter via Net banking Ref ID: tx1002"
    received_at = datetime(2026, 7, 11, 20, 0, 0)
    result = SMSParserService.parse_sms(raw_sms, received_at)
    
    assert result is not None
    assert result["amount"] == 30000
    assert result["type"] == TransactionType.debit
    assert result["reference_id"] == "tx1002"

def test_non_financial_sms_returns_none():
    raw_sms = "Hey, what are you doing tonight? Let's catch up!"
    received_at = datetime(2026, 7, 11, 20, 0, 0)
    result = SMSParserService.parse_sms(raw_sms, received_at)
    
    assert result is None

import re
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.transaction import TransactionType

class SMSParserService:
    # 1. SBI Patterns
    # Debit: "INR 500.00 debited from A/c XX1234 on 15-01-25 to VPA zomato@okaxis Ref No 123456789. Call 18001234 for dispute."
    # Credit: "Rs.5000.00 credited to A/c XX1234 on 15/01/2025 from VPA rahul@okaxis Ref No 11223344"
    SBI_DEBIT = re.compile(
        r'(?i)(?:inr|rs\.?|₹)\s*([\d,]+\.?\d*)\s+debited\s+from\s+A/c\s+(?:XX|X+)\d+\s+on\s+([\d\-:\s/]+)\s+to\s+(?:VPA\s+)?([a-zA-Z0-9.\-_&@]+)(?:\s+Ref\s+(?:No|No\.)?\s*(\d+))?'
    )
    SBI_CREDIT = re.compile(
        r'(?i)(?:inr|rs\.?|₹)\s*([\d,]+\.?\d*)\s+credited\s+to\s+A/c\s+(?:XX|X+)\d+\s+on\s+([\d\-:\s/]+)\s+from\s+(?:VPA\s+)?([a-zA-Z0-9.\-_&@]+)(?:\s+Ref\s+(?:No|No\.)?\s*(\d+))?'
    )

    # 2. HDFC Patterns
    # Debit: "Rs.250 Paid to SWIGGY via UPI. UPI Ref:987654321. If not done by you call 1800XXXX"
    # Credit: "INR 1000.00 credited to A/c XX1234 via UPI. UPI Ref:123456789012"
    HDFC_DEBIT = re.compile(
        r'(?i)(?:inr|rs\.?|₹)\s*([\d,]+\.?\d*)\s+Paid\s+to\s+([a-zA-Z0-9\s.\-_&@]+?)\s+via\s+UPI\.\s+UPI\s+Ref:?\s*(\d+)'
    )
    HDFC_CREDIT = re.compile(
        r'(?i)(?:inr|rs\.?|₹)\s*([\d,]+\.?\d*)\s+credited\s+to\s+A/c\s+(?:XX|X+)\d+\s+via\s+UPI\.\s+UPI\s+Ref:?\s*(\d+)'
    )

    # 3. ICICI Patterns
    # "Your a/c XXXX1234 is credited with INR 5000.00 on 15/01/2025 by UPI-IMPS from Rahul Kumar Ref 112233445566"
    # "Your a/c XXXX1234 is debited with INR 250.00 on 15/01/2025 by UPI to Swiggy Ref 112233445566"
    ICICI_PAT = re.compile(
        r'(?i)(?:Your\s+a/c|A/c)\s+(?:XX|X+)?\d+\s+is\s+(debited|credited)\s+with\s+(?:inr|rs\.?|₹)\s*([\d,]+\.?\d*)\s+on\s+([\d\-:\s/]+)\s+by\s+UPI(?:-IMPS)?\s+(?:from|to)\s+([a-zA-Z0-9\s.\-_&@]+?)(?=\s+Ref\s+|\s*$|\.)(?:\s+Ref\s+(\d+))?'
    )

    # 4. Axis Patterns
    # "Rs. 100.00 debited from Axis Bank A/c XX1234 to VPA test@okaxis on 15-01-25. Ref: 123456"
    AXIS_DEBIT = re.compile(
        r'(?i)(?:inr|rs\.?|₹)\s*([\d,]+\.?\d*)\s+debited\s+from\s+Axis\s+Bank\s+A/c\s+(?:XX|X+)\d+\s+to\s+(?:VPA\s+)?([a-zA-Z0-9.\-_&@]+)\s+on\s+([\d\-:\s/]+)\.\s+Ref:?\s*([0-9a-zA-Z]+)'
    )
    AXIS_CREDIT = re.compile(
        r'(?i)(?:inr|rs\.?|₹)\s*([\d,]+\.?\d*)\s+credited\s+to\s+Axis\s+Bank\s+A/c\s+(?:XX|X+)\d+\s+from\s+(?:VPA\s+)?([a-zA-Z0-9.\-_&@]+)\s+on\s+([\d\-:\s/]+)\.\s+Ref:?\s*([0-9a-zA-Z]+)'
    )

    # 5. Kotak Patterns
    # "Rs. 200.00 debited from Kotak Bank A/c XX1234 to UPI VPA test@okaxis on 15-01-25. Ref No: 123456"
    KOTAK_DEBIT = re.compile(
        r'(?i)(?:inr|rs\.?|₹)\s*([\d,]+\.?\d*)\s+debited\s+from\s+Kotak\s+Bank\s+A/c\s+(?:XX|X+)\d+\s+to\s+(?:UPI\s+)?VPA\s+([a-zA-Z0-9.\-_&@]+)\s+on\s+([\d\-:\s/]+)\.\s+Ref\s+No:?\s*([0-9a-zA-Z]+)'
    )
    KOTAK_CREDIT = re.compile(
        r'(?i)(?:inr|rs\.?|₹)\s*([\d,]+\.?\d*)\s+credited\s+to\s+Kotak\s+Bank\s+A/c\s+(?:XX|X+)\d+\s+from\s+VPA\s+([a-zA-Z0-9.\-_&@]+)\s+on\s+([\d\-:\s/]+)\.\s+Ref\s+No:?\s*([0-9a-zA-Z]+)'
    )

    # 6. PhonePe Patterns
    # "PhonePe: Rs 1200.00 sent to Flipkart. UPI Ref: 123456789012"
    PHONEPE_DEBIT = re.compile(
        r'(?i)PhonePe:\s+(?:inr|rs\.?|₹)\s*([\d,]+\.?\d*)\s+(?:sent\s+to|paid\s+to)\s+([a-zA-Z0-9\s.\-_&@]+?)\.\s+UPI\s+Ref:\s*([0-9a-zA-Z]+)'
    )

    # 7. GPay Patterns
    # "GPay: Payment of Rs.450 to Ola successfully processed. Ref: 9876543210"
    GPAY_DEBIT = re.compile(
        r'(?i)GPay:\s+Payment\s+of\s+(?:inr|rs\.?|₹)\s*([\d,]+\.?\d*)\s+to\s+([a-zA-Z0-9\s.\-_&@]+?)\s+successfully\s+processed\.\s+Ref:\s*([0-9a-zA-Z]+)'
    )

    # 8. Paytm Patterns
    # "Paytm: Sent Rs. 150 to Zomato. Ref: 123456789"
    PAYTM_DEBIT = re.compile(
        r'(?i)Paytm:\s+Sent\s+(?:inr|rs\.?|₹)\s*([\d,]+\.?\d*)\s+to\s+([a-zA-Z0-9\s.\-_&@]+?)\.\s+Ref:\s*([0-9a-zA-Z]+)'
    )

    # 9. Generic Patterns (Fallback)
    AMOUNT_PATTERN = re.compile(r'(?i)(?:rs\.?|inr|₹)\s*([\d,]+\.?\d*)')
    DEBIT_KEYWORDS = ["debited", "sent", "paid", "payment of", "deducted", "withdrawal"]
    CREDIT_KEYWORDS = ["credited", "received", "added", "deposited"]
    UPI_ID_PATTERN = re.compile(r'([a-zA-Z0-9.\-_]+@[a-zA-Z]+)')
    REF_ID_PATTERN = re.compile(r'(?i)(?:ref\s+id|ref\s+no|upi\s+ref|ref|transaction\s+id|txn\s+id)[:\s]*([0-9a-zA-Z]+)')
    MERCHANT_TO_PATTERN = re.compile(r'(?i)to\s+([a-zA-Z0-9\s.\-_&@]+?)(?=\s+(?:via|upi|ref|on|\.|$))')
    MERCHANT_AT_PATTERN = re.compile(r'(?i)at\s+([a-zA-Z0-9\s.\-_&@]+?)(?=\s+(?:via|upi|ref|on|\.|$))')
    MERCHANT_FROM_PATTERN = re.compile(r'(?i)from\s+([a-zA-Z0-9\s.\-_&@]+?)(?=\s+(?:via|upi|ref|on|\.|$))')

    @staticmethod
    def clean_amount(amount_str: str) -> Optional[int]:
        try:
            return int(float(amount_str.replace(',', '')) * 100)
        except ValueError:
            return None

    @staticmethod
    def parse_date(date_str: str, received_at: datetime) -> datetime:
        cleaned = date_str.strip()
        for fmt in ('%d-%m-%y', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d-%b-%y', '%d-%b-%Y'):
            try:
                return datetime.strptime(cleaned, fmt)
            except ValueError:
                continue
        return received_at

    @classmethod
    def parse_sms(cls, raw_sms: str, received_at: datetime) -> Optional[Dict[str, Any]]:
        raw_sms_lower = raw_sms.lower()

        # 1. Check SBI patterns
        sbi_debit_match = cls.SBI_DEBIT.search(raw_sms)
        if sbi_debit_match:
            amount = cls.clean_amount(sbi_debit_match.group(1))
            if amount:
                return {
                    "is_upi_transaction": True,
                    "amount": amount,
                    "type": TransactionType.debit,
                    "merchant_name": sbi_debit_match.group(3).strip(),
                    "upi_id": sbi_debit_match.group(3).strip() if "@" in sbi_debit_match.group(3) else None,
                    "reference_id": sbi_debit_match.group(4) if sbi_debit_match.group(4) else None,
                    "transaction_date": cls.parse_date(sbi_debit_match.group(2), received_at),
                    "raw_sms": raw_sms,
                    "confidence": 0.95
                }

        sbi_credit_match = cls.SBI_CREDIT.search(raw_sms)
        if sbi_credit_match:
            amount = cls.clean_amount(sbi_credit_match.group(1))
            if amount:
                return {
                    "is_upi_transaction": True,
                    "amount": amount,
                    "type": TransactionType.credit,
                    "merchant_name": sbi_credit_match.group(3).strip(),
                    "upi_id": sbi_credit_match.group(3).strip() if "@" in sbi_credit_match.group(3) else None,
                    "reference_id": sbi_credit_match.group(4) if sbi_credit_match.group(4) else None,
                    "transaction_date": cls.parse_date(sbi_credit_match.group(2), received_at),
                    "raw_sms": raw_sms,
                    "confidence": 0.95
                }

        # 2. Check HDFC patterns
        hdfc_debit_match = cls.HDFC_DEBIT.search(raw_sms)
        if hdfc_debit_match:
            amount = cls.clean_amount(hdfc_debit_match.group(1))
            if amount:
                return {
                    "is_upi_transaction": True,
                    "amount": amount,
                    "type": TransactionType.debit,
                    "merchant_name": hdfc_debit_match.group(2).strip(),
                    "upi_id": hdfc_debit_match.group(2).strip() if "@" in hdfc_debit_match.group(2) else None,
                    "reference_id": hdfc_debit_match.group(3),
                    "transaction_date": received_at,
                    "raw_sms": raw_sms,
                    "confidence": 0.95
                }

        hdfc_credit_match = cls.HDFC_CREDIT.search(raw_sms)
        if hdfc_credit_match:
            amount = cls.clean_amount(hdfc_credit_match.group(1))
            if amount:
                return {
                    "is_upi_transaction": True,
                    "amount": amount,
                    "type": TransactionType.credit,
                    "merchant_name": "Bank Deposit / UPI",
                    "upi_id": None,
                    "reference_id": hdfc_credit_match.group(2),
                    "transaction_date": received_at,
                    "raw_sms": raw_sms,
                    "confidence": 0.9
                }

        # 3. Check ICICI patterns
        icici_match = cls.ICICI_PAT.search(raw_sms)
        if icici_match:
            amount = cls.clean_amount(icici_match.group(2))
            if amount:
                txn_type = TransactionType.debit if icici_match.group(1).lower() == "debited" else TransactionType.credit
                return {
                    "is_upi_transaction": True,
                    "amount": amount,
                    "type": txn_type,
                    "merchant_name": icici_match.group(4).strip(),
                    "upi_id": icici_match.group(4).strip() if "@" in icici_match.group(4) else None,
                    "reference_id": icici_match.group(5) if icici_match.group(5) else None,
                    "transaction_date": cls.parse_date(icici_match.group(3), received_at),
                    "raw_sms": raw_sms,
                    "confidence": 0.95
                }

        # 4. Check Axis patterns
        axis_debit_match = cls.AXIS_DEBIT.search(raw_sms)
        if axis_debit_match:
            amount = cls.clean_amount(axis_debit_match.group(1))
            if amount:
                return {
                    "is_upi_transaction": True,
                    "amount": amount,
                    "type": TransactionType.debit,
                    "merchant_name": axis_debit_match.group(2).strip(),
                    "upi_id": axis_debit_match.group(2).strip() if "@" in axis_debit_match.group(2) else None,
                    "reference_id": axis_debit_match.group(4),
                    "transaction_date": cls.parse_date(axis_debit_match.group(3), received_at),
                    "raw_sms": raw_sms,
                    "confidence": 0.95
                }

        axis_credit_match = cls.AXIS_CREDIT.search(raw_sms)
        if axis_credit_match:
            amount = cls.clean_amount(axis_credit_match.group(1))
            if amount:
                return {
                    "is_upi_transaction": True,
                    "amount": amount,
                    "type": TransactionType.credit,
                    "merchant_name": axis_credit_match.group(2).strip(),
                    "upi_id": axis_credit_match.group(2).strip() if "@" in axis_credit_match.group(2) else None,
                    "reference_id": axis_credit_match.group(4),
                    "transaction_date": cls.parse_date(axis_credit_match.group(3), received_at),
                    "raw_sms": raw_sms,
                    "confidence": 0.95
                }

        # 5. Check Kotak patterns
        kotak_debit_match = cls.KOTAK_DEBIT.search(raw_sms)
        if kotak_debit_match:
            amount = cls.clean_amount(kotak_debit_match.group(1))
            if amount:
                return {
                    "is_upi_transaction": True,
                    "amount": amount,
                    "type": TransactionType.debit,
                    "merchant_name": kotak_debit_match.group(2).strip(),
                    "upi_id": kotak_debit_match.group(2).strip() if "@" in kotak_debit_match.group(2) else None,
                    "reference_id": kotak_debit_match.group(4),
                    "transaction_date": cls.parse_date(kotak_debit_match.group(3), received_at),
                    "raw_sms": raw_sms,
                    "confidence": 0.95
                }

        kotak_credit_match = cls.KOTAK_CREDIT.search(raw_sms)
        if kotak_credit_match:
            amount = cls.clean_amount(kotak_credit_match.group(1))
            if amount:
                return {
                    "is_upi_transaction": True,
                    "amount": amount,
                    "type": TransactionType.credit,
                    "merchant_name": kotak_credit_match.group(2).strip(),
                    "upi_id": kotak_credit_match.group(2).strip() if "@" in kotak_credit_match.group(2) else None,
                    "reference_id": kotak_credit_match.group(4),
                    "transaction_date": cls.parse_date(kotak_credit_match.group(3), received_at),
                    "raw_sms": raw_sms,
                    "confidence": 0.95
                }

        # 6. Check PhonePe patterns
        phonepe_match = cls.PHONEPE_DEBIT.search(raw_sms)
        if phonepe_match:
            amount = cls.clean_amount(phonepe_match.group(1))
            if amount:
                return {
                    "is_upi_transaction": True,
                    "amount": amount,
                    "type": TransactionType.debit,
                    "merchant_name": phonepe_match.group(2).strip(),
                    "upi_id": phonepe_match.group(2).strip() if "@" in phonepe_match.group(2) else None,
                    "reference_id": phonepe_match.group(3),
                    "transaction_date": received_at,
                    "raw_sms": raw_sms,
                    "confidence": 0.95
                }

        # 7. Check GPay patterns
        gpay_match = cls.GPAY_DEBIT.search(raw_sms)
        if gpay_match:
            amount = cls.clean_amount(gpay_match.group(1))
            if amount:
                return {
                    "is_upi_transaction": True,
                    "amount": amount,
                    "type": TransactionType.debit,
                    "merchant_name": gpay_match.group(2).strip(),
                    "upi_id": gpay_match.group(2).strip() if "@" in gpay_match.group(2) else None,
                    "reference_id": gpay_match.group(3),
                    "transaction_date": received_at,
                    "raw_sms": raw_sms,
                    "confidence": 0.95
                }

        # 8. Check Paytm patterns
        paytm_match = cls.PAYTM_DEBIT.search(raw_sms)
        if paytm_match:
            amount = cls.clean_amount(paytm_match.group(1))
            if amount:
                return {
                    "is_upi_transaction": True,
                    "amount": amount,
                    "type": TransactionType.debit,
                    "merchant_name": paytm_match.group(2).strip(),
                    "upi_id": paytm_match.group(2).strip() if "@" in paytm_match.group(2) else None,
                    "reference_id": paytm_match.group(3),
                    "transaction_date": received_at,
                    "raw_sms": raw_sms,
                    "confidence": 0.95
                }

        # 9. Generic Fallback Parser
        txn_type = None
        if any(kw in raw_sms_lower for kw in cls.DEBIT_KEYWORDS):
            txn_type = TransactionType.debit
        elif any(kw in raw_sms_lower for kw in cls.CREDIT_KEYWORDS):
            txn_type = TransactionType.credit

        if not txn_type:
            return None  # Not a clear financial transaction

        amount_match = cls.AMOUNT_PATTERN.search(raw_sms)
        if not amount_match:
            return None

        amount = cls.clean_amount(amount_match.group(1))
        if not amount:
            return None

        upi_id_match = cls.UPI_ID_PATTERN.search(raw_sms)
        upi_id = upi_id_match.group(1) if upi_id_match else None

        ref_id_match = cls.REF_ID_PATTERN.search(raw_sms)
        ref_id = ref_id_match.group(1) if ref_id_match else None

        merchant_name = None
        if txn_type == TransactionType.debit:
            merchant_match = cls.MERCHANT_TO_PATTERN.search(raw_sms) or cls.MERCHANT_AT_PATTERN.search(raw_sms)
            if merchant_match:
                merchant_name = merchant_match.group(1).strip()
        else:
            merchant_match = cls.MERCHANT_FROM_PATTERN.search(raw_sms)
            if merchant_match:
                merchant_name = merchant_match.group(1).strip()

        confidence = 0.5
        if amount > 0:
            confidence += 0.1
        if upi_id or ref_id:
            confidence += 0.2
        if merchant_name:
            confidence += 0.1

        return {
            "is_upi_transaction": True,
            "amount": amount,
            "type": txn_type,
            "merchant_name": merchant_name if merchant_name else ("UPI Transfer" if upi_id else "Transaction"),
            "upi_id": upi_id,
            "reference_id": ref_id,
            "transaction_date": received_at,
            "raw_sms": raw_sms,
            "confidence": min(0.9, confidence)
        }

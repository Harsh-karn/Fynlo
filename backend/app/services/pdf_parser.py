import pdfplumber
import io
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from decimal import Decimal


class PDFParserService:
    # A simplified version of what a real production parser would look like.
    # In a real app, we'd have robust strategies per bank.

    @classmethod
    def parse_pdf(cls, file_bytes: bytes, bank_name: Optional[str] = None) -> List[Dict[str, Any]]:
        transactions = []
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    # Extract tables from the page
                    table = page.extract_table()
                    if not table:
                        continue
                        
                    for row in table:
                        # Skip header rows or empty rows
                        if not row or not row[0]:
                            continue
                            
                        # Basic heuristic: if the first column looks like a date
                        date_str = str(row[0]).strip()
                        if re.match(r'\d{2}[-/]\d{2}[-/]\d{2,4}', date_str):
                            tx = cls._parse_row(row, bank_name)
                            if tx:
                                transactions.append(tx)
        except Exception as e:
            print(f"Failed to parse PDF: {e}")
            pass

        return transactions

    @classmethod
    def _parse_row(cls, row: List[Any], bank_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        # Extremely simplified generic row parser
        # Expecting something like: [Date, Description, Ref No, Debit, Credit, Balance]
        try:
            date_str = str(row[0]).strip()
            desc = str(row[1]).strip() if len(row) > 1 else ""
            ref = str(row[2]).strip() if len(row) > 2 else ""
            
            debit_str = str(row[3]).strip() if len(row) > 3 else ""
            credit_str = str(row[4]).strip() if len(row) > 4 else ""
            
            # Clean up amounts
            debit_str = re.sub(r'[^\d.]', '', debit_str)
            credit_str = re.sub(r'[^\d.]', '', credit_str)
            
            amount_val = Decimal("0.00")
            txn_type = None
            
            if debit_str and debit_str != "0" and debit_str != "0.00":
                amount_val = Decimal(debit_str)
                txn_type = "debit"
            elif credit_str and credit_str != "0" and credit_str != "0.00":
                amount_val = Decimal(credit_str)
                txn_type = "credit"
                
            if not txn_type:
                return None
                
            # Parse date (assuming DD/MM/YYYY or DD-MM-YYYY)
            date_str = date_str.replace('-', '/')
            try:
                txn_date = datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                try:
                    txn_date = datetime.strptime(date_str, "%d/%m/%y")
                except ValueError:
                    txn_date = datetime.utcnow() # Fallback

            return {
                "transaction_date": txn_date,
                "description": desc,
                "reference_id": ref if ref else None,
                "amount": amount_val,
                "type": txn_type,
                "merchant_name": None, # Will be determined by AI Categorizer
                "upi_id": None
            }
        except Exception:
            return None

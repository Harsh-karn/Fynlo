from decimal import Decimal
from typing import Dict, Any, List

class AICategorizerService:

    CATEGORY_KEYWORDS = {
        "food": ["zomato", "swiggy", "dominos", "mcdonalds", "kfc", "subway", "blinkit", "instamart", "zepto", "restaurant", "hotel", "dhaba", "cafe", "pizza"],
        "transport": ["ola", "uber", "rapido", "metro", "irctc", "redbus", "petrol", "fuel", "parking", "toll", "makemytrip", "ixigo", "indigo", "spicejet"],
        "shopping": ["amazon", "flipkart", "myntra", "ajio", "meesho", "nykaa", "reliance", "dmart", "bigbasket"],
        "utilities": ["electricity", "jio", "airtel", "vi", "bsnl", "water", "gas", "wifi", "broadband", "recharge"],
        "health": ["pharmacy", "apollo", "medplus", "practo", "1mg", "hospital", "clinic", "doctor", "lab", "test"],
        "entertainment": ["netflix", "spotify", "hotstar", "prime", "bookmyshow", "pvr", "inox", "youtube"],
        "education": ["udemy", "coursera", "byju", "unacademy", "leetcode", "college", "school", "tuition"]
    }

    @classmethod
    def keyword_categorize(cls, merchant_or_description: str) -> str:
        text = (merchant_or_description or "").lower()
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return category
        return "other"

    @classmethod
    async def categorize_transaction(
        cls, 
        description: str, 
        merchant_or_upi: str, 
        amount: Decimal, 
        debit_or_credit: str
    ) -> Dict[str, Any]:
        
        category = cls.keyword_categorize(merchant_or_upi or description)
        return {
            "category": category,
            "sub_category": None,
            "merchant_normalized": merchant_or_upi,
            "confidence": 0.8 if category != "other" else 0.3
        }

    @classmethod
    def categorize_transaction_batch(
        cls, 
        transactions: List[Dict[str, Any]],
        db = None,
        user_id = None
    ) -> List[Dict[str, Any]]:
        is_allowed = True
        if db and user_id:
            from app.services.ai_limiter import AILimiterService
            is_allowed, reason = AILimiterService.check_ai_allowance(db, user_id)
            
        results = []
        tokens_used = 0
        for tx in transactions:
            merchant_or_desc = tx.get('merchant_or_upi') or tx.get('description', '')
            
            if is_allowed:
                # FUTURE: LLM call goes here.
                # For now, simulate LLM integration and token usage
                tokens_used += 50
                category = cls.keyword_categorize(merchant_or_desc)
                confidence = 0.8 if category != "other" else 0.3
            else:
                # GRACEFUL DEGRADATION: Fallback to simple regex/keywords without LLM
                category = cls.keyword_categorize(merchant_or_desc)
                confidence = 0.4 if category != "other" else 0.1
                
            results.append({
                "category": category,
                "sub_category": None,
                "merchant_normalized": merchant_or_desc,
                "confidence": confidence
            })
            
        if is_allowed and db and user_id and tokens_used > 0:
            from app.services.ai_limiter import AILimiterService
            AILimiterService.track_ai_usage(db, user_id, tokens_used)
            
        return results

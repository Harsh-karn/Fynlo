# Fynlo Privacy Policy

**Effective Date:** [Insert Date]  
**Last Updated:** [Insert Date]  

This Privacy Policy explains how Fynlo ("we", "us", or "our") collects, uses, securely processes, and protects your personal and financial data. We are committed to safeguarding your privacy and ensuring compliance with the Digital Personal Data Protection (DPDP) Act, 2023 of India.

---

## 1. Information We Collect
We collect information to provide, improve, and secure our automated financial categorization services.

### A. Personal Data
When you register, we collect:
- Full Name
- Email Address
- Phone Number (Optional)
- Password (Stored as an encrypted, irreversible hash)

### B. Financial Data
To provide categorization and insights, we process:
- **Bank Statements:** PDF or CSV files uploaded directly by you.
- **Transaction SMS:** Data extracted locally from your device (if you opt-in to SMS sync).
*Note: Fynlo extracts transaction amounts, merchant names, dates, and categories. We DO NOT extract or store OTPs, personal messages, or full bank account numbers.*

---

## 2. How We Use Your Data (Purpose Limitation)
We strictly process your data only for the purposes you explicitly consent to:
- To automatically parse and categorize your financial transactions.
- To generate budget alerts, weekly/monthly spending summaries, and insights.
- To improve our categorization algorithms (using anonymized, stripped data only).

**Advertising and Data Sharing Policy**
Fynlo uses Google AdSense to serve advertisements, allowing us to keep the core service free. 
- Google AdSense may use cookies to serve ads based on your prior visits to Fynlo or other websites.
- Google's use of advertising cookies enables it and its partners to serve ads to you based on your browsing history.
- **Strict Data Isolation:** We DO NOT share, sell, or rent your personal financial data (bank statements, SMS texts, balances, transaction history) to Google, advertisers, or any third-party data brokers. Ads are served based on generalized demographic/browsing data, entirely separate from your Fynlo financial profile.

---

## 3. Explicit Consent (DPDP Compliance)
By using Fynlo, you are presented with a non-bypassable "Informed Consent" screen before we process any financial data. 
- You have the right to **withdraw this consent at any time**. 
- Withdrawing consent will pause our ability to parse new statements or SMS data.

---

## 4. Your Rights (DPDP Act, 2023)
Under the DPDP Act, you are the Data Principal and retain full ownership of your data. You have the right to:
1. **Right to Access:** You can view all your stored transactions and budgets on your dashboard.
2. **Right to Correction:** You can manually edit or re-categorize any transaction.
3. **Right to Data Portability:** You can download all your data (CSV/JSON) via the Settings page.
4. **Right to Erasure (Right to be Forgotten):** You can permanently delete your Fynlo account. Initiating account deletion will trigger a hard SQL cascade delete, permanently erasing your profile, statements, budgets, and transactions from our active databases.

---

## 5. AI and Third-Party Processing
- **AI Categorization:** Fynlo uses Large Language Models (LLMs) to categorize unknown merchants. When data is sent to an LLM provider, we strip PII (Personally Identifiable Information). We only send the raw merchant string and transaction amount.
- **Advertising (Google AdSense):** Third-party vendors, including Google, use cookies to serve ads. You may opt out of personalized advertising by visiting [Google Ads Settings](https://www.google.com/settings/ads).
- **Data Residency:** All data is encrypted at rest and in transit (TLS/SSL) and is stored on secure cloud servers located within [Insert Data Center Region, e.g., Mumbai, India] to comply with data localization preferences.

---

## 6. Data Security
We implement strict access controls and robust encryption:
- Passwords are hashed using bcrypt.
- JWT tokens are used for stateless authentication.
- Application-level rate limiting prevents brute-force scraping.

---

## 7. Contact the Data Protection Officer (DPO)
If you have any questions, grievances, or wish to exercise your rights under the DPDP Act, please contact our Grievance Officer:

**Name:** [Insert Name]  
**Email:** privacy@fynlo.com  
**Address:** [Insert Registered Address]  

*We will acknowledge your grievance within 24 hours and resolve it within 15 days.*

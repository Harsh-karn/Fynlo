# Fynlo Privacy Policy

**Last Updated:** July 11, 2026

Fynlo ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your personal and financial data when you use the Fynlo web application, companion Android application, and related services (collectively, the "Platform").

This policy has been updated to align with the **Digital Personal Data Protection (DPDP) Act, 2023** of India. By accessing or using the Platform, you consent to the collection and processing of your personal data in accordance with this Privacy Policy.

---

## 1. Data We Collect

As a financial management platform, we require specific data to categorize and track your transaction history automatically:

### A. Personal Identification & Profile Data
* Name, Email Address, and Phone Number.
* Local settings (e.g., currency preferences, monthly budget limit).

### B. Device-Synced SMS Data (Android App)
* **What we scan:** Our companion Android app scans incoming SMS messages locally.
* **Filter criteria:** The app only processes messages that match bank or merchant transactional templates (e.g., "debited," "credited," "sent," "received," "UPI Ref").
* **Transmitted data:** Only parsed transaction details (amount, transaction type, merchant VPA, reference ID, date, and bank name) are uploaded to our secure servers.
* **We do NOT read, scan, or upload** personal text messages, OTPs, password reset codes, or contact names.

### C. Uploaded Statement Data (PDF/CSV)
* Bank statement files uploaded voluntarily by you.
* Extractable text containing transaction history, date, amount, narration, and account balance.
* Uploaded statements are processed securely via our AI pipeline and saved to cloud storage with restricted access.

---

## 2. Purpose of Processing

We process your data strictly under the following DPDP Act grounds:
1. **Consent-Based Processing:** To compile your financial transactions into a single interactive dashboard.
2. **Service Fulfillment:** To auto-categorize your expenses (e.g., mapping Swiggy/Zomato to "Food") using AI/LLM models.
3. **Notifications:** To send budget crossing alerts and monthly summary reports.

---

## 3. Data Minimization & PII Protection

* **PII Stripping:** Before passing narration texts to LLMs/AI models for categorization, we automatically strip out potential PII (such as account numbers or user names).
* **Logs Security:** We enforce structured logging that explicitly excludes raw transaction narration payloads or account balances.

---

## 4. Your Rights under the DPDP Act 2023

As a Data Principal, you have the following rights:
* **Right to Access:** You can request a copy of the personal and financial data we store.
* **Right to Correction & Erasure:** You can correct inaccurate data or request complete deletion of your account and transaction history.
* **Right to Withdraw Consent:** You can withdraw your consent at any time. Upon withdrawal, we will cease processing and delete your stored records within 30 days.
* **Right to Grievance Redressal:** You can submit grievances regarding data processing directly to our Grievance Officer.

---

## 5. Account Deletion & Data Retention

If you choose to delete your account, we perform a **soft delete** for recovery options within 14 days, after which all database records (User metadata, Budgets, SMS devices, and Transactions) are permanently purged from our primary and backup databases.

---

## 6. Grievance Officer Contact

In compliance with the DPDP Act 2023, our Grievance Officer's contact details are:

* **Name:** Grievance Redressal Officer, Fynlo
* **Email:** support@fynlo.com
* **Address:** compliance/grievance, Fynlo Headquarters, India

# Legal Review Checklist for Fynlo (DPDP Act Compliance)

Hand this document alongside `PRIVACY_POLICY.md` to your legal team for comprehensive review.

## 1. Notice and Consent (Section 5 & 6)
- [ ] **Data Consent Screen:** Fynlo uses an active, non-bypassable full-screen overlay for users to provide explicit consent before we process statements or SMS. Does this meet the threshold for "clear, affirmative action" under the DPDP Act?
- [ ] **Notice Formulation:** Does the consent screen language accurately describe the specific purpose of data collection (categorization and insights)?
- [ ] **Withdrawal Mechanism:** Is the ability to revoke consent (by deleting the account or disabling integrations) sufficient and as easy as providing consent?

## 2. Right to Erasure / Data Portability (Section 11)
- [ ] **Hard Deletion Cascade:** When a user clicks "Delete Account" in Fynlo, we execute a hard SQL cascade delete, erasing the `User` row and all attached `Transactions`, `Statements`, and `Budgets`. Are there any taxation or legal retention requirements in India (e.g., keeping records for 7 years) that conflict with immediate erasure of financial data?
- [ ] **Data Export:** Users can download their raw transaction data as JSON or CSV. Does this adequately satisfy the "Right to Information about personal data" requirement?

## 3. Data Processing via Third-Party LLMs
- [ ] **Cross-Border Transfer:** When Fynlo sends a merchant string (e.g., "AMZN Prime") to an external LLM (like OpenAI/Anthropic API), is this legally permissible since PII (Personally Identifiable Information) like Account Numbers and Names are stripped out before transmission?
- [ ] **Data Processor Agreements:** Do we need a formalized Data Processing Agreement (DPA) with the LLM provider to restrict them from training on our merchant data strings?

## 4. SMS Parsing and Device Permissions
- [ ] **Scope of Collection:** Fynlo's SMS parser is designed to extract *only* financial transaction metadata (Amount, Merchant, Date) and ignore OTPs or personal texts. Does the privacy policy adequately disclose this mechanism?
- [ ] **Google Play / App Store Policies:** Beyond DPDP, does our privacy policy meet Google's strict requirements for apps requesting `READ_SMS` permissions?

## 5. Security Safeguards (Section 8)
- [ ] **Breach Notification:** What is the legal SLA for notifying the Data Protection Board of India and affected users in the event of a database breach? Should this SLA be explicitly stated in the policy?

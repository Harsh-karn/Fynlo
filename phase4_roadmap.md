# Fynlo Phase 4: Scale & Iterate

**Objective:** Grow with real data, optimize the core experience, and explore advanced integrations (Account Aggregators).
**Timeline:** Months 6-12

Welcome to Phase 4! The core product is live and generating revenue. The focus now shifts from building features to analyzing data, reducing churn, and scaling the infrastructure.

## Task Checklist

1. **Implement advanced retention & churn analytics**
   - **Category**: Analytics & Growth
   - **Priority**: High
   - **Status**: Not started
   - **Description**: Integrate PostHog or Amplitude to track user drop-off points in the onboarding flow and identify features that correlate with long-term retention.

2. **Establish user feedback loop and feature voting**
   - **Category**: Product Strategy
   - **Priority**: High
   - **Status**: Not started
   - **Description**: Add an in-app mechanism (e.g., Canny or simple Typeform) for paying users to request and vote on new features.

3. **Maturation of Merchant-Category Cache (ML Retraining Pipeline)**
   - **Category**: Machine Learning & Backend
   - **Priority**: Medium
   - **Status**: Not started
   - **Description**: Automate the retraining of the Scikit-Learn Local ML model. Build a CRON job that takes all newly corrected user transactions, retrains the model weekly, and deploys it with zero downtime.

4. **Account Aggregator (AA) API Exploration (Sahamati / Setu / Finvu)**
   - **Category**: Deep Integration
   - **Priority**: Medium
   - **Status**: Not started
   - **Description**: Research and build a Proof of Concept (PoC) for fetching bank data directly via India's Account Aggregator framework to bypass the need for SMS parsing and PDF uploads.

5. **Cash Flow Forecasting (Predictive Analytics)**
   - **Category**: Core Feature
   - **Priority**: Low
   - **Status**: Not started
   - **Description**: Use historical spending data to predict end-of-month balances and warn users *before* they breach their budgets.

6. **Fundraising Deck Preparation**
   - **Category**: Business & Strategy
   - **Priority**: Low (Dependent on metrics)
   - **Status**: Not started
   - **Description**: If MRR and DAU metrics are strong, prepare a seed deck highlighting Fynlo's $0 ML inference cost and high margins to approach angel investors.

# Fynlo Incident Runbook & Ops Metrics

This runbook outlines standard operating procedures (SOPs) for the engineering team to diagnose, escalate, and resolve production incidents. It works in tandem with the **Ops Metrics Dashboard** (`/admin/metrics`).

## 1. Ops Metrics Dashboard
The Ops Dashboard is available to admin users at `https://fynlo.com/admin`. 

**Key Metrics Monitored:**
- **Users**: Total, Pro Conversions, and 24h Signups.
- **Processing Load**: Total transactions parsed, 24h throughput, and `needs_review_backlog`.
- **System**: ML Engine health, lifetime API costs saved (due to Local ML migration), and MRR.

### Thresholds & Alerts
If any of the following thresholds are breached, consider it a **Sev-2** or **Sev-1** incident:
1. **Review Backlog Spike**: If `needs_review_backlog` > 5% of `total_transactions`, the Local ML engine accuracy has degraded or a new merchant format was introduced.
2. **0 Signups in 24h**: If `new_24h` == 0 during a weekday, auth or Razorpay flows may be broken.

---

## 2. Incident Response Workflow

### Incident Classifications
*   **Sev-1 (Critical)**: Total system outage (Backend 502s, DB down, or Auth broken).
*   **Sev-2 (High)**: Core feature broken (PDF statement parser failing, or Webhooks dropped).
*   **Sev-3 (Medium)**: Non-critical degradation (ML engine confidence low, UI bugs).

### Triage Steps
1. **Acknowledge**: On-call engineer claims the incident.
2. **Investigate**: 
    - Check Sentry (Frontend & Backend) for stack traces.
    - View Render deployment logs (`https://dashboard.render.com`).
3. **Mitigate**: Apply a hotfix or rollback to the previous successful commit.
4. **Resolve**: Confirm system metrics have normalized on the Ops Dashboard.
5. **Post-Mortem**: Required for all Sev-1 incidents.

---

## 3. Common Scenarios & SOPs

### Scenario A: Razorpay Webhooks Failing
**Symptom**: Users pay for Pro but their accounts don't upgrade.
1. Check Sentry for `HMAC Signature Verification Failed`.
2. Ensure `RAZORPAY_WEBHOOK_SECRET` in `.env` matches the Razorpay Dashboard.
3. Use the Razorpay Dashboard to manually retry failed webhooks.

### Scenario B: Database Connections Exhausted
**Symptom**: FastAPI throws `TimeoutError` on SQLAlchemy connections.
1. Verify if background workers (Celery) are hoarding connections.
2. Restart the `fynlo-api` web service on Render.
3. Increase `pool_size` and `max_overflow` in `backend/app/database.py`.

### Scenario C: High "Needs Review" Backlog
**Symptom**: The Ops Dashboard shows a massive spike in Uncategorized transactions.
1. Review the `merchant_or_upi` strings of the flagged transactions.
2. Add new regex patterns to `backend/app/services/ai_categorizer.py`.
3. Retrain the local ML model using updated data and push the new `categorizer_model.pkl`.

## 4. Emergency Contacts
*   **Lead Engineer**: harsh@fynlo.com
*   **Hosting Support**: Render Enterprise Support Portal
*   **Payment Gateway**: Razorpay Merchant Helpdesk

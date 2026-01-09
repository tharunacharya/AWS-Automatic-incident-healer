# Enterprise AIOps Platform: Final Walkthrough

> [!IMPORTANT]
> The system has graduated from "Prototype" to **"Enterprise Platform"**.
> All 3 requested Horizons have been implemented.

## Key Features
*   **Predictive Logic**: AI can anticipate issues before they fully manifest.
*   **Status Polling**: Real-time updates on remediation progress.
*   **Cost Estimator**: Provides estimated costs for proposed actions.

## 1. System Overview (New Architecture)
*   **Brain**: Bedrock (Claude 3) + **S3 Knowledge Base (RAG)** + **Predictive Logic**.
*   **Hands**: **SSM Automation** (Real Remediation) + **Status Polling**.
*   **Guardrails**: **Cost Estimator** (Simulated Pricing API) + **Risk Assessment**.
*   **Governance**: **Immutable Audit Ledger** (DynamoDB WORM Table).

## 2. Verification Steps (The "Perfect Demo")

### Step 1: Trigger "5xx Spike" (Tests RAG & SSM)
Use the `alarm_trigger.py` or AWS CLI.
```bash
aws lambda invoke \
  --function-name ai-incident-healer-detector \
  --payload '{"detail": {"alarmName": "5xxErrorSpike", "reason": "500 errors > 5%", "state": {"value": "ALARM"}}}' \
  --cli-binary-format raw-in-base64-out \
  response.json
```
**Observation**:
1.  **Analyzer Logs**: "Retrieved runbook for 5xxErrorSpike".
2.  **Mission Control**: AI Explanation quotes the Runbook ("Checking DB connection pool...").
3.  **Slack Notification**:
    -   **Headline**: 🚨 High Risk Incident
    -   **Detailed Problem**: "Simulated: The application process is stuck..." (or similar detailed explanation)
    -   **Recommended Action**: RESTART_SERVICE
    -   **Why take this action?**: "Restarting the service will terminate..." (justification from AI)
    -   **Buttons**: `Approve`, `Reject`
4.  **Healing**: Healer triggers SSM Document `ai-incident-healer-restart-service` (Real API Call).

### Step 2: Approve Action (Tests Audit)
Login to Mission Control (`admin@example.com` / `Password123!`) and click **"Authorize Auto-Heal"**.
**Observation**:
1.  **Audit Log**: A new entry is written to `ai-incident-healer-audit`.
    *   `EventType`: `HUMAN_DECISION`
    *   `Action`: `APPROVE`
    *   `User`: `admin@example.com`

### Step 3: Trigger "High CPU" (Tests Predictive Fallback)
```bash
aws lambda invoke \
  --function-name ai-incident-healer-detector \
  --payload '{"detail": {"alarmName": "HighCPU", "reason": "CPU > 90%", "state": {"value": "ALARM"}}}' \
  --cli-binary-format raw-in-base64-out \
  response.json
```
**Observation**:
1.  **RAG**: Loads `HighCPU.md` (Suggests checking infinite loops).
2.  **Healer**: Triggers SSM Document `ai-incident-healer-scale-up`.

### Step 4: Verify Slack Integration
Run the test script to confirm Slack connectivity:
```bash
python3 test_slack.py https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```
**Observation**:
1.  Terminal Output: `Message sent! Status: 200`
2.  **Slack Channel**: A "Hello from your AI Incident Healer!" message appears.

## 3. Audit Compliance
You can prove compliance by querying the immutable ledger:
```bash
aws dynamodb scan --table-name ai-incident-healer-audit
```
*Note: You cannot delete items from this table (Access Denied).*

## 4. Useful Links
*   [Mission Control Dashboard](http://ai-incident-healer-frontend-20251223155425994800000002.s3-website-us-east-1.amazonaws.com)
*   [Knowledge Base Bucket (Runbooks)](https://s3.console.aws.amazon.com/s3/buckets/ai-incident-healer-kb-20251223160654703000000001)
*   [SSM Documents](https://console.aws.amazon.com/systems-manager/documents)

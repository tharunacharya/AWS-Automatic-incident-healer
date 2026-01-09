# Walkthrough v4 - Premium Mission Control & Demo Scenarios

## Overview
This phase demonstrates the **Premium "Mission Control" UI** and the **Dual-Path logic** where:
*   **Low Risk/Cost actions** (< $20) are Auto-Healed.
*   **High Risk/Cost actions** (> $20) require Human Approval.

## 1. Demo Scenarios

### Scenario A: Auto-Approval (Low Cost)
**Trigger**: High CPU Usage
**Action**: Restart Service (~$0.50)
**Outcome**: System heals automatically *without* asking for permission.

```bash
aws lambda invoke \
    --function-name ai-incident-healer-detector \
    --payload '{"detail": {"alarmName": "HighCPU", "state": {"value": "ALARM", "reason": "Process stuck at 99%", "timestamp": "2025-12-09T02:00:00.000+0000"}}}' \
    --cli-binary-format raw-in-base64-out \
    --output json response_cpu.json
```

**What to watch:**
1.  Check the UI or Slack. You will see a notification that the system is **Auto-Healing**.
2.  No approval buttons will appear.

### Scenario B: Manual Approval (High Cost)
**Trigger**: High Traffic Spike
**Action**: Scale Up Cluster (~$45.00)
**Outcome**: System **pauses** and demands approval because the cost exceeds the $20 threshold.

```bash
aws lambda invoke \
    --function-name ai-incident-healer-detector \
    --payload '{"detail": {"alarmName": "HighTraffic", "state": {"value": "ALARM", "reason": "Traffic spike detected (Load > 80%)", "timestamp": "2025-12-09T02:05:00.000+0000"}}}' \
    --cli-binary-format raw-in-base64-out \
    --output json response_traffic.json
```

**What to watch:**
1.  Get the `approval_id` from DynamoDB or the response.
2.  Open the Dashboard. You will see **"ACTION REQUIRED"** and the Approve/Reject buttons.
3.  Note the **Estimated Cost** (~$45.00) shown on the card.

### Scenario C: Critical API Failure (High Risk)
**Trigger**: 5xx Error Spike
**Outcome**: High Risk Analysis -> Manual Approval.

```bash
aws lambda invoke \
    --function-name ai-incident-healer-detector \
    --payload '{"detail": {"alarmName": "5xxErrorSpike", "state": {"value": "ALARM", "reason": "API availability < 90%", "timestamp": "2025-12-09T01:10:00.000+0000"}}}' \
    --cli-binary-format raw-in-base64-out \
    --output json response_api.json
```

## 2. Accessing the Dashboard
URL Format:
`http://ai-incident-healer-frontend-20251223155425994800000002.s3-website-us-east-1.amazonaws.com/index.html?approvalId=[APPROVAL_ID]`

Find Approval ID:
```bash
aws dynamodb scan --table-name ai-incident-healer-approvals --limit 1 --query "Items[0].approval_id.S" --output text
```

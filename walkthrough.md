# AI-Powered Autonomous Incident Healer - Walkthrough

This solution provides a complete, serverless framework for autonomous incident resolution on AWS.

## What has been built

1.  **Infrastructure (Terraform)**:
    *   **DynamoDB**: `ai-incident-healer-incidents` for tracking incident state.
    *   **S3**: `ai-incident-healer-logs-{id}` for storing raw logs and analysis.
    *   **EventBridge**: Rule to trigger on CloudWatch Alarms.
    *   **Step Functions**: `IncidentResponseWorkflow` to orchestrate the healing process.
    *   **SSM Document**: `ai-incident-healer-restart-service` for safe service restarts.

2.  **Lambda Functions**:
    *   `Detector`: Ingests alarms, creates incident records.
    *   `Analyzer`: Uses **Amazon Bedrock (Claude 3)** to analyze logs and recommend actions.
    *   `Healer`: Executes actions (Restart, Scale, Cache Clear) via API/SSM.
    *   `Notifier`: Sends rich Slack alerts with approval buttons.

## Verification Steps

### 1. Deploy the Stack
Run the deployment script to provision all resources:
```bash
./deploy.sh
```

### 2. Simulate an Incident
First, create a mock alarm if it doesn't exist:
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name "HighCPU-Demo" \
    --metric-name "CPUUtilization" \
    --namespace "AWS/EC2" \
    --statistic "Average" \
    --period 300 \
    --threshold 90 \
    --comparison-operator "GreaterThanThreshold" \
    --evaluation-periods 1 \
    --output json
```

Then, trigger the alarm to test the pipeline:
```bash
aws cloudwatch set-alarm-state \
    --alarm-name "HighCPU-Demo" \
    --state-value ALARM \
    --state-reason "CPU utilization > 90% for 5 minutes" \
    --output json
```

### 3. Observe the Workflow
1.  **Slack**: Check your configured channel. You should see a "Incident Resolved" or "Requires Approval" message.
2.  **DynamoDB**: Check the `incidents` table. You will see a new item with `status: ANALYZED` or `HEALED`.
3.  **Step Functions**: Go to the AWS Console -> Step Functions. You will see a successful execution graph.

### 4. Test Healing Actions
To test specific healing actions, you can modify the mock logs in `src/lambdas/analyzer/handler.py` (or ensure real logs exist) to prompt the AI to recommend `RESTART_SERVICE`.

## Next Steps
*   **Connect Real Logs**: Update `Analyzer` to query your specific application log groups.
*   **Expand SSM Docs**: Add more automation documents for complex healing scenarios (e.g., database failover).
*   **Fine-tune Prompts**: Adjust the Bedrock prompt in `Analyzer` for your specific domain context.

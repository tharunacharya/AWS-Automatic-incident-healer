# AI-Powered Autonomous Incident Healer

A serverless, AI-driven incident management system for AWS that detects anomalies, analyzes root causes using Amazon Bedrock (Claude), and executes healing actions.

## Architecture

1.  **Detection**: CloudWatch Alarm -> EventBridge -> Detector Lambda.
2.  **Orchestration**: Step Functions manages the workflow.
3.  **Analysis**: Analyzer Lambda queries CloudWatch Logs & Bedrock (LLM) for RCA.
4.  **Healing**: Healer Lambda triggers SSM Automation or API calls.
5.  **Notification**: Slack notifications at key steps.

## Prerequisites

*   AWS Account
*   Terraform installed
*   Amazon Bedrock Model Access (Claude 3 Sonnet)
*   Slack Webhook URL

## Deployment

1.  Clone the repository.
2.  Export your Slack Webhook URL:
    ```bash
    export TF_VAR_slack_webhook_url="https://hooks.slack.com/services/..."
    ```
3.  Run the deployment script:
    ```bash
    chmod +x deploy.sh
    ./deploy.sh
    ```

## Testing

1.  **Trigger an Alarm**:
    ```bash
    aws cloudwatch set-alarm-state --alarm-name "HighCPU" --state-value ALARM --state-reason "CPU > 90%"
    ```
2.  **Check Slack**: You should see a notification.
3.  **Check Step Functions**: View the execution in the AWS Console.

## Directory Structure

*   `terraform/`: Infrastructure as Code.
*   `src/lambdas/`: Python source code for Lambda functions.
*   `src/step_functions/`: Workflow definition.
*   `src/ssm_docs/`: Systems Manager Automation documents.

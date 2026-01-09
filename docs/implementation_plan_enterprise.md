# Implementation Plan - Enterprise Horizon 1: Operational Maturity

# Goal Description
Transition the "Healer" from a simulation engine to a real-world infrastructure automation tool using AWS Systems Manager (SSM). This allows the AI to actually restart services, resize instances, and execute remediation across the fleet.

## User Review Required
> [!IMPORTANT]
> This upgrade requires `ssm:StartAutomationExecution` permissions. Ensure the target instances (if we were using real EC2s) have the SSM Agent installed. For this demo, we will execute against *Simulated* targets or use Automation Documents that don't require targets (e.g., calling AWS APIs).

## Proposed Changes

### Infrastructure (Terraform)
#### [NEW] [ssm.tf](file:///Users/adminmac/Desktop/AWS Project/terraform/ssm.tf)
- Define `aws_ssm_document` resources:
    - `RestartService` (Action: `aws:runCommand` or `aws:executeScript`)
    - `ScaleUpCluster` (Action: `aws:executeScript` calling AutoScaling API)

#### [MODIFY] [iam.tf](file:///Users/adminmac/Desktop/AWS Project/terraform/iam.tf)
- Update `healer_role` to allow `ssm:StartAutomationExecution` and `ssm:GetAutomationExecution`.

### Backend (Lambdas)
#### [MODIFY] [src/lambdas/healer/handler.py](file:///Users/adminmac/Desktop/AWS Project/src/lambdas/healer/handler.py)
- **Current**: `time.sleep(2)` (Simulation)
- **New**: 
    1.  Map `recommended_action` to specific SSM Document names.
    2.  Call `ssm.start_automation_execution()`.
    3.  Return the `AutomationExecutionId`.
- **Note**: Since Step Functions is managing the flow, the Healer can kick off the SSM job. We might need a polling loop or a `WaitForSSM` state in Step Functions, but for now, we'll keep it synchronous-ish or return the ID for verification.

## Verification Plan
1.  **Deploy**: `terraform apply`.
2.  **Trigger**: Fire a "HighCPU" alarm.
3.  **Verify**:
    - Check SSM Console > Automations to see the execution.
    - Confirm the Healer Lambda successfully triggers it.

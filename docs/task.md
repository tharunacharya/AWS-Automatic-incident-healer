# Tasks: AI-powered Autonomous Incident Healer (Dual Approval v3)

- [x] v1 Implementation (Core) <!-- id: 0 -->
- [x] v2 Enterprise Upgrade (Retries, Fallback, Simple Approval) <!-- id: 23 -->
- [x] **Phase 1: Infrastructure & Database** <!-- id: 41 -->
    - [x] Create DynamoDB `Approvals` table <!-- id: 42 -->
    - [x] Update IAM Roles for new Lambdas and DynamoDB access <!-- id: 43 -->
    - [x] Update API Gateway for new endpoints (`/slack`, `/approval`) <!-- id: 44 -->
- [x] **Phase 2: Lambda Implementation** <!-- id: 45 -->
    - [x] Create `SendApprovalRequest` Lambda <!-- id: 46 -->
    - [x] Create `SlackActionHandler` Lambda <!-- id: 47 -->
    - [x] Update `FrontendApprovalHandler` Lambda <!-- id: 48 -->
- [x] **Phase 3: Workflow Integration** <!-- id: 49 -->
- [x] **Phase 4: Verification** <!-- id: 52 -->
- [x] **Phase 5: Production Frontend (v4)** <!-- id: 55 -->

## Horizon 1: Operational Maturity (Real-World Actions)
- [x] **Infrastructure: SSM Layer** <!-- id: 62 -->
    - [x] Create SSM Document: `RestartService` (ShellScript) <!-- id: 63 -->
    - [x] Create SSM Document: `ScaleEC2` (Automation) <!-- id: 64 -->
    - [x] Trigger test incident and verify all components
    - [x] Verify Detector -> Analyzer -> Healer flow
    - [x] Verify SSM Automation execution (Auto-Remediation)
    - [x] Verify Audit Log entry in DynamoDB
    - [x] Update Healer IAM Role for SSM Access <!-- id: 65 -->
- [x] **Healer Lambda Upgrade** <!-- id: 66 -->
    - [x] Replace simulation logic with `boto3.ssm` calls <!-- id: 67 -->
    - [x] Implement status polling for SSM execution <!-- id: 68 -->
- [x] **Cost Estimator Upgrade** <!-- id: 69 -->
    - [x] Integrate AWS Pricing API (Mock/Proxy if needed) <!-- id: 70 -->

## Horizon 2: Intelligence Deepening (Smart AI)
- [x] **RAG Integration** <!-- id: 71 -->
    - [x] Setup Knowledge Base (S3/Vector) <!-- id: 72 -->
    - [x] Update Analyzer to query Knowledge Base <!-- id: 73 -->
- [x] **Predictive Logic** <!-- id: 74 -->
    - [x] Enhance Bedrock prompt for anomaly prediction <!-- id: 75 -->

## Horizon 3: Enterprise Scale
- [x] **Audit & Governance** <!-- id: 76 -->
    - [x] Create QLDB or Immutable Ledger Table <!-- id: 77 -->
    - [x] Log all decision events to Ledger <!-- id: 78 -->

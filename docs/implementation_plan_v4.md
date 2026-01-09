# Implementation Plan - Production Frontend Approval (v4)

## Goal Description
Upgrade the frontend approval system to be production-grade. This involves adding **Cognito Authentication**, hosting a **Single Page Application (SPA)** on S3, and enhancing the **Lambda/DynamoDB logic** to handle race conditions, expiry, and comments securely.

## User Review Required
> [!IMPORTANT]
> **Cognito Setup**: A new Cognito User Pool will be created. You will need to create a user in this pool to test the approval flow.
> **S3 Hosting**: A new S3 bucket will be created to host the frontend UI.
> **API Auth**: The `POST /approval/{id}/decision` endpoint will now require a valid Cognito JWT.

## Proposed Architecture Updates

### 1. Infrastructure (Terraform)
*   **Cognito (`cognito.tf`)**:
    *   `aws_cognito_user_pool`: For user management.
    *   `aws_cognito_user_pool_client`: For the frontend app.
    *   `aws_cognito_user_group`: "Approvers" group (optional, but good practice).
*   **S3 (`s3_website.tf`)**:
    *   Bucket for static website hosting.
    *   Bucket policy for public read access (or CloudFront OAI if stricter, keeping it simple for now as per "simple CSS layout").
*   **API Gateway (`apigateway.tf`)**:
    *   `aws_apigatewayv2_authorizer`: Cognito User Pool authorizer.
    *   Attach authorizer to `POST /approval/{approvalId}/decision`.
    *   Enable CORS.

### 2. Lambda Functions
*   **`FrontendApprovalHandler` (Enhanced)**:
    *   **GET**: Return extended metadata (actions taken, cost breakdown, etc.). Check expiry.
    *   **POST**:
        *   Validate `status == 'PENDING'`.
        *   Validate `expires_at > now`.
        *   Use **Conditional Writes** to prevent race conditions (Slack vs Frontend).
        *   Call `sendTaskSuccess` with `approver` info and `comment`.
        *   Handle `ConditionalCheckFailedException` gracefully.

### 3. Frontend UI (`src/frontend/index.html`)
*   Vanilla JS + CSS (Single file).
*   **Features**:
    *   Login screen (Cognito integration).
    *   Fetch approval details.
    *   Display formatted cost/risk/analysis.
    *   Approve/Reject buttons with Comment modal.
    *   Error/Success handling.

## Detailed Workflow
1.  **User** receives notification (Slack/Email) with link to S3 UI: `https://<bucket>.s3.amazonaws.com/index.html?approvalId=...`
2.  **User** opens UI, logs in via Cognito.
3.  **UI** calls `GET /approval/{id}`.
4.  **User** reviews details and clicks "Approve".
5.  **UI** calls `POST /approval/{id}/decision` with JWT.
6.  **Lambda** verifies state, updates DynamoDB (atomic), resumes Step Function.
7.  **UI** shows success message.

## Verification Plan
1.  **Deploy**: Apply Terraform.
2.  **Setup**: Create Cognito User.
3.  **Test**:
    *   Trigger Incident.
    *   Open UI.
    *   Login.
    *   Approve.
    *   Verify Step Function resumes.
    *   Try to approve again (should fail/show status).

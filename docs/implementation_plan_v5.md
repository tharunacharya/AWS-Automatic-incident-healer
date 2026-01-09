# Implementation Plan - Phase 6: Real-time Updates & Modern UI

## Goal
Upgrade the Frontend Approval Dashboard to provide a "Mission Control" experience. Users should see detailed analysis, approve actions, and then watch the detailed remediations steps (Healing, Verification) occur in real-time without refreshing.

## User Review Required
> [!IMPORTANT]
> This requires giving the `FrontendApprovalHandler` Lambda read access to the main `Incidents` table again, which was previously removed for strict separation. This is necessary to fetch the "Healing" and "Verification" status.

## Proposed Changes

### Infrastructure (Terraform)
#### [MODIFY] [lambdas.tf](file:///Users/adminmac/Desktop/AWS Project/terraform/lambdas.tf)
- Add `INCIDENTS_TABLE_NAME` environment variable back to `frontend_approval_handler`.

#### [MODIFY] [iam.tf](file:///Users/adminmac/Desktop/AWS Project/terraform/iam.tf)
- Add `dynamodb:GetItem` permission for the `Incidents` table to `frontend_approval_handler_role`.

### Backend (Lambda)
#### [MODIFY] [frontend_approval_handler/handler.py](file:///Users/adminmac/Desktop/AWS Project/src/lambdas/frontend_approval_handler/handler.py)
- **GET Request**:
    1. Fetch `Approval` item (as before).
    2. Extract `incident_id`.
    3. Fetch `Incident` item from `Incidents` table.
    4. Merge response: Include `healing_status`, `healing_result`, `verification`, and `status` (Resolved/Failed) from the Incident record.

### Frontend
#### [MODIFY] [index.html](file:///Users/adminmac/Desktop/AWS Project/src/frontend/index.html)
- **Design Overhaul**:
    - Use a constrained, centered "Card" layout with modern shadows and typography (Inter/Roboto).
    - Status Timeline: Vertical or Horizontal stepper showing `Detected -> Analyzed -> Approved -> Healed -> Verified`.
- **Logic**:
    - **Polling**: After approval (or if already approved), poll `GET` endpoint every 3 seconds.
    - **Dynamic State**: Update the "Current Stage" based on the merged API response.
    - **Live Logs**: Display `healing_result` message as a "console log" output if available.

## Verification Plan
### Automated Tests
- None (UI visual verification).

### Manual Verification
1.  Trigger `HighTraffic` alarm.
2.  Open Link.
3.  Click Approve.
4.  **Watch**:
    - Button disappears.
    - Status changes to "Healing...".
    - Status changes to "Verifying...".
    - Status changes to "Resolved (Success)".

# AI Autonomous Incident Healer - Final Demo Script

## 1. Project Overview
**What is it?**
This is an **AI-Powered "Self-Healing" Infrastructure System**. It autonomously detects cloud incidents (like server crashes or traffic spikes), analyzes the root cause using GenAI (AWS Bedrock), and fixes them—either automatically (for low-risk issues) or after asking for human permission (for high-risk issues).

**The Core Concept:**
*   **"The Brain"**: AWS Bedrock (Claude 3) analyzes logs to understand *why* something broke.
*   **"The Hands"**: AWS Lambda & SSM execute the fix (Restart service, Scale up, etc.).
*   **"The Guardrails"**: A Cost & Risk Estimator ensures the AI doesn't spend too much money without approval.

## 2. Uses & Advantages
| Feature | Advantage |
| :--- | :--- |
| **Instant Root Cause Analysis** | No more digging through thousands of logs. The AI tells you *exactly* what broke in seconds. |
| ** autonomous Healing** | Low-risk issues (like a stuck process) are fixed instantly, reducing downtime to near zero. |
| **Cost & Risk Control** | The system calculates the $$ cost of a fix. If it's expensive (>$20), it *pauses* and asks a human. |
| **Human-in-the-Loop** | Critical decisions (like scaling a cluster) require a click of a button from the SRE, ensuring safety. |

---

## 3. The 2-Minute Demo Script (Video Walkthrough)

**Concept**: The video should show two back-to-back scenarios.
*   **Scenario A (0:00 - 1:00)**: Auto-Healing (Speed).
*   **Scenario B (1:00 - 2:00)**: Manual Approval (Safety).

| Time | Visual / Action | Voiceover Script |
| :--- | :--- | :--- |
| **0:00** | **[Show Architecture Diagram or Title Screen]** | "Hi, this is a demo of my **AI Autonomous Incident Healer**. In modern cloud ops, downtime is expensive. My project uses **GenAI** to detect, analyze, and fix infrastructure issues automatically." |
| **0:15** | **[Switch to Dashboard]** Show empty/clean Mission Control UI. | "Let's look at **Scenario 1: Auto-Healing**. Imagine a low-risk issue, like a high CPU spike on a server." |
| **0:25** | **[Action]** Trigger `HighCPU` Alarm (Scenario A). <br>Show Dashboard updating instantly: "ANALYZING" -> "AUTO-HEALING". | "I've just simulated a CPU spike. Watch the dashboard. The system detects the alarm, and the AI immediately identifies a 'Stuck Process'." |
| **0:30** | **[Visual]** Zoom in on "Cost: ~$0.50" and Green Status. | "Because the fix is cheap—just restarting a service costing 50 cents—the AI classifies this as **Low Risk**." |
| **0:40** | **[Visual]** Status changes to "HEALED". Toast notification appears. | "It bypasses manual approval and executes the fix instantly. In less than 30 seconds, the system healed itself without waking up an engineer." |
| **0:50** | **[Transition]** Clear screen/Reset. | "But what about dangerous or expensive changes? That brings us to **Scenario 2**." |
| **0:55** | **[Action]** Trigger `HighTraffic` Alarm (Scenario B). | "Here, we simulate a massive **Traffic Spike** causing a 500 error API outage." |
| **1:05** | **[Visual]** Dashboard turns **ORANGE/RED**. "ACTION REQUIRED" badge appears. Status: "PENDING". | "The AI analyzes the logs and recommends **Scaling Up** the entire cluster. But wait—look at the Cost Estimator." |
| **1:15** | **[Visual]** Zoom in on "Cost: ~$45.00" and "Risk: HIGH". Mouse hovers over 'Approve' button. | "The estimated cost is **$45.00**. This exceeds our $20 safety threshold. So, the system **pauses** and demands Human Authorization." |
| **1:30** | **[Action]** Click **"Authorize Auto-Heal"**. Modal appears. Type "Go ahead". Click Confirm. | "I review the AI's **detailed root cause and justification** in the Slack message, decide it's valid, and click Approve. Only *now* does the system execute the scaling command." |
| **1:45** | **[Visual]** Status changes to "HEALED" / "VERIFIED". | "The system scales the cluster, verifies the health metrics are back to normal, and marks the incident as Resolved." |
| **1:55** | **[Closing Shot]** Show "Mission Control" logo. | "This allows us to have the speed of AI automation, with the safety of human oversight. Thanks for watching." |

---

## 4. Technical Stack (For Q&A)
*   **Frontend**: S3 Website, API Gateway, HTML5/CSS3 (Glassmorphism).
*   **Backend**: AWS Lambda (Python), DynamoDB, Step Functions.
*   **AI Model**: AWS Bedrock (Claude 3 Sonnet).
*   **Infrastructure**: Terraform (IaC).

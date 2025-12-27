# Runbook: High CPU Utilization

**Severity**: MEDIUM
**SLA**: 30 Minutes

## Symptoms
- CPU Utilization > 80% for more than 5 minutes.
- Latency increasing in correlation with CPU.

## Root Cause Analysis Steps
1.  **Identify Top Consumers**: Use `top` or `htop` to find the process ID.
2.  **Check for Infinite Loops**: Application code regressions can cause tight loops.
3.  **Check for Crypto-Mining**: Unfamiliar processes consuming 100% CPU.

## Remediation Actions
1.  **Scale Up**: Add more capacity immediately to dilute load.
2.  **Restart Service**: Kill stuck processes.
3.  **Block Malicious Traffic**: If traffic is from a single IP, block it at WAF.

## Escalation
If CPU remains high after scaling, page the **Platform-Engineering** team.

# Runbook: 5xx Error Spike Recovery

**Severity**: HIGH
**SLA**: 15 Minutes

## Symptoms
- Elevated 500/502/503 response codes on the Load Balancer.
- Users reporting "Something went wrong" or timeouts.

## Root Cause Analysis Steps
1.  **Check Database Connectivity**: 90% of 5xx errors are due to DB connection pool exhaustion.
2.  **Check Upstream Dependencies**: Is the Payment Gateway or Auth Service returning errors?
3.  **Check Deployment Status**: Was there a recent deployment?

## Remediation Actions
1.  **Restart Service**: If memory usage is high or threads are stuck, a rolling restart often clears the issue.
2.  **Rollback**: If a deployment occurred in the last hour, immediate rollback is mandatory.
3.  **Scale Up**: If CPU > 80%, scale out the ASG.

## Escalation
If unresolved after 15 minutes, page the **SRE-OnCall** team.

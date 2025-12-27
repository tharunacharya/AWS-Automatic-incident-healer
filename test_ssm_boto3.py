import boto3
import os

ssm = boto3.client('ssm')
doc_name = "ai-incident-healer-restart-service"
role_arn = "arn:aws:iam::786923079679:role/ai-incident-healer-healer-role"

params = {
    'Cluster': ['default'],
    'Service': ['demo-service'],
    'ExecutionRole': [role_arn]
}

print(f"Triggering {doc_name} with params: {params}")

try:
    response = ssm.start_automation_execution(
        DocumentName=doc_name,
        Parameters=params
    )
    print("Success:", response['AutomationExecutionId'])
except Exception as e:
    print("Error:", e)

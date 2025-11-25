import json
import logging
import os
import boto3
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
ecs = boto3.client('ecs')
ssm = boto3.client('ssm')

TABLE_NAME = os.environ['TABLE_NAME']

def execute_restart_service(details):
    # In a real app, we'd parse the resource ID from the alarm dimensions
    # For demo, we'll assume a specific cluster/service or mock it
    cluster = os.environ.get('ECS_CLUSTER', 'default')
    service = os.environ.get('ECS_SERVICE', 'demo-service')
    
    logger.info(f"Restarting ECS service {service} in cluster {cluster}")
    
    try:
        # ecs.update_service(
        #     cluster=cluster,
        #     service=service,
        #     forceNewDeployment=True
        # )
        time.sleep(2) # Simulate API call
        return {"status": "SUCCESS", "message": f"Service {service} restart initiated."}
    except Exception as e:
        logger.error(f"Failed to restart service: {e}")
        return {"status": "FAILED", "message": str(e)}

def execute_scale_up(details):
    logger.info("Scaling up service")
    return {"status": "SUCCESS", "message": "Service scaled up by 1 task."}

def execute_clear_cache(details):
    logger.info("Clearing cache")
    return {"status": "SUCCESS", "message": "Cache cleared via SSM."}

def handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    
    incident_id = event.get('incident_id')
    healing_result = event.get('healing_result', {}) # Input from previous step if any
    
    # The input structure depends on the Step Functions state input path.
    # Based on workflow.json: 
    # "ExecuteHealing": { "Type": "Task", "Resource": "${healer_arn}", ... }
    # The input to this state is the output of CheckConfidence (which passes through the whole state).
    # So event should contain 'analysis' from the previous step.
    
    analysis = event.get('analysis', {})
    action = analysis.get('recommended_action')
    
    result = {"status": "SKIPPED", "message": "No action taken."}
    
    if action == 'RESTART_SERVICE':
        result = execute_restart_service(event)
    elif action == 'SCALE_UP':
        result = execute_scale_up(event)
    elif action == 'CLEAR_CACHE':
        result = execute_clear_cache(event)
    elif action == 'NONE':
        result = {"status": "SKIPPED", "message": "AI recommended no action."}
    else:
        result = {"status": "UNKNOWN", "message": f"Unknown action: {action}"}
        
    # Update DynamoDB
    table = dynamodb.Table(TABLE_NAME)
    table.update_item(
        Key={
            'incident_id': incident_id,
            'timestamp': event.get('timestamp')
        },
        UpdateExpression="set healing_status = :s, healing_result = :r",
        ExpressionAttributeValues={
            ':s': result['status'],
            ':r': json.dumps(result)
        }
    )
    
    return result

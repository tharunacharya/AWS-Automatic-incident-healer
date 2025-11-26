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

def execute_reboot_instance(details):
    logger.info("Rebooting EC2 instance")
    time.sleep(2)
    return {"status": "SUCCESS", "message": "Instance reboot initiated."}

def execute_scale_down(details):
    logger.info("Scaling down service (Rollback)")
    return {"status": "SUCCESS", "message": "Service scaled down (Rollback)."}

def execute_fallback(original_action, details):
    logger.info(f"Executing fallback for {original_action}")
    if original_action == 'RESTART_SERVICE':
        return execute_reboot_instance(details)
    else:
        # Generic fallback
        return execute_scale_up(details)

def execute_rollback(original_action, details):
    logger.info(f"Executing rollback for {original_action}")
    if original_action == 'SCALE_UP':
        return execute_scale_down(details)
    else:
        return {"status": "SKIPPED", "message": f"No rollback defined for {original_action}"}

def handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    
    incident_id = event.get('incident_id')
    
    # Check for action_type (PRIMARY, FALLBACK, ROLLBACK)
    action_type = event.get('action_type', 'PRIMARY')
    
    # Analysis might be in 'analysis' (from parallel state output) or direct
    analysis = event.get('analysis', {})
    if not analysis and 'analysis' in event.get('ParallelAnalysis', [{}])[0]:
         # Handle Parallel state output structure if needed, but usually we pass specific inputs
         analysis = event.get('ParallelAnalysis')[0].get('analysis', {})

    action = analysis.get('recommended_action')
    # If this is a fallback/rollback call, the action might be passed explicitly or derived
    if not action:
        action = event.get('original_action', 'UNKNOWN')

    result = {"status": "SKIPPED", "message": "No action taken."}
    
    if action_type == 'FALLBACK':
        result = execute_fallback(action, event)
    elif action_type == 'ROLLBACK':
        result = execute_rollback(action, event)
    else: # PRIMARY
        if action == 'RESTART_SERVICE':
            result = execute_restart_service(event)
        elif action == 'SCALE_UP':
            result = execute_scale_up(event)
        elif action == 'CLEAR_CACHE':
            result = execute_clear_cache(event)
        elif action == 'REBOOT_INSTANCE':
            result = execute_reboot_instance(event)
        elif action == 'NONE':
            result = {"status": "SKIPPED", "message": "AI recommended no action."}
        else:
            result = {"status": "UNKNOWN", "message": f"Unknown action: {action}"}
        
    # Update DynamoDB
    table = dynamodb.Table(TABLE_NAME)
    update_expr = "set healing_status = :s, healing_result = :r"
    expr_attrs = {
        ':s': result['status'],
        ':r': json.dumps(result)
    }
    
    if action_type == 'FALLBACK':
        update_expr += ", fallback_used = :f"
        expr_attrs[':f'] = True
    elif action_type == 'ROLLBACK':
        update_expr += ", rollback_status = :rb"
        expr_attrs[':rb'] = result['status']

    table.update_item(
        Key={
            'incident_id': incident_id,
            'timestamp': event.get('timestamp')
        },
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_attrs
    )
    
    return result

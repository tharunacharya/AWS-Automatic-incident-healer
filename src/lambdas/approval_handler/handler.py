import json
import logging
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sfn = boto3.client('stepfunctions')

def handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    
    try:
        # Handle both POST (body) and GET (queryStringParameters)
        task_token = None
        action = None
        
        if event.get('body'):
            body = json.loads(event.get('body'))
            task_token = body.get('taskToken')
            action = body.get('action')
        elif event.get('queryStringParameters'):
            qs = event.get('queryStringParameters')
            task_token = qs.get('taskToken')
            action = qs.get('action')
        
        if not task_token or not action:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing taskToken or action'})
            }
            
        if action == 'APPROVE':
            sfn.send_task_success(
                taskToken=task_token,
                output=json.dumps({'status': 'APPROVED', 'approver': 'admin'})
            )
            message = "Action APPROVED. Workflow resumed."
        else:
            sfn.send_task_failure(
                taskToken=task_token,
                error='ManualDenial',
                cause='User denied the action'
            )
            message = "Action DENIED. Workflow failed/stopped."
            
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': f"<html><body><h1>{message}</h1><p>You can close this window.</p></body></html>"
        }
        
    except Exception as e:
        logger.error("Error processing approval: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

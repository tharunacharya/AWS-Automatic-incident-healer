import json
import logging
import os
import uuid
import boto3
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
sfn = boto3.client('stepfunctions')

TABLE_NAME = os.environ['TABLE_NAME']
STATE_MACHINE_ARN = os.environ['STATE_MACHINE_ARN']

def handler(event, context):
    logger.info("Received event: %s", json.dumps(event))

    try:
        # Parse CloudWatch Alarm event
        detail = event.get('detail', {})
        alarm_name = detail.get('alarmName')
        state_value = detail.get('state', {}).get('value')
        reason = detail.get('state', {}).get('reason')
        timestamp = detail.get('state', {}).get('timestamp')

        if state_value != 'ALARM':
            logger.info("Alarm state is %s, ignoring.", state_value)
            return {'status': 'ignored'}

        incident_id = str(uuid.uuid4())
        
        resolved_timestamp = timestamp or datetime.utcnow().isoformat()
        
        # Save to DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        item = {
            'incident_id': incident_id,
            'timestamp': resolved_timestamp,
            'alarm_name': alarm_name,
            'reason': reason,
            'status': 'DETECTED',
            'created_at': datetime.utcnow().isoformat()
        }
        table.put_item(Item=item)
        logger.info("Saved incident %s to DynamoDB", incident_id)

        # Start Step Functions Execution
        sfn_input = {
            'incident_id': incident_id,
            'alarm_name': alarm_name,
            'reason': reason,
            'timestamp': resolved_timestamp
        }
        
        response = sfn.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            name=f"incident-{incident_id}",
            input=json.dumps(sfn_input)
        )
        
        logger.info("Started Step Function execution: %s", response['executionArn'])
        
        return {
            'statusCode': 200,
            'body': json.dumps({'incident_id': incident_id})
        }

    except Exception as e:
        logger.error("Error processing event: %s", str(e))
        raise e

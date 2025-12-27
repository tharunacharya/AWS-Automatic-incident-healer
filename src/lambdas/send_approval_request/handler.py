import json
import logging
import os
import boto3
import uuid
import urllib3
from datetime import datetime, timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
http = urllib3.PoolManager()

TABLE_NAME = os.environ['APPROVALS_TABLE_NAME']
SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']

def send_slack_message(message):
    try:
        response = http.request(
            'POST',
            SLACK_WEBHOOK_URL,
            body=json.dumps(message),
            headers={'Content-Type': 'application/json'}
        )
        if response.status != 200:
            logger.error("Request to Slack returned an error %s, the response is:\n%s", response.status, response.data)
    except Exception as e:
        logger.error("Failed to send message to Slack: %s", e)

def handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    
    task_token = event.get('taskToken')
    incident_id = event.get('incident_id')
    analysis = event.get('analysis', {})
    risk_assessment = event.get('risk_assessment', {})
    
    approval_id = str(uuid.uuid4())
    
    # Store in DynamoDB
    table = dynamodb.Table(TABLE_NAME)
    expiration_time = int((datetime.now() + timedelta(hours=1)).timestamp())
    
    item = {
        'approval_id': approval_id,
        'taskToken': task_token,
        'incident_id': incident_id,
        'status': 'PENDING',
        'analysis': json.dumps(analysis),
        'risk_assessment': json.dumps(risk_assessment),
        'created_at': datetime.now().isoformat(),
        'expires_at': expiration_time
    }
    
    table.put_item(Item=item)
    
    # Construct Slack Message with Buttons
    # Note: For interactive buttons to work, we need a Slack App with Interactivity enabled.
    # The buttons will send a payload to the configured Request URL.
    # We embed the approval_id in the button value.
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🚨 High Risk Incident: {incident_id}",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Recommended Action:*\n{analysis.get('recommended_action', 'N/A')}\n\n*Detailed Problem:*\n{analysis.get('detailed_root_cause', analysis.get('root_cause', 'N/A'))}\n\n*Why take this action?*\n{analysis.get('action_justification', analysis.get('reasoning', 'N/A'))}\n\n*Risk Level:* {risk_assessment.get('risk_level', 'HIGH')}\n*Cost Estimate:* ${risk_assessment.get('estimated_cost', 'N/A')}"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Approve",
                        "emoji": True
                    },
                    "style": "primary",
                    "value": approval_id,
                    "action_id": "approve_action"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Reject",
                        "emoji": True
                    },
                    "style": "danger",
                    "value": approval_id,
                    "action_id": "reject_action"
                }
            ]
        }
    ]
    
    send_slack_message({"blocks": blocks})
    
    return {
        'approval_id': approval_id,
        'status': 'PENDING'
    }

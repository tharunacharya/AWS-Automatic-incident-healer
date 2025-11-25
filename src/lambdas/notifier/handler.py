import json
import logging
import os
import urllib3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

http = urllib3.PoolManager()
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
    
    incident_id = event.get('incident_id')
    status = event.get('status') # HEALED, REQUIRES_APPROVAL, FAILED
    details = event.get('details', {})
    analysis = event.get('analysis', {})
    
    color = "#36a64f" # Green
    title = "Incident Resolved"
    
    if status == 'REQUIRES_APPROVAL':
        color = "#ffcc00" # Yellow
        title = "Incident Requires Approval"
    elif status == 'FAILED':
        color = "#ff0000" # Red
        title = "Healing Failed"
        
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{title}: {incident_id}",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Status:*\n{status}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Root Cause:*\n{analysis.get('root_cause', 'N/A')}"
                }
            ]
        }
    ]
    
    if status == 'HEALED':
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Action Taken:*\n{details.get('message', 'N/A')}"
            }
        })
    elif status == 'REQUIRES_APPROVAL':
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Recommended Action:*\n{analysis.get('recommended_action', 'N/A')} (Confidence: {analysis.get('confidence', 'N/A')})"
            }
        })
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Approve",
                        "emoji": True
                    },
                    "value": "approve",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Deny",
                        "emoji": True
                    },
                    "value": "deny",
                    "style": "danger"
                }
            ]
        })

    message = {
        "blocks": blocks,
        "attachments": [
            {
                "color": color,
                "blocks": [] 
            }
        ]
    }
    
    send_slack_message(message)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Notification sent')
    }

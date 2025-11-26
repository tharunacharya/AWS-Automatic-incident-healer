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
        task_token = event.get('taskToken')
        approval_url = event.get('approval_api_url')
        
        # We need to encode the task token to pass it safely in a URL parameter or body
        # For a simple GET link, we'd put it in query params.
        # But the ApprovalHandler expects a POST with body.
        # Slack buttons can send a payload to a URL (Interactive Components), but that requires setting up a Slack App Interactivity URL.
        # For this demo, we'll provide a simple "Click to Approve" link that hits the API Gateway.
        # Since we can't easily do a POST from a simple link, we might need to change ApprovalHandler to accept GET for demo simplicity,
        # OR use a simple intermediate HTML page.
        # Let's assume we use a simple GET for the demo to make it clickable.
        
        approve_link = f"{approval_url}?action=APPROVE&taskToken={task_token}"
        deny_link = f"{approval_url}?action=DENY&taskToken={task_token}"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Recommended Action:*\n{analysis.get('recommended_action', 'N/A')} (Confidence: {analysis.get('confidence', 'N/A')})\n\n*Risk Level:* HIGH\n\n< {approve_link} | ✅ Approve >   < {deny_link} | ❌ Deny >"
            }
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

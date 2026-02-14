import json
import sys
import urllib.request

def send_test_notification(webhook_url):
    # Mimic the payload structure from the Lambda
    # Mimicking it
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Incident Requires Approval: 1234-5678",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*Status:*\nREQUIRES_APPROVAL"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Root Cause:*\nHigh memory pressure detected in container due to memory leak in application code."
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Recommended Action:*\nRESTART_SERVICE (Confidence: 0.95)"
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
            }
        ],
        "attachments": [
            {
                "color": "#ffcc00",
                "blocks": []
            }
        ]
    }

    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(message).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            print(f"Message sent! Status: {response.status}")
            print("Check your Slack channel.")
    except Exception as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_slack.py <YOUR_SLACK_WEBHOOK_URL>")
        sys.exit(1)
    
    send_test_notification(sys.argv[1])

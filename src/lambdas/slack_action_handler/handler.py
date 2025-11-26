import json
import logging
import os
import boto3
import urllib.parse
import hmac
import hashlib
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
sfn = boto3.client('stepfunctions')

TABLE_NAME = os.environ['APPROVALS_TABLE_NAME']
SLACK_SIGNING_SECRET = os.environ.get('SLACK_SIGNING_SECRET', '')

def verify_slack_signature(headers, body):
    if not SLACK_SIGNING_SECRET:
        logger.warning("SLACK_SIGNING_SECRET not set. Skipping signature verification.")
        return True
        
    timestamp = headers.get('x-slack-request-timestamp')
    signature = headers.get('x-slack-signature')
    
    if not timestamp or not signature:
        return False
        
    # Prevent replay attacks
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False
        
    sig_basestring = f"v0:{timestamp}:{body}".encode('utf-8')
    my_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode('utf-8'),
        sig_basestring,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(my_signature, signature)

def handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    
    # API Gateway Proxy Integration
    headers = event.get('headers', {})
    body = event.get('body', '')
    
    if event.get('isBase64Encoded'):
        import base64
        body = base64.b64decode(body).decode('utf-8')
    
    if not verify_slack_signature(headers, body):
        return {
            'statusCode': 401,
            'body': 'Invalid signature'
        }
        
    # Parse payload (x-www-form-urlencoded)
    # payload=%7B%22type%22%3A%22block_actions%22...
    parsed_body = urllib.parse.parse_qs(body)
    payload_json = parsed_body.get('payload', [''])[0]
    
    if not payload_json:
        return {'statusCode': 400, 'body': 'Missing payload'}
        
    payload = json.loads(payload_json)
    
    actions = payload.get('actions', [])
    if not actions:
        return {'statusCode': 200, 'body': ''}
        
    action = actions[0]
    approval_id = action.get('value')
    action_id = action.get('action_id') # approve_action or reject_action
    
    user = payload.get('user', {}).get('username', 'slack_user')
    
    # Fetch from DynamoDB
    table = dynamodb.Table(TABLE_NAME)
    response = table.get_item(Key={'approval_id': approval_id})
    item = response.get('Item')
    
    if not item:
        return {'statusCode': 404, 'body': 'Approval request not found'}
        
    if item.get('status') != 'PENDING':
        return {
            'statusCode': 200, 
            'body': json.dumps({'text': f"Request already processed: {item.get('status')}"})
        }
        
    task_token = item.get('taskToken')
    new_status = 'APPROVED' if action_id == 'approve_action' else 'REJECTED'
    
    # Update DynamoDB
    table.update_item(
        Key={'approval_id': approval_id},
        UpdateExpression="set #s = :s, approved_by = :u, approval_source = :src",
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={
            ':s': new_status,
            ':u': user,
            ':src': 'slack'
        }
    )
    
    # Resume Step Functions
    try:
        if new_status == 'APPROVED':
            sfn.send_task_success(
                taskToken=task_token,
                output=json.dumps({'status': 'APPROVED', 'approver': user, 'source': 'slack'})
            )
            message = "✅ Action Approved!"
        else:
            sfn.send_task_failure(
                taskToken=task_token,
                error='ManualRejection',
                cause=f'User {user} rejected via Slack'
            )
            message = "❌ Action Rejected."
            
        # Respond to Slack to update the message
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'text': message, 'replace_original': False})
        }
        
    except Exception as e:
        logger.error("Error resuming workflow: %s", e)
        return {
            'statusCode': 500,
            'body': 'Error resuming workflow'
        }

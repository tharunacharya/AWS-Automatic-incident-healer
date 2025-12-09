import json
import logging
import os
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
sfn = boto3.client('stepfunctions')

TABLE_NAME = os.environ['APPROVALS_TABLE_NAME']

from decimal import Decimal
from datetime import datetime
import time

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    
    http_method = event.get('requestContext', {}).get('http', {}).get('method')
    path_params = event.get('pathParameters', {})
    approval_id = path_params.get('approvalId')
    
    if not approval_id:
        return {'statusCode': 400, 'body': json.dumps({'error': 'Missing approvalId'})}
        
    table = dynamodb.Table(TABLE_NAME)
    
    if http_method == 'GET':
        response = table.get_item(Key={'approval_id': approval_id})
        item = response.get('Item')
        
        if not item:
            return {'statusCode': 404, 'body': json.dumps({'error': 'Not found'})}
            
        # Remove taskToken from response for security
        if 'taskToken' in item:
            del item['taskToken']

        # Fetch Incident Status for Real-time Updates
        incident_id = item.get('incident_id')
        incidents_table_name = os.environ.get('INCIDENTS_TABLE_NAME')
        
        if incident_id and incidents_table_name:
            try:
                inc_table = dynamodb.Table(incidents_table_name)
                # Incidents table has composite key (incident_id + timestamp). 
                # We query by Partition Key since we might not have the exact timestamp.
                inc_response = inc_table.query(
                    KeyConditionExpression=boto3.dynamodb.conditions.Key('incident_id').eq(incident_id)
                )
                inc_items = inc_response.get('Items', [])
                if inc_items:
                    # Expecting one, but take the latest if multiple
                    inc_item = inc_items[0] 
                    
                    # Merge specific fields into the response
                    item['incident_status'] = inc_item.get('status')
                    item['healing_status'] = inc_item.get('healing_status')
                    item['healing_result'] = inc_item.get('healing_result')
                    item['verification_result'] = inc_item.get('verification')
                    item['rollback_status'] = inc_item.get('rollback_status')
            except Exception as e:
                logger.error("Failed to fetch incident details: %s", e)
                # Continue without incident details rather than failing
            
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(item, cls=DecimalEncoder)
        }
        
    elif http_method == 'POST':
        # Get User Info from Cognito Authorizer
        claims = event.get('requestContext', {}).get('authorizer', {}).get('jwt', {}).get('claims', {})
        user_email = claims.get('email', 'unknown_user')
        
        body = json.loads(event.get('body', '{}'))
        action = body.get('action') # APPROVE or REJECT
        comment = body.get('comment', '')
        
        if action not in ['APPROVE', 'REJECT']:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid action'})}
            
        # Fetch item first to check expiry and taskToken
        response = table.get_item(Key={'approval_id': approval_id})
        item = response.get('Item')
        
        if not item:
            return {'statusCode': 404, 'body': json.dumps({'error': 'Not found'})}
            
        # Check Expiry
        import time
        if item.get('expires_at') and int(item.get('expires_at')) < int(time.time()):
             return {'statusCode': 410, 'body': json.dumps({'error': 'Approval request expired'})}
             
        task_token = item.get('taskToken')
        
        # Atomic Update with ConditionExpression to prevent race conditions
        try:
            table.update_item(
                Key={'approval_id': approval_id},
                UpdateExpression="set #s = :s, approved_by = :u, approval_source = :src, approved_at = :t, #c = :c",
                ConditionExpression="#s = :pending",
                ExpressionAttributeNames={'#s': 'status', '#c': 'comment'},
                ExpressionAttributeValues={
                    ':s': 'APPROVED' if action == 'APPROVE' else 'REJECTED',
                    ':u': user_email,
                    ':src': 'frontend',
                    ':t': datetime.now().isoformat(),
                    ':c': comment,
                    ':pending': 'PENDING'
                }
            )
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
             # Already processed
             return {'statusCode': 409, 'body': json.dumps({'error': 'Request already processed', 'status': item.get('status')})}
        
        # Resume Step Functions
        try:
            if action == 'APPROVE':
                sfn.send_task_success(
                    taskToken=task_token,
                    output=json.dumps({
                        'status': 'APPROVED', 
                        'approver': user_email, 
                        'source': 'frontend',
                        'comment': comment
                    })
                )
            else:
                sfn.send_task_failure(
                    taskToken=task_token,
                    error='ManualRejection',
                    cause=f'User {user_email} rejected via Frontend. Comment: {comment}'
                )
                
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'status': 'Success'})
            }
        except Exception as e:
            logger.error("Error resuming workflow: %s", e)
            # Note: DynamoDB was updated, but SFN failed. 
            # In a real system, we might want to rollback the DB update or retry.
            return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
            
    return {'statusCode': 405, 'body': 'Method Not Allowed'}

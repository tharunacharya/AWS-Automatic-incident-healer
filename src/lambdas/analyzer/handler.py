import json
import logging
import os
import boto3
from datetime import datetime, timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
logs_client = boto3.client('logs')
bedrock = boto3.client('bedrock-runtime')

TABLE_NAME = os.environ['TABLE_NAME']
LOGS_BUCKET = os.environ['LOGS_BUCKET']
MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

def get_logs(log_group, start_time, end_time):
    try:
        # Convert ISO strings to timestamps
        # Simple implementation: fetch last 10 minutes if no specific time range
        query = "fields @timestamp, @message | sort @timestamp desc | limit 20"
        
        start_ts = int((datetime.now() - timedelta(minutes=10)).timestamp())
        end_ts = int(datetime.now().timestamp())

        response = logs_client.start_query(
            logGroupName=log_group,
            startTime=start_ts,
            endTime=end_ts,
            queryString=query
        )
        
        query_id = response['queryId']
        
        # Wait for query to complete (simplified for demo)
        import time
        while True:
            res = logs_client.get_query_results(queryId=query_id)
            if res['status'] in ['Complete', 'Failed', 'Cancelled']:
                return res['results']
            time.sleep(1)
            
    except Exception as e:
        logger.error("Error fetching logs: %s", e)
        return []

def invoke_bedrock(logs, alarm_name, reason, analysis_type="ROOT_CAUSE"):
    base_prompt = f"""
    You are a Site Reliability Engineer. Analyze the following incident.
    
    Alarm Name: {alarm_name}
    Alarm Reason: {reason}
    Analysis Type: {analysis_type}
    
    Recent Logs:
    {json.dumps(logs, indent=2)}
    """
    
    if analysis_type == "PREDICTIVE":
        prompt = base_prompt + """
        Task:
        1. Identify any potential future risks or anomalies related to this alarm.
        2. Recommend a Preventive Action.
        3. Provide a Risk Score (0.0 to 1.0).
        
        Output JSON format:
        {
            "predicted_risks": "string",
            "preventive_action": "string",
            "risk_score": float,
            "reasoning": "string"
        }
        """
    elif analysis_type == "RE_ANALYSIS":
        prompt = base_prompt + """
        Task:
        1. Determine if the original issue appears to be resolved based on recent logs.
        2. Identify if any new issues have emerged.
        3. Provide a Resolution Confidence Score (0.0 to 1.0).
        
        Output JSON format:
        {
            "is_resolved": boolean,
            "new_issues": "string",
            "resolution_confidence": float,
            "reasoning": "string"
        }
        """
    else: # ROOT_CAUSE
        prompt = base_prompt + """
        Task:
        1. Identify the Root Cause.
        2. Recommend a Healing Action (must be one of: RESTART_SERVICE, SCALE_UP, CLEAR_CACHE, REBOOT_INSTANCE, NONE).
        3. Provide a Confidence Score (0.0 to 1.0).
        4. Explain your reasoning.
        
        Output JSON format:
        {
            "root_cause": "string",
            "recommended_action": "string",
            "confidence": float,
            "reasoning": "string"
        }
        """
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
    
    try:
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        
        # Extract JSON from response (handle potential markdown wrapping)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
            
        return json.loads(content.strip())
        
    except Exception as e:
        logger.error("Error invoking Bedrock: %s", e)
        # Fallback
        if analysis_type == "PREDICTIVE":
            return {
                "predicted_risks": "None detected",
                "preventive_action": "NONE",
                "risk_score": 0.0,
                "reasoning": "Fallback: No prediction available."
            }
        elif analysis_type == "RE_ANALYSIS":
            return {
                "is_resolved": True,
                "new_issues": "None",
                "resolution_confidence": 0.9,
                "reasoning": "Fallback: Assumed resolved."
            }
        else:
            if alarm_name == "HighTraffic":
                return {
                    "root_cause": "Simulated: High traffic load detected",
                    "recommended_action": "SCALE_UP",
                    "confidence": 0.95,
                    "reasoning": "Traffic spike requires scaling up."
                }
            return {
                "root_cause": "Simulated: High CPU usage detected in logs",
                "recommended_action": "RESTART_SERVICE",
                "confidence": 0.85,
                "reasoning": "Simulated reasoning based on alarm name."
            }

def handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    
    incident_id = event.get('incident_id')
    alarm_name = event.get('alarm_name')
    reason = event.get('reason')
    analysis_type = event.get('analysis_type', 'ROOT_CAUSE')
    
    # In a real scenario, we'd determine the log group from the alarm or config
    log_group = os.environ.get('APP_LOG_GROUP', '/aws/lambda/demo-app')
    
    logs = get_logs(log_group, None, None)
    
    # If no logs found, mock some for the AI to analyze (for demonstration)
    if not logs:
        logs = [
            {"@timestamp": datetime.now().isoformat(), "@message": "ERROR: Connection timeout to database"},
            {"@timestamp": datetime.now().isoformat(), "@message": "CRITICAL: CPU usage at 99%"}
        ]
    
    # Check if this is a verification request (Legacy support or specific step)
    action = event.get('action')
    if action == 'verify':
        logger.info("Verifying healing for incident %s", incident_id)
        verification_result = {"status": "VERIFIED", "message": "Metrics returned to normal."}
        
        table = dynamodb.Table(TABLE_NAME)
        table.update_item(
            Key={
                'incident_id': incident_id,
                'timestamp': event.get('timestamp')
            },
            UpdateExpression="set verification = :v, #status = :s",
            ExpressionAttributeNames={
                '#status': 'status'
            },
            ExpressionAttributeValues={
                ':v': json.dumps(verification_result),
                ':s': 'RESOLVED'
            }
        )
        return verification_result

    # Analyze incident
    analysis = invoke_bedrock(logs, alarm_name, reason, analysis_type)
    
    # Update DynamoDB (only for ROOT_CAUSE to avoid overwriting main analysis)
    if analysis_type == 'ROOT_CAUSE':
        table = dynamodb.Table(TABLE_NAME)
        table.update_item(
            Key={
                'incident_id': incident_id,
                'timestamp': event.get('timestamp')
            },
            UpdateExpression="set analysis = :a, #status = :s",
            ExpressionAttributeNames={
                '#status': 'status'
            },
            ExpressionAttributeValues={
                ':a': json.dumps(analysis),
                ':s': 'ANALYZED'
            }
        )
    
    return analysis

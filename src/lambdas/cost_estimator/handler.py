import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    
    # Mock logic for cost estimation
    # In a real scenario, this would query AWS Pricing API
    
    action = event.get('recommended_action', 'UNKNOWN')
    
    # Mock cost data
    costs = {
        'RESTART_SERVICE': 0.0,
        'SCALE_UP': 50.0, # Estimated monthly cost increase
        'CLEAR_CACHE': 0.0,
        'REBOOT_INSTANCE': 0.0
    }
    
    estimated_cost = costs.get(action, 100.0)
    
    # Determine risk level based on cost and action type
    risk_level = 'LOW'
    if estimated_cost > 20.0 or action in ['REBOOT_INSTANCE', 'DELETE_RESOURCE']:
        risk_level = 'HIGH'
        
    return {
        'estimated_cost': estimated_cost,
        'risk_level': risk_level,
        'currency': 'USD'
    }

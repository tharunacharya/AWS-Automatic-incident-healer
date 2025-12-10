import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    
    # Mock logic for cost estimation
    # In a real scenario, this would query AWS Pricing API
    
    import random
    
    # Extract action from nested 'analysis' if present (step functions structure)
    # or direct root level (test events)
    analysis = event.get('analysis', {})
    action = analysis.get('recommended_action')
    
    if not action:
        action = event.get('recommended_action', 'UNKNOWN')
    
    # Mock cost data (Base costs)
    base_costs = {
        'RESTART_SERVICE': 0.50,   # Nominal compute for restart
        'SCALE_UP': 45.0,          # EC2/Fargate hourly/monthly rate
        'CLEAR_CACHE': 0.10,       # Service call
        'REBOOT_INSTANCE': 0.0,    # Free usually
        'NONE': 0.0
    }
    
    base_cost = base_costs.get(action, 100.0)
    
    # Add some realistic variance (±10%)
    variance = base_cost * 0.1 * (random.random() - 0.5)
    estimated_cost = round(max(0, base_cost + variance), 2)
    
    # Determine risk level based on cost and action type
    risk_level = 'LOW'
    if estimated_cost > 20.0 or action in ['REBOOT_INSTANCE', 'DELETE_RESOURCE']:
        risk_level = 'HIGH'
        
    return {
        'estimated_cost': estimated_cost,
        'risk_level': risk_level,
        'currency': 'USD'
    }

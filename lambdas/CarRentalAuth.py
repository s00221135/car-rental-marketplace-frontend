import json

def generate_policy(principal_id, effect, resource):
    """Helper to build an IAM policy document."""
    auth_response = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        }
    }
    return auth_response

def lambda_handler(event, context):
    """
    event: {
      "type": "TOKEN",
      "authorizationToken": "Bearer <token>",
      "methodArn":    "arn:aws:execute-api:…"
    }
    """
    # Grab the token from the incoming header
    auth_header = event.get('authorizationToken', '')
    parts = auth_header.split()
    token = parts[1] if len(parts) == 2 and parts[0].lower() == 'bearer' else ''

    # Simple check against a hard‑coded token
    if token != "super-secret-token":
        # API Gateway will return a 401
        raise Exception('Unauthorized')

    # If we get here, token is valid → allow the request
    return generate_policy(principal_id='user123', effect='Allow', resource=event['methodArn'])

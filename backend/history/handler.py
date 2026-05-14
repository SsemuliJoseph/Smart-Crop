"""
backend/history/handler.py
===========================
Lambda function for retrieving detection history for a farmer.

Author: Tukahirwa Clinton (feature/backend)
Project: PotatoGuard - Group 7, BSc Computer Science 2024/2025
"""

import json
import os
import boto3

DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'potatoguard-detections')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

import sys
sys.path.insert(0, '/var/task')
try:
    from database.dynamo_helper import get_farmer_history
except ImportError:
    from dynamo_helper import get_farmer_history


def lambda_handler(event, context):
    """
    Lambda handler for retrieving farmer detection history.
    
    Path parameter: farmerId
    
    Response:
    [
        {
            "detectionId": "uuid",
            "disease": "Healthy",
            "confidence": 0.99,
            "timestamp": "2025-05-14T10:30:00Z",
            "imageUrl": "https://..."
        },
        ...
    ]
    """
    try:
        farmer_id = event.get('pathParameters', {}).get('farmerId')
        
        if not farmer_id:
            return error_response(400, "Missing farmerId parameter")
        
        # Query DynamoDB for all records for this farmer
        records = get_farmer_history(DYNAMODB_TABLE, farmer_id)
        
        return success_response(records)
        
    except Exception as e:
        print(f"Error retrieving history: {str(e)}")
        return error_response(500, f"Failed to retrieve history: {str(e)}")


def success_response(data):
    """Return a successful 200 response."""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(data)
    }


def error_response(status_code, message):
    """Return an error response."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': message})
    }

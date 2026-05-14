"""
backend/report/handler.py
==========================
Lambda function for retrieving a single detection report.

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
    from database.dynamo_helper import get_detection
except ImportError:
    from dynamo_helper import get_detection


def lambda_handler(event, context):
    """
    Lambda handler for retrieving a single detection report.
    
    Path parameters: detectionId
    Query parameter: timestamp (optional)
    
    Response:
    {
        "detectionId": "uuid",
        "farmerId": "farmer001",
        "disease": "Late Blight",
        "confidence": 0.96,
        "treatment": "...",
        "imageUrl": "https://...",
        "timestamp": "2025-05-14T10:30:00Z"
    }
    """
    try:
        path_params = event.get('pathParameters', {})
        detection_id = path_params.get('detectionId')
        
        if not detection_id:
            return error_response(400, "Missing detectionId parameter")
        
        # For simplicity, we'll do a table scan (not ideal in production)
        # In production, you might store timestamp separately or use a GSI
        table = dynamodb.Table(DYNAMODB_TABLE)
        
        # Scan for the detection (better would be to query if timestamp is known)
        response = table.scan(
            FilterExpression='detectionId = :id',
            ExpressionAttributeValues={
                ':id': detection_id
            }
        )
        
        if not response.get('Items'):
            return error_response(404, f"Detection {detection_id} not found")
        
        record = response['Items'][0]
        return success_response(record)
        
    except Exception as e:
        print(f"Error retrieving report: {str(e)}")
        return error_response(500, f"Failed to retrieve report: {str(e)}")


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

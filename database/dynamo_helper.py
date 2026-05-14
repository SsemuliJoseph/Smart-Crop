"""
database/dynamo_helper.py
=========================
Reusable DynamoDB helper functions for PotatoGuard.
Provides functions to save, retrieve, and query detection records.

Author: Namata Juliet (feature/database)
Project: PotatoGuard - Group 7, BSc Computer Science 2024/2025
"""

import boto3
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

def get_table(table_name):
    """Get reference to DynamoDB table."""
    return dynamodb.Table(table_name)


def save_detection(table_name, detection_dict):
    """
    Save a new detection record to DynamoDB.
    
    Args:
        table_name (str): Name of DynamoDB table
        detection_dict (dict): Detection record with fields:
            - detectionId (str): Unique ID
            - farmerId (str): Farmer identifier
            - disease (str): Disease classification
            - confidence (float): Model confidence 0-1
            - treatment (str): Treatment advice
            - imageUrl (str): S3 URL of image
            - timestamp (str): ISO format timestamp
    
    Returns:
        str: The detectionId if successful, None if failed
    """
    try:
        table = get_table(table_name)
        table.put_item(Item=detection_dict)
        print(f"✓ Saved detection {detection_dict['detectionId']} for farmer {detection_dict['farmerId']}")
        return detection_dict['detectionId']
    except Exception as e:
        print(f"✗ Error saving detection: {e}")
        return None


def get_detection(table_name, detection_id, timestamp):
    """
    Retrieve a single detection record by ID and timestamp.
    
    Args:
        table_name (str): Name of DynamoDB table
        detection_id (str): Primary key (partition key)
        timestamp (str): Sort key
    
    Returns:
        dict: Detection record or None if not found
    """
    try:
        table = get_table(table_name)
        response = table.get_item(
            Key={
                'detectionId': detection_id,
                'timestamp': timestamp
            }
        )
        return response.get('Item')
    except Exception as e:
        print(f"✗ Error retrieving detection: {e}")
        return None


def get_farmer_history(table_name, farmer_id):
    """
    Retrieve all detection records for a farmer, sorted by timestamp (newest first).
    
    Args:
        table_name (str): Name of DynamoDB table
        farmer_id (str): Farmer identifier
    
    Returns:
        list: List of detection records, newest first. Empty list if none found.
    """
    try:
        table = get_table(table_name)
        # Query using Global Secondary Index on farmerId
        response = table.query(
            IndexName='farmerId-index',
            KeyConditionExpression=Key('farmerId').eq(farmer_id),
            ScanIndexForward=False  # Sort descending (newest first)
        )
        items = response.get('Items', [])
        print(f"✓ Retrieved {len(items)} records for farmer {farmer_id}")
        return items
    except Exception as e:
        print(f"✗ Error retrieving farmer history: {e}")
        return []


def delete_detection(table_name, detection_id, timestamp):
    """
    Delete a detection record by ID and timestamp.
    
    Args:
        table_name (str): Name of DynamoDB table
        detection_id (str): Primary key
        timestamp (str): Sort key
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        table = get_table(table_name)
        table.delete_item(
            Key={
                'detectionId': detection_id,
                'timestamp': timestamp
            }
        )
        print(f"✓ Deleted detection {detection_id}")
        return True
    except Exception as e:
        print(f"✗ Error deleting detection: {e}")
        return False

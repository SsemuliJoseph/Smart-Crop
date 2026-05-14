"""
tests/test_history.py
=====================
Tests for the PotatoGuard history Lambda function (backend/history/handler.py).
Uses pytest + moto to mock DynamoDB. No real AWS account needed.

Author : Katusiime Moreen  (feature/testing)
Project: PotatoGuard - Group 7, BSc Computer Science 2024/2025
"""

import json
import os
import sys
import uuid
from datetime import datetime, timedelta

import boto3
import pytest
from moto import mock_dynamodb

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("DYNAMODB_TABLE", "potatoguard-detections")
os.environ.setdefault("AWS_REGION_NAME", "us-east-1")


def _create_dynamo_table():
    """Create the mock DynamoDB table required by the history handler."""
    ddb = boto3.resource("dynamodb", region_name="us-east-1")
    table = ddb.create_table(
        TableName="potatoguard-detections",
        KeySchema=[
            {"AttributeName": "detectionId", "KeyType": "HASH"},
            {"AttributeName": "timestamp", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "detectionId", "AttributeType": "S"},
            {"AttributeName": "timestamp", "AttributeType": "S"},
            {"AttributeName": "farmerId", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "farmerId-index",
                "KeySchema": [{"AttributeName": "farmerId", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    return table


def _put_detection(table, farmer_id, disease, minutes_ago=0):
    """
    Insert a dummy detection record into the mock table.
    minutes_ago lets us control the timestamp to verify sort order.
    """
    ts = (datetime.utcnow() - timedelta(minutes=minutes_ago)).isoformat()
    detection_id = str(uuid.uuid4())
    table.put_item(
        Item={
            "detectionId": detection_id,
            "timestamp": ts,
            "farmerId": farmer_id,
            "disease": disease,
            "confidence": 0.95,
            "treatment": "Apply fungicide.",
            "imageUrl": f"https://s3.amazonaws.com/potatoguard-images/{detection_id}.png",
        }
    )
    return detection_id, ts


def _history_event(farmer_id):
    """Build a fake API Gateway proxy event for GET /history/{farmerId}."""
    return {
        "httpMethod": "GET",
        "path": f"/history/{farmer_id}",
        "pathParameters": {"farmerId": farmer_id},
        "body": None,
    }


@mock_dynamodb
def test_empty_history_returns_200_and_empty_list():
    """
    WHAT IT CHECKS:
    A brand-new farmer who has never scanned a leaf should receive HTTP 200
    and an empty list not an error or a 404.
    """
    _create_dynamo_table()
    from backend.history import handler
    event = _history_event("brand_new_farmer_999")
    response = handler.lambda_handler(event, {})
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert isinstance(body, list), "Body should be a list"
    assert len(body) == 0, f"Expected empty list, got {body}"


@mock_dynamodb
def test_history_returns_correct_records():
    """
    WHAT IT CHECKS:
    After saving 2 detection records for a specific farmer, the history
    endpoint must return exactly those 2 records neither more nor less.
    """
    table = _create_dynamo_table()
    farmer_id = "farmer_test_002"
    id1, _ = _put_detection(table, farmer_id, "Late Blight", minutes_ago=10)
    id2, _ = _put_detection(table, farmer_id, "Healthy", minutes_ago=5)
    from backend.history import handler
    event = _history_event(farmer_id)
    response = handler.lambda_handler(event, {})
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert len(body) == 2, f"Expected 2 records, got {len(body)}"
    returned_ids = {r["detectionId"] for r in body}
    assert id1 in returned_ids, f"Record {id1} missing from response"
    assert id2 in returned_ids, f"Record {id2} missing from response"


@mock_dynamodb
def test_history_sorted_newest_first():
    """
    WHAT IT CHECKS:
    The history list must be sorted by timestamp in descending order
    so the most recent scan appears first in the list.
    """
    table = _create_dynamo_table()
    farmer_id = "farmer_sort_003"
    _put_detection(table, farmer_id, "Early Blight", minutes_ago=30)
    _put_detection(table, farmer_id, "Late Blight", minutes_ago=20)
    _put_detection(table, farmer_id, "Healthy", minutes_ago=5)
    from backend.history import handler
    event = _history_event(farmer_id)
    response = handler.lambda_handler(event, {})
    body = json.loads(response["body"])
    assert len(body) == 3
    timestamps = [r["timestamp"] for r in body]
    for i in range(len(timestamps) - 1):
        assert timestamps[i] >= timestamps[i + 1], (
            f"Records not sorted newest-first at position {i}: "
            f"{timestamps[i]} should be >= {timestamps[i+1]}"
        )

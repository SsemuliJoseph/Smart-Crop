"""
tests/test_detect.py
====================
Tests for the PotatoGuard detect Lambda function (backend/detect/handler.py).
Uses pytest + moto to mock AWS services so NO real AWS account is needed.

Author : Katusiime Moreen  (feature/testing)
Project: PotatoGuard - Group 7, BSc Computer Science 2024/2025
"""

import base64
import io
import json
import os
import sys

import boto3
import pytest
from moto import mock_dynamodb, mock_s3
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("DYNAMODB_TABLE", "potatoguard-detections")
os.environ.setdefault("S3_BUCKET", "potatoguard-images")
os.environ.setdefault("SAGEMAKER_ENDPOINT", "potatoguard-endpoint")
os.environ.setdefault("AWS_REGION_NAME", "us-east-1")


def _make_base64_image(width=224, height=224):
    """
    Create a tiny solid-colour PNG image and return it as a base64 string.
    This is used as the image_base64 payload in test requests.
    """
    img = Image.new("RGB", (width, height), color=(34, 139, 34))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _detect_event(image_b64=None, farmer_id="farmer001"):
    """
    Return a fake API Gateway proxy event for the detect endpoint.
    Pass image_b64=None or farmer_id=None to simulate missing fields.
    """
    body = {}
    if image_b64 is not None:
        body["image_base64"] = image_b64
    if farmer_id is not None:
        body["farmer_id"] = farmer_id
    return {
        "httpMethod": "POST",
        "path": "/detect",
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
        "isBase64Encoded": False,
    }


def _create_aws_resources():
    """Create the mock S3 bucket and DynamoDB table that the handler depends on."""
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="potatoguard-images")

    ddb = boto3.resource("dynamodb", region_name="us-east-1")
    ddb.create_table(
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


@mock_s3
@mock_dynamodb
def test_detect_returns_200_for_valid_input():
    """
    WHAT IT CHECKS:
    When the Lambda receives a valid request with a proper base64 image
    and farmer_id, it should return HTTP 200 and a body that contains
    the fields disease, confidence, and treatment.
    """
    _create_aws_resources()
    from backend.detect import handler
    event = _detect_event(image_b64=_make_base64_image())
    response = handler.lambda_handler(event, {})
    assert response["statusCode"] == 200, f"Expected 200, got {response['statusCode']}"
    body = json.loads(response["body"])
    assert "disease" in body, "Response must contain disease"
    assert "confidence" in body, "Response must contain confidence"
    assert "treatment" in body, "Response must contain treatment"


@mock_s3
@mock_dynamodb
def test_detect_returns_400_if_image_missing():
    """
    WHAT IT CHECKS:
    When the request body is missing the image_base64 field,
    the Lambda should reject it with HTTP 400 Bad Request.
    """
    _create_aws_resources()
    from backend.detect import handler
    event = _detect_event(image_b64=None, farmer_id="farmer001")
    response = handler.lambda_handler(event, {})
    assert response["statusCode"] == 400, f"Expected 400, got {response['statusCode']}"


@mock_s3
@mock_dynamodb
def test_detect_returns_400_if_farmer_id_missing():
    """
    WHAT IT CHECKS:
    When the request body is missing the farmer_id field,
    the Lambda should reject it with HTTP 400 Bad Request.
    """
    _create_aws_resources()
    from backend.detect import handler
    event = _detect_event(image_b64=_make_base64_image(), farmer_id=None)
    response = handler.lambda_handler(event, {})
    assert response["statusCode"] == 400, f"Expected 400, got {response['statusCode']}"


@mock_s3
@mock_dynamodb
def test_confidence_is_between_0_and_1():
    """
    WHAT IT CHECKS:
    The confidence value returned in the response must be a number
    between 0.0 and 1.0 inclusive representing a probability score.
    """
    _create_aws_resources()
    from backend.detect import handler
    event = _detect_event(image_b64=_make_base64_image())
    response = handler.lambda_handler(event, {})
    body = json.loads(response["body"])
    confidence = float(body.get("confidence", -1))
    assert 0.0 <= confidence <= 1.0, f"Confidence {confidence} is not in range 0 to 1"


@mock_s3
@mock_dynamodb
def test_disease_is_valid_category():
    """
    WHAT IT CHECKS:
    The disease field in the response must be one of the four valid
    disease categories that PotatoGuard is trained to detect.
    """
    _create_aws_resources()
    from backend.detect import handler
    valid_diseases = {"Healthy", "Late Blight", "Early Blight", "Bacterial Wilt"}
    event = _detect_event(image_b64=_make_base64_image())
    response = handler.lambda_handler(event, {})
    body = json.loads(response["body"])
    disease = body.get("disease", "")
    assert disease in valid_diseases, (
        f"{disease} is not a recognised disease category. Valid options: {valid_diseases}"
    )

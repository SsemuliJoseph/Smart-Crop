"""
tests/test_database.py
======================
Tests for the PotatoGuard database helper modules:
  - database/dynamo_helper.py  (DynamoDB operations)
  - database/s3_helper.py      (S3 image storage)

All AWS calls are intercepted by moto. No real AWS account needed.

Author : Katusiime Moreen  (feature/testing)
Project: PotatoGuard - Group 7, BSc Computer Science 2024/2025
"""

import io
import os
import sys
import uuid

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
os.environ.setdefault("AWS_REGION_NAME", "us-east-1")


def _create_dynamo_table():
    """Spin up the mock DynamoDB table that the helper functions expect."""
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


def _create_s3_bucket():
    """Create the mock S3 bucket."""
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="potatoguard-images")


def _sample_detection(farmer_id="farmer001"):
    """Return a sample detection dictionary ready to pass to save_detection()."""
    return {
        "detectionId": str(uuid.uuid4()),
        "farmerId": farmer_id,
        "timestamp": "2025-01-15T10:30:00.000000",
        "disease": "Late Blight",
        "confidence": 0.93,
        "treatment": "Apply Mancozeb fungicide immediately.",
        "imageUrl": "https://s3.amazonaws.com/potatoguard-images/test.png",
        "imageS3Key": "test.png",
    }


def _make_image_bytes():
    """Return a tiny 32x32 PNG image as raw bytes for S3 upload tests."""
    img = Image.new("RGB", (32, 32), color=(0, 128, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@mock_dynamodb
def test_save_and_retrieve_detection():
    """
    WHAT IT CHECKS:
    Save a detection record using save_detection() then retrieve it with
    get_detection(). All fields that were saved must come back unchanged.
    """
    _create_dynamo_table()
    from database.dynamo_helper import save_detection, get_detection
    record = _sample_detection()
    detection_id = save_detection(record)
    assert detection_id is not None, "save_detection() should return a detectionId"
    retrieved = get_detection(detection_id)
    assert retrieved is not None, "get_detection() should return the saved record"
    assert retrieved["disease"] == record["disease"]
    assert retrieved["farmerId"] == record["farmerId"]
    assert float(retrieved["confidence"]) == pytest.approx(record["confidence"])


@mock_dynamodb
def test_get_farmer_history_returns_all_records():
    """
    WHAT IT CHECKS:
    After saving 3 detection records for the same farmer,
    get_farmer_history() must return all 3 of them.
    """
    _create_dynamo_table()
    from database.dynamo_helper import save_detection, get_farmer_history
    farmer_id = "farmer_history_test"
    saved_ids = set()
    for disease in ["Healthy", "Late Blight", "Early Blight"]:
        rec = _sample_detection(farmer_id)
        rec["disease"] = disease
        did = save_detection(rec)
        saved_ids.add(did)
    history = get_farmer_history(farmer_id)
    assert len(history) == 3, f"Expected 3 records, got {len(history)}"
    returned_ids = {r["detectionId"] for r in history}
    assert saved_ids == returned_ids, "Returned IDs do not match saved IDs"


@mock_dynamodb
def test_delete_detection_removes_record():
    """
    WHAT IT CHECKS:
    After saving a record and then calling delete_detection(),
    calling get_detection() for that same ID should return None.
    """
    _create_dynamo_table()
    from database.dynamo_helper import save_detection, get_detection, delete_detection
    record = _sample_detection()
    detection_id = save_detection(record)
    result = delete_detection(detection_id)
    assert result is True, "delete_detection() should return True on success"
    retrieved_after_delete = get_detection(detection_id)
    assert retrieved_after_delete is None, (
        "Record should not exist after deletion but get_detection() returned data."
    )


@mock_s3
def test_upload_image_returns_url():
    """
    WHAT IT CHECKS:
    Calling upload_image() with raw image bytes should store the file in S3
    and return a non-empty URL string pointing to that image.
    """
    _create_s3_bucket()
    from database.s3_helper import upload_image
    image_bytes = _make_image_bytes()
    filename = f"test_{uuid.uuid4()}.png"
    url = upload_image(image_bytes, filename)
    assert url is not None, "upload_image() should return a URL"
    assert isinstance(url, str) and len(url) > 0, "Returned URL must be a non-empty string"
    assert "potatoguard-images" in url or filename in url, (
        "URL should reference the bucket or filename"
    )

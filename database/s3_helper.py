"""
database/s3_helper.py
=====================
Reusable S3 helper functions for PotatoGuard.
Provides functions to upload, retrieve, and manage leaf images.

Author: Namata Juliet (feature/database)
Project: PotatoGuard - Group 7, BSc Computer Science 2024/2025
"""

import boto3
import uuid
from botocore.exceptions import ClientError

# Initialize S3 client
s3_client = boto3.client('s3')


def upload_image(bucket_name, image_bytes, filename=None):
    """
    Upload image bytes to S3 bucket.
    
    Args:
        bucket_name (str): S3 bucket name
        image_bytes (bytes): Image file content
        filename (str): Optional filename. If None, generates UUID-based name.
    
    Returns:
        str: Public S3 URL of uploaded image or None if failed
    """
    try:
        if filename is None:
            filename = f"leaf_{uuid.uuid4()}.jpg"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=image_bytes,
            ContentType='image/jpeg'
        )
        
        url = f"https://{bucket_name}.s3.amazonaws.com/{filename}"
        print(f"✓ Uploaded image to S3: {filename}")
        return url
    except ClientError as e:
        print(f"✗ Error uploading image: {e}")
        return None


def generate_presigned_url(bucket_name, s3_key, expiry_seconds=3600):
    """
    Generate a temporary presigned URL for downloading an image.
    
    Args:
        bucket_name (str): S3 bucket name
        s3_key (str): Object key (filename)
        expiry_seconds (int): URL expiry time in seconds (default 1 hour)
    
    Returns:
        str: Presigned URL or None if failed
    """
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': s3_key},
            ExpiresIn=expiry_seconds
        )
        print(f"✓ Generated presigned URL for {s3_key}")
        return url
    except ClientError as e:
        print(f"✗ Error generating presigned URL: {e}")
        return None


def delete_image(bucket_name, s3_key):
    """
    Delete an image from S3 bucket.
    
    Args:
        bucket_name (str): S3 bucket name
        s3_key (str): Object key (filename)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
        print(f"✓ Deleted image from S3: {s3_key}")
        return True
    except ClientError as e:
        print(f"✗ Error deleting image: {e}")
        return False


def list_farmer_images(bucket_name, farmer_id):
    """
    List all S3 object keys for images belonging to a farmer.
    Assumes images are stored with farmer_id as prefix.
    
    Args:
        bucket_name (str): S3 bucket name
        farmer_id (str): Farmer identifier (used as prefix)
    
    Returns:
        list: List of S3 object keys or empty list if none found
    """
    try:
        prefix = f"{farmer_id}/"
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix
        )
        
        keys = []
        if 'Contents' in response:
            keys = [obj['Key'] for obj in response['Contents']]
        
        print(f"✓ Found {len(keys)} images for farmer {farmer_id}")
        return keys
    except ClientError as e:
        print(f"✗ Error listing farmer images: {e}")
        return []

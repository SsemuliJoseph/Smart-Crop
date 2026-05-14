"""
backend/detect/handler.py
==========================
Lambda function for disease detection.
Receives a base64 encoded leaf image and returns disease classification.

Author: Tukahirwa Clinton (feature/backend)
Project: PotatoGuard - Group 7, BSc Computer Science 2024/2025
"""

import json
import base64
import uuid
import os
from datetime import datetime
import boto3
from PIL import Image
import io
import numpy as np

# Environment variables
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'potatoguard-detections')
S3_BUCKET = os.environ.get('S3_BUCKET', 'potatoguard-images')
SAGEMAKER_ENDPOINT = os.environ.get('SAGEMAKER_ENDPOINT', 'potatoguard-endpoint')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# AWS clients
s3_client = boto3.client('s3', region_name=AWS_REGION)
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
sagemaker_client = boto3.client('sagemaker-runtime', region_name=AWS_REGION)

# Import database helpers
import sys
sys.path.insert(0, '/var/task')
try:
    from database.dynamo_helper import save_detection
    from database.s3_helper import upload_image
except ImportError:
    # For local testing
    from dynamo_helper import save_detection
    from s3_helper import upload_image

# Disease classes and treatment advice
DISEASE_CLASSES = {
    0: {"name": "Healthy", "treatment": "Your plant is healthy! Keep monitoring weekly."},
    1: {"name": "Late Blight", "treatment": "Apply fungicide (Mancozeb or Chlorothalonil) immediately. Remove infected leaves."},
    2: {"name": "Early Blight", "treatment": "Apply copper-based fungicide. Improve air circulation between plants."},
    3: {"name": "Bacterial Wilt", "treatment": "Remove and destroy infected plants. Do not replant in same soil for 2 seasons."}
}


def lambda_handler(event, context):
    """
    Lambda handler for disease detection.
    
    Request body:
    {
        "image_base64": "<base64_encoded_image>",
        "farmer_id": "farmer001"
    }
    
    Response:
    {
        "statusCode": 200,
        "body": {
            "disease": "Late Blight",
            "confidence": 0.96,
            "treatment": "...",
            "imageUrl": "https://...",
            "detectionId": "uuid",
            "farmerId": "farmer001"
        }
    }
    """
    try:
        # Step 1: Parse and validate request
        body = json.loads(event.get('body', '{}'))
        image_base64 = body.get('image_base64')
        farmer_id = body.get('farmer_id')
        
        if not image_base64 or not farmer_id:
            return error_response(400, "Missing image_base64 or farmer_id")
        
        # Step 2: Decode base64 image
        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception as e:
            return error_response(400, f"Invalid base64 image: {str(e)}")
        
        # Step 3: Generate unique filename
        detection_id = str(uuid.uuid4())
        filename = f"{farmer_id}/{detection_id}.jpg"
        
        # Step 4: Upload to S3
        image_url = upload_image(S3_BUCKET, image_bytes, filename)
        if not image_url:
            return error_response(500, "Failed to upload image to S3")
        
        # Step 5: Preprocess image for CNN
        try:
            processed_image = preprocess_image(image_bytes)
        except Exception as e:
            return error_response(500, f"Failed to preprocess image: {str(e)}")
        
        # Step 6: Call SageMaker endpoint
        try:
            prediction = invoke_sagemaker_endpoint(processed_image)
            disease_index = prediction['disease_index']
            confidence = float(prediction['confidence'])
        except Exception as e:
            return error_response(500, f"Failed to invoke SageMaker: {str(e)}")
        
        # Step 7-8: Map to disease name and get treatment
        disease_info = DISEASE_CLASSES.get(disease_index, DISEASE_CLASSES[0])
        disease_name = disease_info['name']
        treatment = disease_info['treatment']
        
        # Step 9-10: Save to DynamoDB
        timestamp = datetime.utcnow().isoformat() + "Z"
        detection_record = {
            'detectionId': detection_id,
            'timestamp': timestamp,
            'farmerId': farmer_id,
            'disease': disease_name,
            'confidence': confidence,
            'treatment': treatment,
            'imageUrl': image_url,
            'imageS3Key': filename
        }
        
        save_detection(DYNAMODB_TABLE, detection_record)
        
        # Step 11: Return response
        return success_response({
            'disease': disease_name,
            'confidence': confidence,
            'treatment': treatment,
            'imageUrl': image_url,
            'detectionId': detection_id,
            'farmerId': farmer_id
        })
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return error_response(500, f"Internal server error: {str(e)}")


def preprocess_image(image_bytes):
    """
    Preprocess image for CNN: resize to 224x224, normalize, expand dimensions.
    
    Returns:
        numpy array: Image ready for model input, shape (1, 224, 224, 3)
    """
    img = Image.open(io.BytesIO(image_bytes))
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize to 224x224
    img = img.resize((224, 224))
    
    # Convert to numpy array
    img_array = np.array(img, dtype=np.float32)
    
    # Normalize to 0-1 range
    img_array = img_array / 255.0
    
    # Expand dimensions: (224, 224, 3) -> (1, 224, 224, 3)
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array


def invoke_sagemaker_endpoint(image_array):
    """
    Invoke SageMaker endpoint for prediction.
    
    Returns:
        dict: {"disease_index": int, "confidence": float}
    """
    # Convert numpy array to bytes for SageMaker
    payload = image_array.astype(np.float32).tobytes()
    
    response = sagemaker_client.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT,
        ContentType='application/octet-stream',
        Body=payload
    )
    
    # Parse response
    result = json.loads(response['Body'].read().decode('utf-8'))
    
    # Handle different response formats
    if isinstance(result, dict):
        if 'predictions' in result:
            predictions = result['predictions'][0]
            # Find max probability and its index
            probabilities = predictions if isinstance(predictions, list) else [predictions]
            disease_index = int(np.argmax(probabilities))
            confidence = float(probabilities[disease_index])
        else:
            disease_index = int(result.get('class', 0))
            confidence = float(result.get('confidence', 0.5))
    else:
        # Assume result is list of probabilities
        probabilities = list(result) if hasattr(result, '__iter__') else [result]
        disease_index = int(np.argmax(probabilities))
        confidence = float(probabilities[disease_index])
    
    return {
        'disease_index': min(disease_index, 3),  # Ensure within range
        'confidence': min(confidence, 1.0)
    }


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
    """Return an error response with given status code."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': message})
    }

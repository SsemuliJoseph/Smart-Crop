"""
PotatoGuard SageMaker Deployment Script
Converts trained model to SavedModel format, uploads to S3, and deploys to SageMaker
Provides inference endpoint for real-time disease prediction
"""

import os
import json
import boto3
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from PIL import Image
import sagemaker
from sagemaker.tensorflow import TensorFlowModel
from datetime import datetime


def convert_h5_to_savedmodel(h5_model_path='./potatoguard_model.h5', 
                             savedmodel_dir='./potatoguard_savedmodel'):
    """
    Convert trained Keras model from H5 format to TensorFlow SavedModel format
    
    Why convert?
    - H5 format is Keras-specific and older
    - SavedModel is TensorFlow's standard format for production
    - Better compatibility with SageMaker and production systems
    - Supports distributed training and serving
    - More flexible for different deployment scenarios
    
    What happens?
    - Loads the .h5 model file (contains weights and architecture)
    - Exports to SavedModel format (creates a directory structure)
    - SavedModel includes: assets/, variables/, saved_model.pb
    
    Args:
        h5_model_path: Path to the saved .h5 model file
        savedmodel_dir: Directory to save the converted SavedModel
    
    Returns:
        Path to the SavedModel directory
    """
    
    print("="*60)
    print("CONVERTING MODEL FROM H5 TO SAVEDMODEL FORMAT")
    print("="*60)
    
    # Check if the H5 model file exists
    if not os.path.exists(h5_model_path):
        raise FileNotFoundError(f"Model file not found: {h5_model_path}")
    
    # Load the H5 model
    print(f"Loading H5 model from {h5_model_path}...")
    model = load_model(h5_model_path)
    
    # Create output directory if it doesn't exist
    # If directory already exists, remove it and create fresh
    if os.path.exists(savedmodel_dir):
        import shutil
        shutil.rmtree(savedmodel_dir)
    os.makedirs(savedmodel_dir, exist_ok=True)
    
    # Save model in SavedModel format
    print(f"Converting and saving to SavedModel format...")
    model.save(savedmodel_dir)
    
    print(f"✓ Model successfully converted to {savedmodel_dir}")
    
    return savedmodel_dir


def upload_model_to_s3(savedmodel_dir='./potatoguard_savedmodel',
                       bucket_name='potatoguard-models',
                       model_prefix='potato-disease-model'):
    """
    Upload the SavedModel to AWS S3 bucket
    
    Why S3?
    - SageMaker needs to access the model from S3 during deployment
    - S3 is AWS's object storage service (like a cloud drive)
    - Secure and scalable storage
    
    Steps this function performs:
    1. Create S3 client (connection to AWS)
    2. Check if bucket exists, create if needed
    3. Upload all SavedModel files to S3
    4. Return the S3 URI (address) of the model
    
    Args:
        savedmodel_dir: Path to SavedModel directory on local disk
        bucket_name: S3 bucket name (will be created if doesn't exist)
        model_prefix: S3 path prefix for the model (folder structure)
    
    Returns:
        Tuple of (s3_model_uri, bucket_name) for use in SageMaker
    """
    
    print("\n" + "="*60)
    print("UPLOADING MODEL TO S3")
    print("="*60)
    
    # Create S3 client - this is how we interact with AWS S3
    s3_client = boto3.client('s3')
    
    # Check if bucket already exists
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✓ S3 bucket '{bucket_name}' already exists")
    except:
        # Bucket doesn't exist, so create it
        print(f"Creating S3 bucket '{bucket_name}'...")
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"✓ S3 bucket created: {bucket_name}")
    
    # Upload SavedModel files to S3
    print(f"Uploading model files to s3://{bucket_name}/{model_prefix}/")
    
    uploaded_count = 0
    
    # Walk through the SavedModel directory structure
    # SavedModel has: assets/, variables/, and saved_model.pb
    for root, dirs, files in os.walk(savedmodel_dir):
        for file in files:
            # Get full local file path
            local_file_path = os.path.join(root, file)
            
            # Construct S3 key (path in bucket)
            # Example: "potato-disease-model/variables/variables.data-00000-of-00001"
            relative_path = os.path.relpath(local_file_path, savedmodel_dir)
            s3_key = f"{model_prefix}/{relative_path}"
            
            # Upload file to S3
            s3_client.upload_file(local_file_path, bucket_name, s3_key)
            uploaded_count += 1
    
    print(f"✓ Uploaded {uploaded_count} files to S3")
    
    # Return S3 URI of the model
    # This is the address SageMaker uses to download the model
    s3_model_uri = f"s3://{bucket_name}/{model_prefix}"
    print(f"✓ Model S3 URI: {s3_model_uri}")
    
    return s3_model_uri, bucket_name


def create_and_deploy_sagemaker_endpoint(s3_model_uri,
                                         endpoint_name='potatoguard-endpoint',
                                         instance_type='ml.t2.medium',
                                         initial_instance_count=1):
    """
    Create SageMaker model and deploy real-time inference endpoint
    
    What is an endpoint?
    - A live web service that runs the model
    - Can receive images and return predictions
    - Available 24/7 for real-time inference (making predictions)
    - Can be accessed via HTTP/REST API
    
    What this function does step-by-step:
    1. Creates a SageMaker session (connection to AWS)
    2. Wraps the SavedModel as a TensorFlowModel
    3. Deploys the model to EC2 instances
    4. Creates an HTTP endpoint
    
    Instance types (choose based on your needs):
    - ml.t2.medium: Low traffic, cost-effective (~$0.05/hour)
    - ml.t3.large: Medium traffic (~$0.12/hour)
    - ml.c5.xlarge: High traffic, production (~$0.25/hour)
    - ml.p3.2xlarge: GPU acceleration, highest cost (~$3.06/hour)
    
    Args:
        s3_model_uri: S3 path to the SavedModel (from upload_model_to_s3)
        endpoint_name: Name for the SageMaker endpoint (e.g., "potatoguard-endpoint")
        instance_type: EC2 instance type for deployment
        initial_instance_count: Number of instances to deploy
    
    Returns:
        Tuple of (endpoint_name, predictor) for making predictions
    """
    
    print("\n" + "="*60)
    print("DEPLOYING TO SAGEMAKER ENDPOINT")
    print("="*60)
    
    # Create a SageMaker session
    # This is our connection to AWS SageMaker service
    sagemaker_session = sagemaker.Session()
    
    # Get the IAM role for SageMaker
    # IAM role defines permissions (what SageMaker can access)
    role_arn = sagemaker.get_execution_role()
    
    # Create TensorFlow model wrapper
    # This tells SageMaker about our model and how to run it
    print(f"Creating SageMaker TensorFlow model...")
    
    tensorflow_model = TensorFlowModel(
        model_data=s3_model_uri,           # S3 path to SavedModel
        role=role_arn,                     # IAM role (permissions)
        framework_version='2.12',          # TensorFlow version (matches training)
        sagemaker_session=sagemaker_session,
        name=f"{endpoint_name}-model-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    
    # Deploy the model to an endpoint
    print(f"Deploying model to endpoint '{endpoint_name}'...")
    print(f"Instance type: {instance_type}")
    print(f"Number of instances: {initial_instance_count}")
    print("This may take 5-10 minutes...")
    
    predictor = tensorflow_model.deploy(
        initial_instance_count=initial_instance_count,
        instance_type=instance_type,
        endpoint_name=endpoint_name,
        wait=True  # Wait for endpoint deployment to complete
    )
    
    print(f"✓ Endpoint '{endpoint_name}' is now in service and ready for predictions!")
    
    return endpoint_name, predictor


def test_single_image(image_path, predictor=None, endpoint_name='potatoguard-endpoint',
                     class_names=['Healthy', 'Late Blight', 'Early Blight']):
    """
    Test the SageMaker endpoint with a single potato leaf image
    
    This function demonstrates how to:
    1. Load an image from disk
    2. Preprocess it (resize, normalize) like training data
    3. Send to the SageMaker endpoint
    4. Parse the response and display results
    
    Example output:
    ============================================================
    PREDICTION RESULT
    ============================================================
    Predicted Disease: Early Blight
    Confidence Score: 94.23%
    
    Detailed Probabilities:
      Healthy        :   3.45%
      Late Blight    :   2.32%
      Early Blight   :  94.23%
    
    Args:
        image_path: Path to potato leaf image file
        predictor: SageMaker predictor object (if None, creates runtime client)
        endpoint_name: Name of the SageMaker endpoint
        class_names: List of disease class names in order
    
    Returns:
        Dictionary with prediction result
    """
    
    print("\n" + "="*60)
    print("TESTING ENDPOINT WITH SINGLE IMAGE")
    print("="*60)
    
    # Check if image exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    print(f"Loading image from {image_path}...")
    
    # Load image and resize to 224x224
    # This matches the input size used during training
    image = load_img(image_path, target_size=(224, 224))
    
    # Convert image to numpy array (pixel values 0-255)
    image_array = img_to_array(image)
    
    # Normalize pixel values from [0, 255] to [0, 1]
    # This matches the normalization used during training
    image_array = image_array / 255.0
    
    # Add batch dimension
    # Model expects: (batch_size, height, width, channels)
    # So we add 1: (1, 224, 224, 3)
    image_batch = np.expand_dims(image_array, axis=0)
    
    print(f"Image shape: {image_batch.shape}")
    print("Sending to SageMaker endpoint for prediction...")
    
    try:
        # If predictor is provided, use it directly
        if predictor is not None:
            prediction = predictor.predict(image_batch)
        else:
            # Otherwise, create a runtime client
            # SageMaker Runtime lets us invoke endpoints
            runtime_client = boto3.client('sagemaker-runtime')
            
            # Send request to the endpoint
            response = runtime_client.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType='application/x-npy',  # NumPy array format
                Body=image_batch.tobytes()        # Convert to bytes
            )
            
            # Parse the response from the endpoint
            prediction = json.loads(response['Body'].read().decode())
        
        # Extract prediction probabilities from response
        # Predictions are softmax probabilities: [P(class0), P(class1), P(class2)]
        if isinstance(prediction, dict):
            probabilities = prediction.get('predictions', [[]])[0]
        else:
            probabilities = prediction[0] if len(prediction.shape) > 1 else prediction
        
        # Get predicted class (highest probability)
        # argmax returns the index of the highest value
        predicted_class_idx = np.argmax(probabilities)
        confidence = probabilities[predicted_class_idx]
        
        # Get disease name from class index
        predicted_disease = class_names[predicted_class_idx]
        
        # Print results
        print("\n" + "-"*60)
        print("PREDICTION RESULT")
        print("-"*60)
        print(f"Predicted Disease: {predicted_disease}")
        print(f"Confidence Score: {confidence*100:.2f}%")
        print("-"*60)
        
        # Show probabilities for all classes
        print("\nDetailed Probabilities:")
        for idx, disease in enumerate(class_names):
            prob = probabilities[idx] * 100
            print(f"  {disease:20s}: {prob:6.2f}%")
        
        # Return result as dictionary
        result = {
            'image_path': image_path,
            'predicted_disease': predicted_disease,
            'confidence': confidence,
            'all_probabilities': {disease: float(prob) for disease, prob in zip(class_names, probabilities)}
        }
        
        return result
        
    except Exception as e:
        print(f"Error during inference: {str(e)}")
        print("Make sure the endpoint is deployed and in service")
        raise


def deploy_pipeline(h5_model_path='./potatoguard_model.h5',
                   bucket_name='potatoguard-models',
                   endpoint_name='potatoguard-endpoint',
                   test_image_path=None):
    """
    Complete deployment pipeline
    
    This orchestrates the entire deployment process:
    
    Step 1: Convert H5 model to SavedModel format
    Step 2: Upload SavedModel to S3 bucket
    Step 3: Deploy to SageMaker endpoint
    Step 4: Test with sample image (optional)
    
    Args:
        h5_model_path: Path to trained H5 model
        bucket_name: S3 bucket for model storage
        endpoint_name: SageMaker endpoint name
        test_image_path: Optional path to test image
    """
    
    print("\n" + "="*70)
    print("POTATOGUARD - SAGEMAKER DEPLOYMENT PIPELINE")
    print("="*70)
    
    try:
        # Step 1: Convert model from H5 to SavedModel
        savedmodel_dir = convert_h5_to_savedmodel(h5_model_path)
        
        # Step 2: Upload SavedModel to S3
        s3_model_uri, bucket = upload_model_to_s3(savedmodel_dir, bucket_name)
        
        # Step 3: Deploy to SageMaker
        print("\nNote: SageMaker deployment requires AWS credentials and IAM roles.")
        print("Uncomment the next section if running in AWS environment:")
        print("# endpoint_name, predictor = create_and_deploy_sagemaker_endpoint(s3_model_uri, endpoint_name)")
        
        # Uncomment below if running in AWS SageMaker environment
        # endpoint_name, predictor = create_and_deploy_sagemaker_endpoint(s3_model_uri, endpoint_name)
        
        # Step 4: Test endpoint (if image provided)
        if test_image_path and os.path.exists(test_image_path):
            # test_single_image(test_image_path, endpoint_name=endpoint_name)
            print(f"\nTo test the endpoint with {test_image_path}:")
            print(f"  test_single_image('{test_image_path}', endpoint_name='{endpoint_name}')")
        
        print("\n" + "="*70)
        print("DEPLOYMENT PIPELINE COMPLETE")
        print("="*70)
        print(f"\nNext steps:")
        print(f"1. Model saved and ready at: {s3_model_uri}")
        print(f"2. Deploy endpoint using: create_and_deploy_sagemaker_endpoint('{s3_model_uri}', '{endpoint_name}')")
        print(f"3. Test endpoint with: test_single_image(image_path, endpoint_name='{endpoint_name}')")
        
    except Exception as e:
        print(f"\n✗ Error during deployment: {str(e)}")
        raise


if __name__ == "__main__":
    """
    Main entry point for deployment script
    
    Usage: python deploy.py
    
    Prerequisites:
    1. Model trained and saved as ./potatoguard_model.h5
    2. AWS credentials configured (aws configure or environment variables)
    3. IAM role with S3 and SageMaker permissions
    """
    
    # Check if model exists
    model_path = './potatoguard_model.h5'
    if not os.path.exists(model_path):
        print(f"Error: Model file '{model_path}' not found!")
        print("Please run train.py first to train the model.")
        exit(1)
    
    # Run deployment pipeline
    deploy_pipeline(
        h5_model_path='./potatoguard_model.h5',
        bucket_name='potatoguard-models',
        endpoint_name='potatoguard-endpoint',
        test_image_path=None  # Provide path to test image if available
    )
    
    print("\nDeployment script completed!")

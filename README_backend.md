# PotatoGuard Backend - AWS Lambda Functions

Backend infrastructure for PotatoGuard, an AI-powered Irish potato disease detection system. Built with AWS SAM (Serverless Application Model), AWS Lambda, Amazon SageMaker, and DynamoDB.

## Overview

This backend consists of three AWS Lambda functions that handle:
- **Detect**: Receives leaf photos, invokes the AI model via SageMaker, saves results
- **History**: Retrieves detection history for a farmer
- **Report**: Retrieves a single detection report

## Project Structure

```
backend/
├── detect/
│   └── handler.py          # Main detection Lambda function
├── history/
│   └── handler.py          # Detection history Lambda function
├── report/
│   └── handler.py          # Single report Lambda function
├── template.yaml           # AWS SAM infrastructure template
└── README_backend.md       # This file
```

## Required AWS Resources

Before deploying, ensure you have:
- **SageMaker Endpoint**: `potatoguard-endpoint` (trained CNN model for disease classification)
- **DynamoDB Table**: `potatoguard-detections` (stores detection records)
- **S3 Bucket**: `potatoguard-images` (stores uploaded leaf images)
- **AWS Region**: `us-east-1`

## Environment Variables

All Lambda functions require these environment variables (configured in `template.yaml`):

| Variable | Value | Description |
|----------|-------|-------------|
| `SAGEMAKER_ENDPOINT` | `potatoguard-endpoint` | SageMaker endpoint name for model predictions |
| `DYNAMODB_TABLE` | `potatoguard-detections` | DynamoDB table for storing detections |
| `S3_BUCKET` | `potatoguard-images` | S3 bucket for storing leaf images |
| `AWS_REGION_NAME` | `us-east-1` | AWS region for all resources |

## Lambda Functions

### 1. DetectFunction (POST /detect)

**Purpose**: Main detection endpoint. Receives leaf photos, classifies disease using SageMaker, stores results.

**Event Payload**:
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
  "farmer_id": "farmer001"
}
```

**Processing Steps**:
1. Parse and validate request body (check for required fields)
2. Decode base64 image to bytes
3. Generate unique filename using UUID
4. Upload image to S3
5. Pre-process image (resize to 224x224, normalize, expand dimensions)
6. Invoke SageMaker endpoint
7. Parse predictions and get confidence score
8. Map disease class index to disease name and treatment
9. Generate S3 image URL
10. Save detection record to DynamoDB
11. Return detection results

**Response**:
```json
{
  "statusCode": 200,
  "body": {
    "disease": "Late Blight",
    "confidence": 0.95,
    "treatment": "Apply fungicide (Mancozeb or Chlorothalonil) immediately. Remove infected leaves.",
    "imageUrl": "https://potatoguard-images.s3.us-east-1.amazonaws.com/detections/farmer001/uuid-here.jpg",
    "detectionId": "uuid-here",
    "farmerId": "farmer001",
    "timestamp": "2024-04-15T10:30:45.123456Z"
  }
}
```

**Disease Classifications**:
- **0 - Healthy**: "Your plant is healthy! Keep monitoring weekly."
- **1 - Late Blight**: "Apply fungicide (Mancozeb or Chlorothalonil) immediately. Remove infected leaves."
- **2 - Early Blight**: "Apply copper-based fungicide. Improve air circulation between plants."
- **3 - Bacterial Wilt**: "Remove and destroy infected plants. Do not replant in same soil for 2 seasons."

### 2. HistoryFunction (GET /history/{farmerId})

**Purpose**: Retrieves all detection records for a farmer, sorted by newest first.

**Path Parameter**:
```
/history/farmer001
```

**Query Logic**:
- Uses DynamoDB Global Secondary Index `farmerId-index`
- Sorts by timestamp descending (newest first)
- Returns empty list if no records found (not an error)

**Response**:
```json
{
  "statusCode": 200,
  "body": {
    "farmerId": "farmer001",
    "detections": [
      {
        "detectionId": "uuid-1",
        "farmerId": "farmer001",
        "disease": "Late Blight",
        "confidence": 0.95,
        "treatment": "Apply fungicide...",
        "imageUrl": "https://...",
        "timestamp": "2024-04-15T10:30:45.123456Z",
        "s3Key": "detections/farmer001/uuid-1.jpg"
      },
      {
        "detectionId": "uuid-2",
        "farmerId": "farmer001",
        "disease": "Healthy",
        "confidence": 0.98,
        "treatment": "Your plant is healthy...",
        "imageUrl": "https://...",
        "timestamp": "2024-04-14T14:22:10.123456Z",
        "s3Key": "detections/farmer001/uuid-2.jpg"
      }
    ],
    "count": 2
  }
}
```

### 3. ReportFunction (GET /report/{detectionId})

**Purpose**: Retrieves a single detection report by ID.

**Path Parameter**:
```
/report/uuid-1
```

**Response**:
```json
{
  "statusCode": 200,
  "body": {
    "detectionId": "uuid-1",
    "farmerId": "farmer001",
    "disease": "Late Blight",
    "confidence": 0.95,
    "treatment": "Apply fungicide (Mancozeb or Chlorothalonil) immediately. Remove infected leaves.",
    "imageUrl": "https://potatoguard-images.s3.us-east-1.amazonaws.com/detections/farmer001/uuid-1.jpg",
    "timestamp": "2024-04-15T10:30:45.123456Z",
    "s3Key": "detections/farmer001/uuid-1.jpg"
  }
}
```

**Error Response** (if detectionId not found):
```json
{
  "statusCode": 404,
  "body": {
    "error": "Detection report not found",
    "detectionId": "invalid-uuid"
  }
}
```

## Prerequisites

### Required Software

1. **AWS Account** - with access to Lambda, DynamoDB, S3, SageMaker
2. **AWS CLI** - for AWS credentials configuration
3. **AWS SAM CLI** - for local testing and deployment
   - Download from: [docs.aws.amazon.com/serverless-application-model](https://docs.aws.amazon.com/serverless-application-model)
4. **Python 3.11+** - runtime for Lambda functions
5. **Docker** - required by SAM CLI for local testing
6. **Git** - for version control

### Installation Steps

#### 1. Install AWS CLI
```bash
# Windows
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# macOS
brew install awscli

# Linux
sudo apt-get install awscli
```

#### 2. Install AWS SAM CLI
```bash
# Windows
pip install aws-sam-cli

# macOS/Linux
brew tap aws/tap
brew install aws-sam-cli
```

#### 3. Verify Installation
```bash
sam --version
# Expected output: SAM CLI, version x.x.x
```

#### 4. Configure AWS Credentials
```bash
aws configure
# Enter: AWS Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)
```

## Deployment

### Step 1: Build the Project

Compile Lambda functions and resolve dependencies:

```bash
cd backend
sam build
```

**Expected Output**:
```
Building resources
Building image for DetectFunction
Building image for HistoryFunction
Building image for ReportFunction
...
Build Successful
```

### Step 2: Deploy to AWS

Deploy using AWS CloudFormation:

```bash
sam deploy --guided
```

**Interactive Prompts** (first time only):
```
Stack Name [sam-app]: potatoguard-backend
Region [us-east-1]: us-east-1
Confirm changes before deploy [y/N]: y
Allow SAM CLI IAM role creation [Y/n]: y
Allow SAM CLI Lambda function URL creation [Y/n]: n
Save parameters to samconfig.toml for future deployments [Y/n]: y
```

**Subsequent Deployments**:
```bash
sam deploy
```

### Step 3: Verify Deployment

Check CloudFormation stack:
```bash
aws cloudformation describe-stacks --stack-name potatoguard-backend --query 'Stacks[0].Outputs'
```

This will output your API endpoint and resource information.

## Local Testing

### Test with SAM Local

#### Option 1: Invoke Individual Lambda Functions

**Test Detect Function**:
```bash
# Create test_event_detect.json
cat > test_event_detect.json << 'EOF'
{
  "body": "{\"image_base64\": \"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==\", \"farmer_id\": \"farmer001\"}"
}
EOF

# Invoke function
sam local invoke DetectFunction --event test_event_detect.json
```

**Test History Function**:
```bash
# Create test_event_history.json
cat > test_event_history.json << 'EOF'
{
  "pathParameters": {
    "farmerId": "farmer001"
  }
}
EOF

# Invoke function
sam local invoke HistoryFunction --event test_event_history.json
```

**Test Report Function**:
```bash
# Create test_event_report.json
cat > test_event_report.json << 'EOF'
{
  "pathParameters": {
    "detectionId": "550e8400-e29b-41d4-a716-446655440000"
  }
}
EOF

# Invoke function
sam local invoke ReportFunction --event test_event_report.json
```

#### Option 2: Start Local API Gateway

```bash
sam local start-api
```

This starts a local API Gateway at `http://localhost:3000`

### Test with Postman

#### 1. Import API

Open Postman and create requests:

**POST /detect**
```
URL: https://{YOUR_API_ENDPOINT}/Prod/detect
Method: POST
Headers: Content-Type: application/json
Body (raw):
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "farmer_id": "farmer001"
}
```

**GET /history/{farmerId}**
```
URL: https://{YOUR_API_ENDPOINT}/Prod/history/farmer001
Method: GET
Headers: Content-Type: application/json
```

**GET /report/{detectionId}**
```
URL: https://{YOUR_API_ENDPOINT}/Prod/report/550e8400-e29b-41d4-a716-446655440000
Method: GET
Headers: Content-Type: application/json
```

#### 2. Test Error Handling

**Missing Required Fields**:
```json
{
  "image_base64": "valid_base64_here"
  // Missing farmer_id
}
```
Expected: 400 Bad Request

**Invalid Base64**:
```json
{
  "image_base64": "not-valid-base64!!!",
  "farmer_id": "farmer001"
}
```
Expected: 400 Bad Request

## AWS Resources Created

### Lambda Functions
- **PotatoGuard-Detect**: POST /detect
- **PotatoGuard-History**: GET /history/{farmerId}
- **PotatoGuard-Report**: GET /report/{detectionId}

### API Gateway
- **HTTP API**: Handles all endpoints with CORS enabled

### DynamoDB
- **potatoguard-detections**: Table with Global Secondary Index on farmerId

### S3
- **potatoguard-images**: Bucket for storing leaf images (public read access for image URLs)

### IAM Roles
- Lambda execution roles with permissions for DynamoDB, S3, and SageMaker

## Monitoring & Logging

### View Lambda Logs

```bash
# View recent logs for Detect function
sam logs -n DetectFunction --stack-name potatoguard-backend --tail

# View logs for specific function
aws logs tail /aws/lambda/PotatoGuard-Detect --follow
```

### CloudWatch Metrics

Access CloudWatch console to monitor:
- Lambda invocations and errors
- DynamoDB read/write capacity
- S3 object count and size

## Troubleshooting

### Common Issues

**Issue**: "Unable to locate credentials"
```bash
# Solution: Configure AWS credentials
aws configure
```

**Issue**: "Module not found" when running locally
```bash
# Solution: Ensure Python dependencies are installed in virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Issue**: "SageMaker endpoint not found"
```bash
# Solution: Create or verify your SageMaker endpoint
aws sagemaker describe-endpoint --endpoint-name potatoguard-endpoint
```

**Issue**: DynamoDB table not found
```bash
# Solution: Verify table exists in your AWS region
aws dynamodb list-tables --region us-east-1
```

## Development

### Adding Dependencies

1. Update `requirements.txt` in each handler directory
2. Run `sam build` to install dependencies
3. Test locally: `sam local invoke`

### Modifying Lambda Functions

1. Edit handler.py file
2. Run `sam build` to validate syntax
3. Test locally: `sam local invoke FunctionName --event test_event.json`
4. Deploy: `sam deploy`

## Cleanup

To delete all AWS resources created by this template:

```bash
aws cloudformation delete-stack --stack-name potatoguard-backend
```

Confirm deletion:
```bash
aws cloudformation wait stack-delete-complete --stack-name potatoguard-backend
```

## Production Considerations

### Security
- Enable VPC for Lambda functions
- Use IAM roles with least privilege
- Enable encryption for DynamoDB and S3
- Use AWS Secrets Manager for sensitive data

### Performance
- Monitor Lambda cold starts
- Optimize image processing
- Use Lambda layers for common dependencies
- Enable DynamoDB point-in-time recovery

### Cost Optimization
- Use S3 lifecycle policies to archive old images
- Set up DynamoDB auto-scaling
- Monitor CloudWatch costs
- Use S3 Intelligent-Tiering

## Support

For issues or questions:
1. Check AWS documentation: https://docs.aws.amazon.com
2. Review CloudWatch logs for error details
3. Test locally before deploying to production
4. Verify all environment variables are correctly configured

---

**Author**: Tukahirwa Clinton  
**Branch**: feature/backend  
**Last Updated**: April 2024

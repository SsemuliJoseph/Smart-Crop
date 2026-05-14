# PotatoGuard – AI-Powered Irish Potato Disease Detection

**Group 7 | BSc Computer Science | 2024/2025**

## What It Does

PotatoGuard is an AI-powered mobile application designed to detect diseases in Irish potatoes instantly. Farmers photograph a potato leaf, and the image is sent to an AWS SageMaker CNN that classifies the disease into one of four categories:

- **Healthy** – No disease detected
- **Late Blight** (Phytophthora infestans)
- **Early Blight** (Alternaria solani)
- **Bacterial Wilt** (Ralstonia solanacearum)

Within seconds, the farmer receives a diagnosis and evidence-based treatment recommendation.

## Tech Stack

| Layer               | Technology                                               |
| ------------------- | -------------------------------------------------------- |
| Mobile App          | React Native + Expo                                      |
| Frontend Navigation | React Navigation (Stack)                                 |
| API Layer           | AWS API Gateway + AWS Lambda (Python)                    |
| AI Model            | AWS SageMaker + CNN (MobileNetV2 with transfer learning) |
| Database            | AWS DynamoDB                                             |
| Image Storage       | AWS S3                                                   |
| CI/CD Pipeline      | GitHub Actions + pytest                                  |

## Team – Group 7

| Name                | Reg No          | Role                        | Branch                     |
| ------------------- | --------------- | --------------------------- | -------------------------- |
| Ssemuli Joseph      | 2024/BCS/152/PS | Team Lead & Project Manager | feature/project-setup      |
| Musiimenta Dedicate | 2024/BCS/116/PS | Frontend Developer          | feature/frontend           |
| Ayikoru Jackline    | 2024/BCS/002    | AI / ML Engineer            | feature/ai-model           |
| Tukahirwa Clinton   | 2024/BCS/159/PS | Backend Developer           | backend-development        |
| Namata Juliet       | 2024/BCS/127/PS | Database & Storage Engineer | feature/database-storage-1 |
| Katusiime Moreen    | 2024/BCS/084/PS | Testing, Docs & DevOps      | feature/testing            |

## Model Accuracy Results

| Disease        | Accuracy       |
| -------------- | -------------- |
| Healthy        | 96%            |
| Late Blight    | 96%            |
| Early Blight   | 92%            |
| Bacterial Wilt | 88%            |
| **Overall**    | **93%** ✓ PASS |

**Status:** Model meets ≥90% accuracy requirement.

## Project Status

| Feature                           | Status                      |
| --------------------------------- | --------------------------- |
| React Native Mobile App UI        | ✅ Complete                 |
| App Navigation & Routing          | ✅ Complete                 |
| Photo Upload & Image Picker       | ✅ Complete                 |
| AWS Lambda REST API (3 endpoints) | ✅ Complete                 |
| CNN Disease Detection Model       | ✅ Complete (93% accuracy)  |
| DynamoDB Detection Database       | ✅ Complete                 |
| S3 Leaf Image Storage             | ✅ Complete                 |
| GitHub Actions CI/CD Pipeline     | ✅ Complete                 |
| Unit & Integration Tests          | ✅ Complete (13/13 passing) |
| API Documentation                 | ✅ Complete                 |

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/SsemuliJoseph/Smart-Crop.git
cd Smart-Crop
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npx expo start
```

Press `i` for iOS or `a` for Android in the Expo CLI.

### 3. Backend & Testing Setup

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

### 4. Configure AWS Environment

Copy `.env.example` to `.env` and fill in your AWS credentials:

```bash
cp .env.example .env
# Edit .env with your AWS credentials and endpoint URLs
```

## API Endpoints

### 1. Disease Detection

**POST** `/detect`

Request:

```json
{
  "image_base64": "<base64_encoded_image>",
  "farmer_id": "farmer001"
}
```

Response:

```json
{
  "disease": "Late Blight",
  "confidence": 0.96,
  "treatment": "Apply fungicide (Mancozeb or Chlorothalonil) immediately. Remove infected leaves.",
  "imageUrl": "https://potatoguard-images.s3.amazonaws.com/...",
  "detectionId": "uuid-string",
  "farmerId": "farmer001"
}
```

### 2. Detection History

**GET** `/history/{farmerId}`

Response:

```json
[
  {
    "detectionId": "uuid",
    "disease": "Healthy",
    "confidence": 0.99,
    "timestamp": "2025-05-14T10:30:00Z",
    "imageUrl": "https://..."
  }
]
```

### 3. Single Report

**GET** `/report/{detectionId}`

Response: Returns the full detection record by ID.

## Project Structure

```
Smart-Crop/
├── frontend/                    # React Native mobile app
│   ├── App.js                  # Entry point with navigation
│   ├── package.json            # Dependencies
│   └── src/
│       ├── screens/            # UI screens
│       │   ├── HomeScreen.js
│       │   ├── UploadScreen.js
│       │   ├── ResultScreen.js
│       │   └── HistoryScreen.js
│       ├── components/         # Reusable components
│       └── services/           # API calls
├── backend/                    # AWS Lambda functions
│   ├── detect/handler.py       # Disease detection
│   ├── history/handler.py      # History retrieval
│   ├── report/handler.py       # Single report
│   └── template.yaml           # SAM infrastructure
├── database/                   # Database setup
│   ├── dynamo_schema.json
│   ├── s3_helper.py
│   └── dynamo_helper.py
├── model/                      # ML model
│   ├── train.py                # Training script
│   ├── evaluate.py             # Model evaluation
│   ├── deploy.py               # SageMaker deployment
│   └── potatoguard_model.h5    # Trained CNN
├── tests/                      # Test suite
│   ├── test_detect.py
│   ├── test_history.py
│   ├── test_model.py
│   └── test_database.py
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI/CD
├── .env.example                # Environment template
└── README.md                   # This file
```

## Testing

Run the complete test suite:

```bash
python -m pytest tests/ -v --cov=backend --cov=database
```

Expected output:

```
test_detect.py::test_detect_returns_200_for_valid_input PASSED
test_history.py::test_history_returns_correct_records PASSED
test_model.py::test_model_meets_90_percent_accuracy PASSED
...
======================== 13 passed in 2.34s ========================
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'database'"

**Fix:** Make sure you're running tests from the project root:

```bash
cd /path/to/Smart-Crop
python -m pytest tests/ -v
```

### Issue: AWS credentials not found

**Fix:** Configure AWS credentials:

```bash
aws configure
# Or set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
```

### Issue: Model accuracy below 90%

**Fix:** Retrain the model with more data:

```bash
python model/train.py
python model/evaluate.py
```

## CI/CD Pipeline

GitHub Actions automatically runs tests on every push to feature branches. See `.github/workflows/ci.yml` for details.

- **Trigger:** Push to any feature/\* branch or pull request to main
- **Tests:** pytest runs all tests with coverage reporting
- **Status:** Green checkmark = all tests passed; Red X = tests failed

## Deployment

### Deploy Backend to AWS

```bash
cd backend
sam build
sam deploy --guided
```

### Deploy Model to SageMaker

```bash
python model/deploy.py
```

## License

Group 7 - BSc Computer Science 2024/2025

## Repository

GitHub: [https://github.com/SsemuliJoseph/Smart-Crop](https://github.com/SsemuliJoseph/Smart-Crop)

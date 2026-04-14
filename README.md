# PotatoGuard - AI-Powered Irish Potato Disease Detection

## Description

PotatoGuard is an AI-powered mobile application designed to detect diseases in Irish potatoes instantly. Utilizing modern machine learning techniques, the system can analyze images of potato leaves and accurately classify them into four categories: Late Blight, Early Blight, Bacterial Wilt, and Healthy.

## Tech Stack

- **Frontend:** React Native with Expo
- **Backend:** AWS Lambda, API Gateway
- **Database & Storage:** DynamoDB, S3
- **AI / Machine Learning:** SageMaker CNN

## Team

**Group 7 - BSc Computer Science**

- **Ssemuli Joseph** - Team Lead

## Branch Structure

| Branch Name             | Purpose                                                          |
| :---------------------- | :--------------------------------------------------------------- |
| `feature/project-setup` | Initial repository scaffolding, architecture, and documentation. |
| `feature/frontend`      | React Native UI/UX development and screen implementation.        |
| `feature/ai-model`      | CNN model training, tuning, and SageMaker deployment.            |
| `feature/backend`       | AWS Lambda functions and API Gateway route configurations.       |
| `feature/database`      | DynamoDB definitions and S3 bucket setup.                        |
| `feature/testing`       | Unit testing, integration tests, and QA.                         |

## Setup Instructions

### Prerequisites

- Node.js (v14 or newer)
- Expo CLI
- Python 3.8+ (for AI model scripts)

### Installation & Running

1. **Clone the repository:**

   ```bash
   git clone https://github.com/SsemuliJoseph/Smart-Crop.git
   cd Smart-Crop
   ```

2. **Install frontend dependencies:**

   ```bash
   cd frontend
   npm install
   ```

3. **Run the React Native app:**
   ```bash
   npx expo start
   ```
   _Note: Use the Expo Go app on your physical device or run an Android/iOS emulator to preview._

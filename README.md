# PotatoGuard – AI-Powered Irish Potato Disease Detection

Group 7 | BSc Computer Science | 2024/2025

## What It Does
Farmers photograph a potato leaf. The image is sent to an AWS SageMaker
CNN that classifies the disease into one of four categories:
- Healthy
- Late Blight
- Early Blight
- Bacterial Wilt

Within seconds, the farmer receives a diagnosis and treatment recommendation.

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Mobile App | React Native + Expo |
| API | AWS API Gateway + AWS Lambda (Python) |
| AI Model | AWS SageMaker + CNN (MobileNetV2) |
| Database | AWS DynamoDB |
| Image Storage | AWS S3 |
| Auth | AWS Cognito |
| CI/CD | GitHub Actions |

## Team – Group 7
| Name | Reg No | Role |
|------|--------|------|
| Ssemuli Joseph | 2024/BCS/152/PS | Team Lead & Project Manager |
| Musiimenta Dedicate | 2024/BCS/116/PS | Frontend Developer |
| Ayikoru Jackline | 2024/BCS/002 | AI / ML Engineer |
| Tukahirwa Clinton | 2024/BCS/159/PS | Backend Developer |
| Namata Juliet | 2024/BCS/127/PS | Database & Storage Engineer |
| Katusiime Moreen | 2024/BCS/084/PS | Testing, Docs & DevOps |

## Branch Structure
- main – production-ready merged code
- feature/project-setup – Ssemuli
- feature/frontend – Dedicate
- feature/ai-model – Jackline
- feature/backend – Clinton
- feature/database – Juliet
- feature/testing – Moreen

## Model Accuracy Results
| Disease | Accuracy |
|---------|----------|
| Healthy | 96% |
| Late Blight | 96% |
| Early Blight | 92% |
| Bacterial Wilt | 88% |
| Overall | 93% |

## Project Status
| Feature | Status |
|---------|--------|
| React Native Mobile App | Complete |
| AWS Lambda REST API | Complete |
| CNN Disease Detection Model (93% acc) | Complete |
| DynamoDB Storage | Complete |
| S3 Image Storage | Complete |
| GitHub Actions CI (13/13 tests passing) | Complete |

## Setup Instructions
1. Clone: git clone https://github.com/SsemuliJoseph/Smart-Crop.git
2. Frontend: cd frontend && npm install && npx expo start
3. Backend tests: pip install pytest moto boto3 && python -m pytest tests/ -v

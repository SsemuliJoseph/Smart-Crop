# PotatoGuard Database & Storage Setup
**Engineer:** Namata Juliet | 2024/BCS/127/PS
**Role:** Database & Storage Engineer

---

## DynamoDB Table: detections

| Field | Type | Description |
|-------|------|-------------|
| detectionId | String (PK) | Unique ID for each detection |
| farmerId | String | ID of the farmer who uploaded the photo |
| imageUrl | String | S3 URL of the uploaded leaf photo |
| disease | String | CNN result: Healthy, Late Blight, Early Blight, Bacterial Wilt |
| confidence | Float | Model confidence score e.g. 0.94 |
| timestamp | String | Date and time of detection e.g. 2025-04-14T10:30:00Z |
| treatment | String | Recommended treatment for the detected disease |

---

## S3 Bucket: potatoguard-images

- Stores all potato leaf photos uploaded by farmers
- Bucket policy configured to allow Lambda read/write access

---

## Status
- [x] DynamoDB table created
- [x] S3 bucket created
- [x] Bucket policy configured

# Day 2 – Tuesday | Design & Model Training Start
**Role:** Katusiime Moreen | Testing, Docs & DevOps
**Branch:** feature/testing
**SDLC Phase:** Phase 2 – Design + Phase 3 – Development (start)

---

## Tasks Completed Today

### 1. Local Test Environment Set Up
Installed all required testing libraries:
pip install pytest pytest-cov moto boto3 requests pillow numpy

Verified installation:
pytest --version shows pytest 7.x.x

Created tests/ folder structure:
tests/
├── __init__.py
├── test_detect.py       (unit tests for /detect Lambda)
├── test_history.py      (unit tests for /history Lambda)
├── test_model.py        (CNN model accuracy validation)
└── test_database.py     (DynamoDB and S3 helper tests)

---

### 2. Unit Test Skeletons Written
Wrote skeleton test files where every test has a clear name and docstring
explaining exactly what it checks. Bodies left as pass to be filled on Day 3.

test_detect.py contains 5 test skeletons:
- test_detect_returns_200_for_valid_input
  Checks that a valid image and farmer_id returns HTTP 200 with disease, confidence, treatment
- test_detect_returns_400_if_image_missing
  Checks that missing image_base64 field returns HTTP 400
- test_detect_returns_400_if_farmer_id_missing
  Checks that missing farmer_id field returns HTTP 400
- test_confidence_is_between_0_and_1
  Checks that confidence score is a float between 0.0 and 1.0
- test_disease_is_valid_category
  Checks disease is one of: Healthy, Late Blight, Early Blight, Bacterial Wilt

test_history.py contains 3 test skeletons:
- test_empty_history_returns_200_and_empty_list
  New farmer with no scans should get HTTP 200 and empty list not an error
- test_history_returns_correct_records
  Saving 2 records and calling history should return exactly those 2
- test_history_sorted_newest_first
  History list must be sorted by timestamp descending newest first

test_database.py contains 4 test skeletons:
- test_save_and_retrieve_detection
  Save a record with save_detection() then retrieve it and check all fields match
- test_get_farmer_history_returns_all_records
  Save 3 records for one farmer and get_farmer_history() must return all 3
- test_upload_image_returns_url
  upload_image() should store image in S3 and return a non-empty URL string
- test_delete_detection_removes_record
  After delete_detection() calling get_detection() should return None

---

### 3. Test Data Fixtures Created
Created shared tests/conftest.py with reusable fixtures:
- sample_base64_image: generates a valid 224x224 PNG image as base64 string
- sample_detection_record: returns a sample detection dict matching DynamoDB schema

---

### 4. GitHub Actions CI File Created
Created .github/workflows/ci.yml that:
- Triggers automatically on every push to any feature/* branch
- Installs Python 3.9 and all dependencies
- Runs pytest tests/ -v automatically
- Shows green checkmark or red cross on GitHub for the lecturer to see

---

## Git Commit for Today
git add tests/ .github/
git commit -m "Day 2: Unit test skeletons, fixtures and CI pipeline by Katusiime Moreen"
git push origin feature/testing

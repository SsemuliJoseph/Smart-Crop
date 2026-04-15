# PotatoGuard - Potato Disease Detection AI Model

**PotatoGuard** is an AI-powered system for detecting Irish potato diseases using deep learning. It uses a MobileNetV2-based Convolutional Neural Network (CNN) to classify potato leaf images into four disease categories with high accuracy.

## Disease Classes

The model detects the following potato diseases:

| Index | Disease Class | Scientific Name | Typical Symptoms |
|-------|---------------|-----------------|------------------|
| 0 | Healthy | — | No disease, normal leaf appearance |
| 1 | Late Blight | *Phytophthora infestans* | Water-soaked spots, white mold on undersides |
| 2 | Early Blight | *Alternaria solani* | Target-like concentric rings, yellow halos |
| 3 | Bacterial Wilt | *Ralstonia solanacearum* | Wilting, browning of vascular tissue *(optional - if dataset available)* |

**Note:** Currently trained on 3 classes (Healthy, Early Blight, Late Blight). Adjust to 4 if Bacterial Wilt data is available.

---

## System Architecture

```
Input Image (224x224)
        ↓
MobileNetV2 Base Model (ImageNet pre-trained)
        ↓
Global Average Pooling 2D
        ↓
Dense(128, ReLU) → Dropout(0.3)
        ↓
Dense(3, Softmax) → Probability Distribution
        ↓
Output: Disease Classification with Confidence Score
```

### Key Properties
- **Base Model:** MobileNetV2 (frozen layers - transfer learning)
- **Input Size:** 224×224 RGB images
- **Training Approach:** Transfer learning + fine-tuning
- **Batch Size:** 32 images per batch
- **Target Accuracy:** ≥ 90%

---

## Step 1: Download Dataset from Kaggle

### Method 1: Using Kaggle API (Recommended)

```bash
# 1. Install Kaggle CLI
pip install kaggle

# 2. Download Kaggle API credentials
# Go to: https://www.kaggle.com/settings/account
# Click "Create New API Token" → kaggle.json file downloads
# Place kaggle.json in ~/.kaggle/ directory

# 3. Download PlantVillage dataset
kaggle datasets download -d arjunashok/plant-disease-classification
unzip plant-disease-classification.zip

# 4. Organize files into model/data/ subdirectory
# Expected structure:
# model/data/
#   ├── Potato___healthy/
#   ├── Potato___Early_blight/
#   └── Potato___Late_blight/
```

### Method 2: Manual Download

1. Visit: https://www.kaggle.com/datasets/arjunashok/plant-disease-classification
2. Click "Download" button
3. Extract the zip file
4. Locate potato disease folders
5. Move to `model/data/` directory

### Method 3: Use Direct Kaggle Link

```bash
# If you have Kaggle account set up
cd model
kaggle datasets download -d arjunashok/plant-disease-classification
unzip plant-disease-classification.zip
# Then organize disease folders into data/ subdirectory
```

### Verify Dataset Structure

After download, your directory should look like:

```
model/
├── data/
│   ├── Potato___healthy/          (≥ 1000 images)
│   ├── Potato___Early_blight/     (≥ 1000 images)
│   └── Potato___Late_blight/      (≥ 1000 images)
├── train.py
├── evaluate.py
├── deploy.py
├── requirements.txt
└── README_model.md
```

---

## Step 2: Train the Model

### Prerequisites

```bash
# Install Python 3.8+
python --version  # Should be 3.8 or higher

# Install required packages
pip install -r requirements.txt

# Verify installations
python -c "import tensorflow; print(f'TensorFlow version: {tensorflow.__version__}')"
```

### Local Training

```bash
# Navigate to model directory
cd model

# Run training script
python train.py
```

**Expected Output:**
```
============================================================
POTATO DISEASE DETECTION DATASET
============================================================
Found 3 disease classes:
  [0] Potato___healthy: 2152 samples
  [1] Potato___Early_blight: 1000 samples
  [2] Potato___Late_blight: 1155 samples
============================================================

Building MobileNetV2-based CNN model...

Model Architecture:
_________________________________________________________________
Layer (type)                 Output Shape              Param #
=================================================================
...
Total params: 2,659,331
Trainable params: 259,331
Non-trainable params: 2,400,000
_________________________________________________________________

============================================================
STARTING TRAINING
Epochs: 25, Batch Size: 32, Classes: 3
Early Stopping Patience: 5 epochs
============================================================

Epoch 1/25
[████████████████████████] 100 steps - 45s - loss: 0.8234 - accuracy: 0.7821
Epoch 2/25
[████████████████████████] 100 steps - 42s - loss: 0.4561 - accuracy: 0.8945
...
Epoch 15/25
[████████████████████████] 100 steps - 40s - loss: 0.1234 - accuracy: 0.9567

============================================================
Training complete. Validation accuracy: 94.23%
============================================================
✓ SUCCESS: Validation accuracy >= 90%
Model is ready for evaluation and deployment!
```

### Training in Google Colab

```python
# 1. Upload this notebook to Google Colab
# 2. Upload model/ folder (or use Git to clone)

# 3. Install dependencies
!pip install -r model/requirements.txt

# 4. Mount Google Drive to save models
from google.colab import drive
drive.mount('/content/drive')

# 5. Change to model directory and train
%cd model
!python train.py

# 6. Models are saved to /content/model/potatoguard_model.h5
```

### Training Parameters You Can Adjust

Edit `train.py` to modify:

```python
train_model(
    data_dir='./data',      # Dataset directory
    image_size=224,         # Image size (224x224 for MobileNetV2)
    batch_size=32,          # Batch size (reduce to 16 if out of memory)
    epochs=25,              # Max epochs (increase to 50 for better accuracy)
    num_classes=3           # Number of classes (3 or 4)
)
```

### Common Training Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError: data/ not found` | Dataset not in correct location | Ensure `model/data/` exists with subdirectories |
| `CUDA out of memory` | GPU memory too low | Reduce batch_size from 32 to 16 |
| Slow training | Large dataset or slow disk | Use SSD, reduce image_size, or increase batch_size |
| Low accuracy after training | Insufficient data or poor augmentation | Add more images, train longer (50-100 epochs) |
| Model not improving | Learning rate too high | Change `learning_rate=0.0001` in build_model() |

---

## Step 3: Evaluate Accuracy (≥ 90% Required)

### Run Evaluation

```bash
cd model
python evaluate.py
```

### Expected Output

```
============================================================
POTATO DISEASE DETECTION DATASET
============================================================
Found 3 disease classes:
  [0] Potato___healthy: 256 samples
  [1] Potato___Early_blight: 180 samples
  [2] Potato___Late_blight: x samples
============================================================

Loading test data from ./data/...
Generating predictions on test set...

============================================================
PER-CLASS ACCURACY
============================================================
Potato___healthy:                  94.53% (242/256)
Potato___Early_blight:             91.67% (165/180)
Potato___Late_blight:              89.23% (x/x)
============================================================

============================================================
OVERALL PERFORMANCE METRICS
============================================================
Overall Accuracy: 92.14%
Precision (weighted):  0.9234
Recall (weighted):     0.9214
F1 Score (weighted):   0.9218

============================================================
DETAILED CLASSIFICATION REPORT
============================================================
                     precision  recall  f1-score  support
    Potato___healthy       0.95    0.95     0.95      256
Potato___Early_blight       0.92    0.92     0.92      180
Potato___Late_blight       0.89    0.89     0.89      188
         weighted avg       0.92    0.92     0.92      624

============================================================
EVALUATION RESULT
============================================================
✓ PASS: Model accuracy is 92.14% (>= 90%)
The model is ready for deployment!
============================================================
```

### Output Files Generated

- **confusion_matrix.png** - Visual confusion matrix showing classification accuracy per disease class

### Interpreting Results

**Confusion Matrix:**
- **Diagonal (dark blue):** Correct predictions ✓
- **Off-diagonal (light colors):** Misclassifications (errors)
- **Goal:** Maximize diagonal values (want 90%+ correct)

**Per-Class Accuracy:**
- Shows how well model performs on each disease
- Ideally all classes ≥ 90%
- If one class is low, may need more training data for that class

**Overall Metrics:**
- **Accuracy:** Overall percentage correct (primary metric)
- **Precision:** Of predicted positives, how many were correct
- **Recall:** Of actual positives, how many were found
- **F1 Score:** Harmonic mean (balanced metric)

### Troubleshooting: Accuracy Below 90%

If accuracy is **below 90%**, try these improvements:

#### 1. **Increase Training Data**
```bash
# Download additional PlantVillage images from Kaggle
# Add more potato disease images to model/data/
```

#### 2. **Train Longer**
Edit `train.py`:
```python
train_model(epochs=50)  # Increase from 25 to 50
```

#### 3. **Adjust Learning Rate**
Edit `train.py` in `build_model()`:
```python
optimizer=Adam(learning_rate=0.0001)  # Lower learning rate
```

#### 4. **Increase Model Capacity**
Edit `train.py` custom head:
```python
x = Dense(256, activation='relu')(x)  # Increase from 128 to 256
x = Dropout(0.2)(x)                    # Reduce dropout from 0.3 to 0.2
```

#### 5. **Use Stronger Data Augmentation**
Edit `train.py` in `create_data_generators()`:
```python
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=40,        # Increase from 20
    width_shift=0.3,          # Increase from 0.2
    height_shift=0.3,         # Increase from 0.2
    shear_range=0.2,          # Add shearing
    horizontal_flip=True,
    zoom_range=0.3,           # Increase from 0.2
    fill_mode='nearest'
)
```

#### 6. **Unfreeze Base Model (Fine-tuning)**
Edit `train.py` in `build_model()`:
```python
# Unfreeze last layers of base model
base_model.trainable = True
for layer in base_model.layers[:-30]:  # Freeze first 30 layers
    layer.trainable = False
```

#### 7. **Try Different Base Model**
Edit `train.py`:
```python
# Instead of MobileNetV2, try:
base_model = ResNet50(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
# or
base_model = InceptionV3(input_shape=(299, 299, 3), include_top=False, weights='imagenet')
```

---

## Step 4: Deploy to AWS SageMaker

### Prerequisites

- AWS Account with SageMaker access
- AWS CLI configured: `aws configure`
- IAM role for SageMaker with S3 access

### Deployment Steps

```bash
cd model
python deploy.py
```

### What the Script Does

1. **Converts H5 Model to SavedModel Format**
   - Converts from Keras .h5 format to TensorFlow SavedModel
   - SavedModel is the production format for TensorFlow Serving

2. **Uploads Model to S3**
   - Creates S3 bucket: `potatoguard-models` (if doesn't exist)
   - Uploads SavedModel files
   - SageMaker accesses model from S3

3. **Creates SageMaker Endpoint**
   - Deploys model for real-time inference
   - Endpoint URL: `https://potatoguard-endpoint.sagemaker.<region>.amazonaws.com/`
   - Can handle HTTP requests with image data

4. **Saves Inference Function**
   - `test_single_image()` tests endpoint with potato leaf photo
   - Returns disease name and confidence score

### Endpoint Deployment Configuration

```python
# Instance types (choose based on traffic/cost)
'ml.t2.medium'      # Low traffic, cost-effective (~$0.05/hour)
'ml.t3.large'       # Medium traffic, ~$0.12/hour
'ml.c5.xlarge'      # High traffic, production-grade ~$0.25/hour
'ml.p3.2xlarge'     # GPU acceleration, ~$3.06/hour
```

### Using the Deployed Endpoint

```python
# Method 1: Using SageMaker predictor
from sagemaker.tensorflow import TensorFlowPredictor

predictor = TensorFlowPredictor('potatoguard-endpoint')
result = test_single_image('./potato_leaf.jpg', predictor=predictor)

# Method 2: Using boto3 runtime client
import boto3
runtime = boto3.client('sagemaker-runtime')

# Send image to endpoint and get prediction
response = runtime.invoke_endpoint(
    EndpointName='potatoguard-endpoint',
    ContentType='application/x-npy',
    Body=image_data
)
```

### Example: Test with Single Image

```python
# From deploy.py
result = test_single_image(
    image_path='./test_potato_leaf.jpg',
    endpoint_name='potatoguard-endpoint',
    class_names=['Healthy', 'Late Blight', 'Early Blight']
)

# Output:
# ============================================================
# TESTING ENDPOINT WITH SINGLE IMAGE
# ============================================================
# Image shape: (1, 224, 224, 3)
# 
# PREDICTION RESULT
# ============================================================
# Predicted Disease: Early Blight
# Confidence Score: 94.23%
# 
# Detailed Probabilities:
#   Healthy        :   3.45%
#   Late Blight    :   2.32%
#   Early Blight   :  94.23%
```

### Monitoring Endpoint Usage

```bash
# View endpoint status
aws sagemaker describe-endpoint --endpoint-name potatoguard-endpoint

# View CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/SageMaker \
  --metric-name ModelInvocations \
  --dimensions Name=EndpointName,Value=potatoguard-endpoint
```

### Deleting Endpoint (Stop Costs)

```bash
# When done, delete endpoint to stop charges
aws sagemaker delete-endpoint --endpoint-name potatoguard-endpoint
```

---

## Complete Workflow Summary

### For Local Development

```bash
# 1. Download dataset
# 2. Train model
python train.py

# 3. Evaluate accuracy
python evaluate.py
# Goal: ≥ 90% accuracy

# 4. Make predictions on local images
python
>>> import train
>>> model = __import__('tensorflow').keras.models.load_model('./potatoguard_model.h5')
>>> # Use model.predict() for inference
```

### For AWS SageMaker Deployment

```bash
# 1-3. (Same as above)

# 4. Deploy to SageMaker
python deploy.py

# 5. Make predictions via endpoint
python
>>> from deploy import test_single_image
>>> result = test_single_image('./leaf.jpg', endpoint_name='potatoguard-endpoint')
```

---

## Quick Reference: Commands

```bash
# Setup
cd model
pip install -r requirements.txt

# Training
python train.py

# Evaluation
python evaluate.py

# Deployment
python deploy.py

# Testing (in Python)
from deploy import test_single_image
test_single_image('./test_image.jpg', endpoint_name='potatoguard-endpoint')
```

---

## Model Architecture Details

### MobileNetV2 Base Model (Transfer Learning)

**Why MobileNetV2?**
- ✓ Lightweight (88 MB) - fast inference
- ✓ Pre-trained on 1.4M ImageNet images
- ✓ Already learned feature detection (edges, shapes, textures)
- ✓ Mobile-friendly (can run on edge devices)

**Transfer Learning Approach:**
1. Use pre-trained ImageNet weights (frozen)
2. Remove top classification layer
3. Add custom layers for potato disease classification
4. Train only the custom layers

**Benefits:**
- Requires less training data (only ~3,000 images total)
- Trains faster (converges in ~15-25 epochs)
- Better generalization
- Lower risk of overfitting

### Custom Classification Head

```
GlobalAveragePooling2D
  └─ Converts (7,7,1280) → (1280,)
  
Dense(128, ReLU)
  └─ Learn disease-specific patterns
  
Dropout(0.3)
  └─ Prevent overfitting by deactivating random neurons
  
Dense(3, Softmax)
  └─ Output: [P(Healthy), P(Early Blight), P(Late Blight)]
```

### Training Configuration

- **Optimizer:** Adam (adapts learning rate per parameter)
- **Loss Function:** Categorical Crossentropy (multi-class)
- **Batch Size:** 32 (balance between speed and accuracy)
- **Learning Rate:** 0.001 (typical for transfer learning)

---

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Overall Accuracy | ≥ 90% | ✓ Target |
| Per-Class Accuracy | ≥ 85% | ✓ Target |
| Inference Speed | < 100ms | ✓ MobileNetV2 |
| Model Size | < 100MB | ✓ ~88MB |

---

## Troubleshooting Guide

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: tensorflow` | Run `pip install -r requirements.txt` |
| `FileNotFoundError: ./data/` not found | Download dataset and verify directory structure |
| Low validation accuracy (< 90%) | See "Troubleshooting" section in Step 3 |
| Out of GPU memory | Reduce `batch_size` from 32 to 16 |
| Slow training | Use GPU instead of CPU; reduce dataset size |
| SageMaker endpoint fails | Verify AWS credentials and IAM permissions |

---

## Dataset Credits

- **Source:** PlantVillage Dataset (Kaggle)
- **License:** Public domain
- **Citation:** Hughes et al. (2015) "An Open Access Repository of Images on Plant Health to Enable the Development of Mobile Disease Diagnostics"

---

## Additional Resources

- **TensorFlow Docs:** https://www.tensorflow.org/
- **MobileNetV2 Paper:** https://arxiv.org/abs/1801.04381
- **SageMaker Docs:** https://docs.aws.amazon.com/sagemaker/
- **Plant Village:** https://plantvillage.psu.edu/

---

## Support & Questions

For PotatoGuard implementation questions:
1. Check troubleshooting sections above
2. Review comments in each Python script
3. Verify dataset structure matches examples
4. Check TensorFlow/SageMaker documentation

**Good luck building PotatoGuard! 🥔🌱**

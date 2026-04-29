"""
tests/test_model.py
===================
Validates that the trained CNN model meets the minimum 90% accuracy
requirement for PotatoGuard.

If the model file does not exist yet the test is SKIPPED automatically
so the CI pipeline stays green for the other test files.

Author : Katusiime Moreen  (feature/testing)
Project: PotatoGuard - Group 7, BSc Computer Science 2024/2025
"""

import os
import sys
import glob
import numpy as np
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

MODEL_PATH = os.path.join(ROOT, "model", "potatoguard_model.h5")
DATA_DIR = os.path.join(ROOT, "model", "data")

CLASS_FOLDERS = {
    "Potato___healthy": "Healthy",
    "Potato___Early_blight": "Early Blight",
    "Potato___Late_blight": "Late Blight",
}
CLASS_NAMES = ["Healthy", "Late Blight", "Early Blight", "Bacterial Wilt"]


@pytest.fixture(scope="module")
def model():
    """
    Load the saved Keras model once for all tests in this module.
    Skip the entire module if the model file does not exist yet.
    """
    if not os.path.exists(MODEL_PATH):
        pytest.skip(
            f"Model file not found at {MODEL_PATH}. "
            "Run model/train.py first or wait for Ayikoru to push it."
        )
    import tensorflow as tf
    loaded = tf.keras.models.load_model(MODEL_PATH)
    return loaded


def _load_test_images(n_per_class=5):
    """
    Grab up to n_per_class images from each disease folder under model/data/.
    Returns None, None if the data directory does not exist or is empty.
    """
    try:
        from PIL import Image
    except ImportError:
        return None, None

    images, labels = [], []
    label_map = {name: idx for idx, name in enumerate(CLASS_NAMES)}

    for folder_name, disease_label in CLASS_FOLDERS.items():
        folder_path = os.path.join(DATA_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue
        img_files = (
            glob.glob(os.path.join(folder_path, "*.JPG"))
            + glob.glob(os.path.join(folder_path, "*.jpg"))
            + glob.glob(os.path.join(folder_path, "*.png"))
        )[:n_per_class]
        for img_path in img_files:
            img = Image.open(img_path).convert("RGB").resize((224, 224))
            arr = np.array(img, dtype=np.float32) / 255.0
            images.append(arr)
            labels.append(label_map.get(disease_label, 0))

    if not images:
        return None, None
    return np.array(images), labels


def test_model_meets_90_percent_accuracy(model):
    """
    WHAT IT CHECKS:
    Load 5 test images from each disease class and run them through
    the trained model. The overall accuracy must be 90% or higher.
    """
    images, labels = _load_test_images(n_per_class=5)
    if images is None:
        pytest.skip(
            "No test images found in model/data/. "
            "Download the PlantVillage dataset first."
        )

    predictions = model.predict(images, verbose=0)
    predicted_classes = np.argmax(predictions, axis=1)
    correct = sum(p == t for p, t in zip(predicted_classes, labels))
    accuracy = correct / len(labels)
    accuracy_pct = accuracy * 100

    if accuracy >= 0.90:
        print(f"Model accuracy: {accuracy_pct:.1f}% - PASS")
    else:
        print(
            f"Model accuracy: {accuracy_pct:.1f}% - FAIL\n"
            "ACTION NEEDED: Retrain the model.\n"
            "Tips: increase epochs, reduce dropout, add more training images."
        )

    assert accuracy >= 0.90, (
        f"Model accuracy {accuracy_pct:.1f}% is below the required 90%. "
        "Please retrain the model."
    )

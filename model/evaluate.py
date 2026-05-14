"""
model/evaluate.py
=================
Model evaluation and validation script.

Author: Ayikoru Jackline (feature/ai-model)
Project: PotatoGuard - Group 7, BSc Computer Science 2024/2025
"""

import numpy as np
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns
import os

def evaluate_model(model_path='model/potatoguard_model.h5', data_dir='model/data', batch_size=32):
    """
    Load model and evaluate on test set.
    Generates confusion matrix and detailed metrics.
    """
    
    if not os.path.exists(model_path):
        print(f"✗ Model file not found: {model_path}")
        return False
    
    # Load model
    model = keras.models.load_model(model_path)
    print(f"✓ Loaded model from {model_path}")
    
    # Load test data
    test_datagen = ImageDataGenerator(rescale=1.0/255)
    test_generator = test_datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=False
    )
    
    # Get predictions
    print("Evaluating model...")
    predictions = model.predict(test_generator)
    true_labels = test_generator.classes
    pred_labels = np.argmax(predictions, axis=1)
    
    # Calculate metrics
    accuracy = accuracy_score(true_labels, pred_labels)
    precision = precision_score(true_labels, pred_labels, average='weighted')
    recall = recall_score(true_labels, pred_labels, average='weighted')
    f1 = f1_score(true_labels, pred_labels, average='weighted')
    
    # Per-class accuracy
    class_names = list(test_generator.class_indices.keys())
    cm = confusion_matrix(true_labels, pred_labels)
    
    print("\n=== Model Evaluation Results ===")
    print(f"Overall Accuracy: {accuracy*100:.1f}%")
    print(f"Precision: {precision*100:.1f}%")
    print(f"Recall: {recall*100:.1f}%")
    print(f"F1 Score: {f1*100:.1f}%")
    
    print("\nPer-Class Accuracy:")
    for i, class_name in enumerate(class_names):
        class_accuracy = cm[i, i] / cm[i].sum()
        print(f"  {class_name}: {class_accuracy*100:.1f}%")
    
    # Save confusion matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig('model/confusion_matrix.png')
    print("✓ Saved confusion matrix to model/confusion_matrix.png")
    
    # Pass/Fail determination
    if accuracy >= 0.90:
        print("\n✓ PASS: Model accuracy ≥ 90%")
        return True
    else:
        print(f"\n✗ FAIL: Model accuracy {accuracy*100:.1f}% < 90%")
        print("Consider retraining with more data or adjusting hyperparameters.")
        return False

if __name__ == '__main__':
    success = evaluate_model()
    exit(0 if success else 1)

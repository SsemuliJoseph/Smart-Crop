"""
PotatoGuard Model Evaluation Script
Evaluates the trained CNN model on the test dataset
Generates performance metrics, confusion matrix, and accuracy reports
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, confusion_matrix, classification_report)
from sklearn.preprocessing import LabelBinarizer
import matplotlib.pyplot as plt
import seaborn as sns


def load_trained_model(model_path='./potatoguard_model.h5'):
    """
    Load the trained CNN model from disk
    
    This function reads the saved model file that was created during training
    The model contains all the learned weights and architecture information
    
    Args:
        model_path: Path to the saved .h5 model file
    
    Returns:
        Loaded Keras model object ready for inference (making predictions)
    """
    
    # Check if the model file exists before trying to load it
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    # Load the saved model using Keras
    print(f"Loading trained model from {model_path}...")
    model = load_model(model_path)
    print("✓ Model loaded successfully!")
    
    return model


def prepare_test_data(data_dir='./data', image_size=224, batch_size=32):
    """
    Prepare test dataset using ImageDataGenerator
    
    This function loads images directly from disk using flow_from_directory
    Images are resized to 224x224 (same size as training) and normalized
    This step does NOT apply augmentation - we want to test on original images
    
    Args:
        data_dir: Path to data directory containing class subdirectories
        image_size: Image size for resizing (224x224 for MobileNetV2)
        batch_size: Number of images per batch for processing
    
    Returns:
        Tuple of (test_generator, class_names_list)
    """
    
    # Create a data generator that only rescales pixel values
    # Rescaling: converts pixel values from [0, 255] to [0, 1] range
    # This matches the normalization used during training
    test_datagen = ImageDataGenerator(rescale=1./255)
    
    print(f"\nLoading test data from {data_dir}...")
    
    # Load images from directory structure
    # Each subdirectory (Potato___healthy, Potato___Early_blight, etc.) is treated as a class
    test_generator = test_datagen.flow_from_directory(
        data_dir,
        target_size=(image_size, image_size),  # Resize all images to 224x224
        batch_size=batch_size,                 # Process 32 images at a time
        class_mode='categorical',              # Convert labels to one-hot encoding
        shuffle=False                          # Don't shuffle - keep order consistent
    )
    
    # Extract and sort class names (disease categories)
    # class_indices is a dictionary like {'Potato___healthy': 0, 'Potato___Early_blight': 1}
    class_names = sorted(test_generator.class_indices.keys())
    
    print(f"Found {len(class_names)} disease classes:")
    for idx, class_name in enumerate(class_names):
        print(f"  [{idx}] {class_name}")
    
    return test_generator, class_names


def get_predictions_and_labels(model, test_generator):
    """
    Generate predictions for all test images and collect true labels
    
    This function runs the model on the entire test set in batches
    For each image, we get predicted probabilities for all disease classes
    We convert these probabilities to class indices (argmax)
    
    Args:
        model: Trained Keras model ready for inference
        test_generator: Data generator yielding test batches
    
    Returns:
        Tuple of (predicted_labels, true_labels) as class indices (0, 1, 2, etc.)
    """
    
    print("\nGenerating predictions on test set...")
    
    # Lists to store all predictions and true labels
    all_predictions = []
    all_labels = []
    
    # Get total number of batches to process
    steps = len(test_generator)
    
    # Process test data batch by batch
    for batch_idx in range(steps):
        # Get next batch from the test generator
        # images: array of shape (batch_size, 224, 224, 3) containing pixel values
        # labels: one-hot encoded labels, shape (batch_size, num_classes)
        images, labels = next(test_generator)
        
        # Get model predictions for this batch of images
        # Returns probabilities for each class, shape (batch_size, num_classes)
        # Example: [0.05, 0.90, 0.05] means 90% confidence for class 1 (Early Blight)
        batch_predictions = model.predict(images, verbose=0)
        
        # Convert one-hot labels to class indices
        # argmax finds the index of the highest probability
        # Example: [0, 1, 0] → 1 (the class with the 1)
        batch_pred_labels = np.argmax(batch_predictions, axis=1)
        batch_true_labels = np.argmax(labels, axis=1)
        
        # Add this batch's predictions and labels to our lists
        all_predictions.extend(batch_pred_labels)
        all_labels.extend(batch_true_labels)
        
        # Print progress every so often
        if (batch_idx + 1) % max(1, steps // 5) == 0:
            print(f"  Processed {batch_idx + 1}/{steps} batches")
    
    # Convert lists to numpy arrays for easier manipulation
    return np.array(all_predictions), np.array(all_labels)


def calculate_per_class_accuracy(true_labels, pred_labels, class_names):
    """
    Calculate accuracy for each disease class separately
    
    This shows how well the model performs on each specific disease type
    For example, it helps identify if the model struggles with Early Blight
    but does well on Late Blight
    
    Algorithm:
    1. For each disease class
    2. Find all test images that actually belong to that class
    3. Count how many were predicted correctly
    4. Calculate accuracy = correct_count / total_count
    
    Args:
        true_labels: Array of true class labels (0, 1, 2, ...)
        pred_labels: Array of predicted class labels (0, 1, 2, ...)
        class_names: List of disease class names
    
    Returns:
        Dictionary mapping class names to their accuracy percentages
    """
    
    print("\n" + "="*60)
    print("PER-CLASS ACCURACY")
    print("="*60)
    
    per_class_accuracy = {}
    
    # Calculate accuracy for each class
    for class_idx, class_name in enumerate(class_names):
        # Create a mask: True for all samples belonging to this class
        # Example: [False, True, False, True, ...] for class index 1
        class_mask = true_labels == class_idx
        
        # Skip if this class has no samples
        if class_mask.sum() == 0:
            continue
        
        # Count how many predictions were correct for this class
        # We only check predictions where true label matches this class
        correct = (pred_labels[class_mask] == class_idx).sum()
        total = class_mask.sum()
        
        # Calculate percentage
        accuracy = (correct / total) * 100
        
        # Store result
        per_class_accuracy[class_name] = accuracy
        
        # Display result with colored formatting
        print(f"{class_name:30s}: {accuracy:6.2f}% ({correct}/{total})")
    
    return per_class_accuracy


def calculate_overall_metrics(true_labels, pred_labels, class_names):
    """
    Calculate overall performance metrics for the model
    
    Metrics calculated:
    1. Overall Accuracy: Percentage of all predictions that were correct
       Example: If 620 out of 624 predictions were correct = 99.36%
    
    2. Precision (weighted): For each class, how many predicted positives were actually positive
       Example: If we predicted 100 Early Blight cases, how many were actually Early Blight?
       Weighted = average across all classes, weighted by support (number of samples)
    
    3. Recall (weighted): For each class, how many actual cases were correctly identified
       Example: If there were 100 actual Early Blight cases, how many did we catch?
       Weighted = average across all classes, weighted by number of samples
    
    4. F1 Score (weighted): Harmonic mean of precision and recall
       High F1 score means good balance between precision and recall
       Weighted = average across all classes, weighted by number of samples
    
    Args:
        true_labels: Array of true class labels
        pred_labels: Array of predicted class labels
        class_names: List of disease class names
    
    Returns:
        Dictionary containing all calculated metrics
    """
    
    # Calculate overall accuracy across all classes
    overall_accuracy = accuracy_score(true_labels, pred_labels)
    
    # Calculate precision for each class (weighted average)
    # zero_division=0 means return 0 if no positive predictions exist
    precision = precision_score(true_labels, pred_labels, average='weighted', zero_division=0)
    
    # Calculate recall for each class (weighted average)
    recall = recall_score(true_labels, pred_labels, average='weighted', zero_division=0)
    
    # Calculate F1 score (harmonic mean of precision and recall)
    f1 = f1_score(true_labels, pred_labels, average='weighted', zero_division=0)
    
    # Print overall metrics
    print("\n" + "="*60)
    print("OVERALL PERFORMANCE METRICS")
    print("="*60)
    print(f"Overall Accuracy: {overall_accuracy*100:.2f}%")
    print(f"Precision (weighted):  {precision:.4f}")
    print(f"Recall (weighted):     {recall:.4f}")
    print(f"F1 Score (weighted):   {f1:.4f}")
    
    # Get detailed metrics per class
    print("\n" + "="*60)
    print("DETAILED CLASSIFICATION REPORT")
    print("="*60)
    print(classification_report(true_labels, pred_labels, target_names=class_names))
    
    return {
        'overall_accuracy': overall_accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }


def generate_confusion_matrix_image(true_labels, pred_labels, class_names, 
                                   output_path='./confusion_matrix.png'):
    """
    Generate and save a confusion matrix visualization
    
    What is a confusion matrix?
    - Shows actual vs predicted labels for all test samples
    - Rows represent true (actual) disease classes
    - Columns represent predicted disease classes
    - Each cell shows the count of samples
    
    Interpreting the matrix:
    ✓ Diagonal elements (top-left to bottom-right): Correct predictions
    ✗ Off-diagonal elements: Misclassifications (model mistakes)
    
    Example:
            Pred: Healthy  Early  Late
    True:
    Healthy     250        4      2     <- Model got 250/256 correct
    Early         3      175      2     <- Model got 175/180 correct
    Late          2        6    180     <- Model got 180/188 correct
    
    The heatmap color represents count (dark blue = high count = good)
    
    Args:
        true_labels: Array of true class labels
        pred_labels: Array of predicted class labels
        class_names: List of disease class names
        output_path: Path to save the confusion matrix image (PNG file)
    """
    
    print(f"\nGenerating confusion matrix visualization...")
    
    # Calculate the confusion matrix
    # cm[i][j] = count of samples that were actually class i but predicted as class j
    cm = confusion_matrix(true_labels, pred_labels)
    
    # Create a large figure for clarity (10x8 inches)
    plt.figure(figsize=(10, 8))
    
    # Create heatmap
    # annot=True: Show numbers in cells
    # fmt='d': Format as integers (no decimals)
    # cmap='Blues': Use blue color scheme (darker = higher values)
    sns.heatmap(
        cm,
        annot=True,                    # Show numbers inside cells
        fmt='d',                        # Format as integers
        cmap='Blues',                   # Blue color palette
        xticklabels=class_names,        # X-axis labels (predictions)
        yticklabels=class_names,        # Y-axis labels (true labels)
        cbar_kws={'label': 'Count'}     # Colorbar label
    )
    
    # Add title and axis labels
    plt.title('Confusion Matrix - Potato Disease Classification', fontsize=14, fontweight='bold')
    plt.ylabel('True Label (Actual Disease)', fontsize=12)
    plt.xlabel('Predicted Label (Model Prediction)', fontsize=12)
    
    # Adjust layout to prevent labels from being cut off
    plt.tight_layout()
    
    # Save the figure to a PNG file
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Confusion matrix saved to {output_path}")
    
    # Close the figure to free up memory
    plt.close()


def evaluate_model(model_path='./potatoguard_model.h5', data_dir='./data', 
                  image_size=224, batch_size=32):
    """
    Main evaluation pipeline
    
    This function orchestrates the entire evaluation process:
    
    Step 1: Load the trained model from disk
    Step 2: Prepare test dataset 
    Step 3: Generate predictions on all test images
    Step 4: Calculate accuracy for each disease class separately
    Step 5: Calculate overall metrics (accuracy, precision, recall, F1)
    Step 6: Generate confusion matrix visualization
    Step 7: Print PASS/FAIL assessment based on >= 90% accuracy threshold
    
    Args:
        model_path: Path to saved model file (usually ./potatoguard_model.h5)
        data_dir: Path to data directory (usually ./data)
        image_size: Image size (224x224 for MobileNetV2)
        batch_size: Batch size for processing (32 images at a time)
    """
    
    try:
        # Step 1: Load the trained model
        model = load_trained_model(model_path)
        
        # Step 2: Prepare test data
        test_generator, class_names = prepare_test_data(data_dir, image_size, batch_size)
        
        # Step 3: Generate predictions
        predicted_labels, true_labels = get_predictions_and_labels(model, test_generator)
        
        # Step 4: Calculate per-class accuracy
        per_class_acc = calculate_per_class_accuracy(true_labels, predicted_labels, class_names)
        
        # Step 5: Calculate overall metrics
        metrics = calculate_overall_metrics(true_labels, predicted_labels, class_names)
        
        # Step 6: Generate confusion matrix
        generate_confusion_matrix_image(true_labels, predicted_labels, class_names)
        
        # Step 7: Print PASS/FAIL assessment
        print("\n" + "="*60)
        print("EVALUATION RESULT")
        print("="*60)
        
        overall_accuracy = metrics['overall_accuracy'] * 100
        
        # Check if accuracy meets the threshold
        if overall_accuracy >= 90:
            print(f"✓ PASS: Model accuracy is {overall_accuracy:.2f}% (>= 90%)")
            print("✓ The model is ready for deployment!")
        else:
            print(f"✗ FAIL: Model accuracy is {overall_accuracy:.2f}% (< 90%)")
            print("\nSuggested improvements:")
            print("1. Train for more epochs:")
            print("   - Edit train.py and change: train_model(epochs=50)")
            print("   - More epochs give the model more chances to learn patterns")
            print("")
            print("2. Increase dataset size by:")
            print("   - Downloading more potato disease images from Kaggle PlantVillage")
            print("   - Having more diverse training examples helps generalization")
            print("")
            print("3. Adjust data augmentation (makes training data more varied):")
            print("   - In train.py, increase rotation_range from 20 to 40")
            print("   - Increase zoom_range from 0.2 to 0.3")
            print("   - This helps the model learn rotation-invariant features")
            print("")
            print("4. Adjust hyperparameters:")
            print("   - Try lower learning_rate: 0.0001 instead of 0.001")
            print("   - This helps the model converge more carefully")
            print("   - Increase Dense layer units from 128 to 256")
            print("   - Reduce Dropout from 0.3 to 0.2")
            print("")
            print("5. Try fine-tuning (unfreeze base model layers):")
            print("   - In train.py, set: base_model.trainable = True")
            print("   - This allows the model to adapt ImageNet weights to potatoes")
            print("")
            print("6. Try a different base model:")
            print("   - MobileNetV2: lightweight, fast")
            print("   - ResNet50: more accurate but heavier")
            print("   - InceptionV3: very accurate but slower")
        
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"Error during evaluation: {str(e)}")
        raise


if __name__ == "__main__":
    """
    Main entry point for the evaluation script
    
    Usage: python evaluate.py
    
    This script assumes:
    1. Model has been trained and saved as ./potatoguard_model.h5
    2. Test data is in ./data/ directory with subdirectories for each disease class
    """
    
    # Check if model exists
    model_path = './potatoguard_model.h5'
    if not os.path.exists(model_path):
        print(f"Error: Model file '{model_path}' not found!")
        print("Please run train.py first to train the model.")
        exit(1)
    
    # Check if data exists
    data_dir = './data'
    if not os.path.exists(data_dir):
        print(f"Error: Data directory '{data_dir}' not found!")
        print("Please ensure your data is in the ./data/ directory")
        exit(1)
    
    # Run evaluation with default parameters
    evaluate_model(
        model_path='./potatoguard_model.h5',
        data_dir='./data',
        image_size=224,
        batch_size=32
    )
    
    print("Evaluation script completed successfully!")

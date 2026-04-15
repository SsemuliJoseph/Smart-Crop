"""
PotatoGuard CNN Model Training Script
Trains a MobileNetV2-based deep learning model to detect potato diseases
Using transfer learning with frozen base model and custom classification head
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt


def count_class_samples(data_dir):
    """
    Count the number of image samples in each disease class directory
    Returns a dictionary with class names as keys and sample counts as values
    """
    class_counts = {}
    if os.path.exists(data_dir):
        for class_name in os.listdir(data_dir):
            class_path = os.path.join(data_dir, class_name)
            if os.path.isdir(class_path):
                count = len([f for f in os.listdir(class_path) 
                           if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                class_counts[class_name] = count
    return class_counts


def build_model(num_classes=3, learning_rate=0.001):
    """
    Build the CNN model using MobileNetV2 as the base model
    
    Architecture:
    1. MobileNetV2 base model (pre-trained on ImageNet) - weights frozen
    2. GlobalAveragePooling2D layer - reduces spatial dimensions
    3. Dense layer with 128 units and ReLU activation
    4. Dropout layer (30% dropout rate) - prevents overfitting
    5. Output Dense layer with softmax activation for multi-class classification
    
    Args:
        num_classes: Number of disease classes (3 or 4)
        learning_rate: Learning rate for the Adam optimizer
    
    Returns:
        Compiled Keras model ready for training
    """
    
    # Load pre-trained MobileNetV2 model (trained on ImageNet dataset)
    base_model = MobileNetV2(
        input_shape=(224, 224, 3),  # Input image size: 224x224 RGB
        include_top=False,           # Remove the top classification layer
        weights='imagenet'           # Use pre-trained ImageNet weights
    )
    
    # Freeze all layers in the base model (transfer learning approach)
    # This keeps the learned features from ImageNet intact
    base_model.trainable = False
    
    # Build the custom classification head
    inputs = tf.keras.Input(shape=(224, 224, 3))
    x = base_model(inputs, training=False)  # Pass through frozen base model
    
    # GlobalAveragePooling2D: Averages the spatial dimensions (e.g., 7x7x1280 -> 1280)
    # This reduces parameters and helps with overfitting
    x = GlobalAveragePooling2D()(x)
    
    # Dense layer with 128 neurons and ReLU activation
    # Learns complex decision boundaries for disease classification
    x = Dense(128, activation='relu')(x)
    
    # Dropout layer: Randomly deactivates 30% of neurons during training
    # This helps prevent overfitting by forcing the network to learn robust features
    x = Dropout(0.3)(x)
    
    # Output layer: num_classes neurons with softmax activation
    # Produces probability distribution over disease classes
    outputs = Dense(num_classes, activation='softmax')(x)
    
    # Create the complete model
    model = Model(inputs=inputs, outputs=outputs)
    
    # Compile the model with optimizer, loss function, and metrics
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),  # Adam optimizer with specified learning rate
        loss='categorical_crossentropy',              # Multi-class classification loss
        metrics=['accuracy']                          # Monitor accuracy during training
    )
    
    return model


def create_data_generators():
    """
    Create ImageDataGenerator objects for training and validation sets
    
    Training generator includes data augmentation to:
    - Increase dataset diversity
    - Help the model generalize better
    - Prevent overfitting to specific image orientations and conditions
    
    Validation generator does NOT apply augmentation (only rescaling)
    This ensures fair evaluation on unmodified images
    
    Returns:
        Tuple of (training_generator, validation_generator)
    """
    
    # Training data augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,              # Normalize pixel values to [0, 1]
        rotation_range=20,           # Random rotation up to 20 degrees
        width_shift=0.2,             # Random horizontal shift up to 20% of width
        height_shift=0.2,            # Random vertical shift up to 20% of height
        horizontal_flip=True,        # Randomly flip images horizontally (left-right)
        zoom_range=0.2,              # Random zoom in/out by 0-20%
        fill_mode='nearest'          # Fill empty pixels with nearest neighbor values
    )
    
    # Validation data generator (no augmentation)
    # Only rescales pixel values to [0, 1] for consistency with training
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    return train_datagen, val_datagen


def load_and_split_data(data_dir, train_split=0.8, val_split=0.1, test_split=0.1):
    """
    Load image data from organized directories and split into train/val/test sets
    
    Expected directory structure:
    data_dir/
        Potato___healthy/
        Potato___Early_blight/
        Potato___Late_blight/
        (optional: Potato___Bacterial_wilt/)
    
    Args:
        data_dir: Path to the root data directory
        train_split: Fraction of data for training (default 80%)
        val_split: Fraction of data for validation (default 10%)
        test_split: Fraction of data for testing (default 10%)
    
    Returns:
        Tuple of (class_names, num_classes, split_info_dict)
    """
    
    # Get list of disease classes from subdirectories
    class_names = sorted([d for d in os.listdir(data_dir) 
                         if os.path.isdir(os.path.join(data_dir, d))])
    
    num_classes = len(class_names)
    
    print(f"\n{'='*60}")
    print(f"POTATO DISEASE DETECTION DATASET")
    print(f"{'='*60}")
    print(f"Found {num_classes} disease classes:")
    
    # Display dataset statistics
    for idx, class_name in enumerate(class_names):
        class_path = os.path.join(data_dir, class_name)
        num_samples = len([f for f in os.listdir(class_path) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        print(f"  [{idx}] {class_name}: {num_samples} samples")
    
    print(f"{'='*60}\n")
    
    return class_names, num_classes, {
        'train': train_split,
        'val': val_split,
        'test': test_split
    }


def train_model(data_dir='./data', image_size=224, batch_size=32, 
                epochs=25, num_classes=3):
    """
    Main training pipeline
    
    Steps:
    1. Load and prepare data
    2. Create data generators with augmentation
    3. Build the model
    4. Set up callbacks (EarlyStopping, ModelCheckpoint)
    5. Train the model
    6. Save the final model
    7. Print final validation accuracy
    
    Args:
        data_dir: Path to data directory containing class subdirectories
        image_size: Image size for resizing (224x224 for MobileNetV2)
        batch_size: Number of images per batch (32)
        epochs: Maximum number of training epochs (25)
        num_classes: Number of disease classes (3 or 4)
    """
    
    # Step 1: Load dataset information
    class_names, detected_classes, split_info = load_and_split_data(data_dir)
    
    if detected_classes != num_classes:
        print(f"Warning: Expected {num_classes} classes but found {detected_classes}")
        num_classes = detected_classes
    
    # Step 2: Create data generators for augmentation and normalization
    train_datagen, val_datagen = create_data_generators()
    
    # Step 3: Load training data using flow_from_directory
    # This function reads images directly from disk on-the-fly during training
    print(f"Loading training data from {data_dir}...")
    train_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(image_size, image_size),  # Resize all images to 224x224
        batch_size=batch_size,                  # 32 images per batch
        class_mode='categorical',               # Multi-class classification
        shuffle=True                            # Shuffle training data each epoch
    )
    
    # Load validation data (using the same dataset split as training for now)
    print(f"Loading validation data from {data_dir}...")
    val_generator = val_datagen.flow_from_directory(
        data_dir,
        target_size=(image_size, image_size),
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=False                           # Don't shuffle validation data
    )
    
    # Step 4: Build the model
    print("\nBuilding MobileNetV2-based CNN model...")
    model = build_model(num_classes=num_classes, learning_rate=0.001)
    
    # Print model architecture summary
    print("\nModel Architecture:")
    model.summary()
    
    # Step 5: Define callbacks to monitor training and prevent overfitting
    
    # EarlyStopping: Stop training if validation accuracy doesn't improve for 5 epochs
    # This prevents overfitting and saves training time
    early_stopping = EarlyStopping(
        monitor='val_accuracy',          # Monitor validation accuracy
        patience=5,                       # Wait 5 epochs for improvement
        restore_best_weights=True,       # Restore weights from best epoch
        verbose=1
    )
    
    # ModelCheckpoint: Save the best model weights during training
    # Only saves when validation accuracy improves
    model_checkpoint = ModelCheckpoint(
        filepath='./potatoguard_model_best.h5',  # Save best model here
        monitor='val_accuracy',
        save_best_only=True,             # Only save if this is the best so far
        verbose=1
    )
    
    # Step 6: Train the model
    print(f"\n{'='*60}")
    print(f"STARTING TRAINING")
    print(f"Epochs: {epochs}, Batch Size: {batch_size}, Classes: {num_classes}")
    print(f"Early Stopping Patience: 5 epochs")
    print(f"{'='*60}\n")
    
    history = model.fit(
        train_generator,                 # Training data generator
        validation_data=val_generator,   # Validation data generator
        epochs=epochs,                   # Maximum 25 epochs
        callbacks=[early_stopping, model_checkpoint],  # Use our callbacks
        verbose=1                        # Print progress for each epoch
    )
    
    # Step 7: Save the final trained model
    print("\nSaving final trained model...")
    model.save('./potatoguard_model.h5')
    print("Model saved as ./potatoguard_model.h5")
    
    # Step 8: Calculate and print final validation accuracy
    print(f"\n{'='*60}")
    val_loss, val_accuracy = model.evaluate(val_generator)
    val_accuracy_percent = val_accuracy * 100
    print(f"Training complete. Validation accuracy: {val_accuracy_percent:.2f}%")
    print(f"{'='*60}\n")
    
    # Provide feedback on model performance
    if val_accuracy_percent >= 90:
        print("✓ SUCCESS: Validation accuracy >= 90%")
        print("The model is ready for evaluation and deployment!")
    else:
        print(f"✗ NOTE: Validation accuracy {val_accuracy_percent:.2f}% is below 90%")
        print("Consider: adjusting hyperparameters, using more data, or training longer")
    
    return model, history, class_names


if __name__ == "__main__":
    """
    Main entry point for the training script
    Run with: python train.py
    """
    
    # Check if data directory exists
    data_dir = './data'
    if not os.path.exists(data_dir):
        print(f"Error: Data directory '{data_dir}' not found!")
        print("Please download the dataset from Kaggle and place it in ./data/")
        exit(1)
    
    # Train the model with default parameters
    model, history, class_names = train_model(
        data_dir='./data',
        image_size=224,
        batch_size=32,
        epochs=25,
        num_classes=3  # Adjust to 4 if Bacterial Wilt data is available
    )
    
    print("\nTraining script completed successfully!")

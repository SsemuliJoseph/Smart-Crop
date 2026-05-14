"""
model/train.py
==============
CNN training script for PotatoGuard.
Trains MobileNetV2 model for potato disease classification.

Author: Ayikoru Jackline (feature/ai-model)
Project: PotatoGuard - Group 7, BSc Computer Science 2024/2025
"""

import os
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers, applications
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from pathlib import Path

def train_model(data_dir='model/data', epochs=25, batch_size=32):
    """
    Train MobileNetV2 CNN for potato disease detection.
    
    Directory structure expected:
    model/data/
    ├── Potato___healthy/
    ├── Potato___Early_blight/
    └── Potato___Late_blight/
    """
    
    # Find all disease classes
    classes = []
    for item in Path(data_dir).iterdir():
        if item.is_dir() and 'Potato' in item.name:
            classes.append(item.name)
    
    num_classes = len(classes)
    print(f"Found {num_classes} disease classes: {classes}")
    
    if num_classes == 0:
        print("ERROR: No potato disease directories found!")
        return None
    
    # Data preprocessing
    train_datagen = ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        rescale=1.0/255,
        validation_split=0.1
    )
    
    # Load training data
    train_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        subset='training'
    )
    
    val_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        subset='validation'
    )
    
    # Build model with MobileNetV2
    base_model = applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False  # Freeze base model
    
    # Add custom layers
    model = keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer=keras.optimizers.Adam(lr=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        ),
        keras.callbacks.ModelCheckpoint(
            'model/potatoguard_model_best.h5',
            monitor='val_accuracy',
            save_best_only=True
        )
    ]
    
    # Train
    print(f"Training for {epochs} epochs...")
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=epochs,
        callbacks=callbacks
    )
    
    # Save model
    model.save('model/potatoguard_model.h5')
    print("✓ Model saved to model/potatoguard_model.h5")
    
    # Get final validation accuracy
    val_accuracy = history.history['val_accuracy'][-1]
    print(f"Training complete. Validation accuracy: {val_accuracy*100:.1f}%")
    
    if val_accuracy >= 0.90:
        print("✓ PASS: Model meets ≥90% accuracy requirement")
    else:
        print("✗ FAIL: Model accuracy below 90%. Retrain with more data.")
    
    return model

if __name__ == '__main__':
    model = train_model()

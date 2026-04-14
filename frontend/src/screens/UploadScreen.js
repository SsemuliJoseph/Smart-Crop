import React, { useState } from 'react';
import { View, Text, TouchableOpacity, Image, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { detectDisease } from '../services/api';

// Screen where users can upload or take a photo of a potato leaf
export default function UploadScreen({ navigation }) {
  const [image, setImage] = useState(null); // stores the selected image object
  const [loading, setLoading] = useState(false);

  // Opens the camera to take a photo
  const takePhoto = async () => {
    const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
    if (permissionResult.granted === false) {
      Alert.alert("Permission Required", "You need to allow camera access.");
      return;
    }
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
      base64: true, // Generate base64 string
    });
    if (!result.canceled) {
      setImage(result.assets[0]);
    }
  };

  // Opens the gallery to pick an existing image
  const chooseFromGallery = async () => {
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (permissionResult.granted === false) {
      Alert.alert("Permission Required", "You need to allow gallery access.");
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
      base64: true, // Generate base64 string
    });
    if (!result.canceled) {
      setImage(result.assets[0]);
    }
  };

  // Converts image to base64, calls the API, and handles the result
  const handleDetectDisease = async () => {
    if (!image) {
      Alert.alert("No Image", "Please select or take an image first.");
      return;
    }
    setLoading(true);
    try {
      // Calls detectDisease() passing the base64 string
      const response = await detectDisease(image.base64);
      setLoading(false);
      
      // On success: navigates to ResultScreen passing the result
      navigation.navigate('Result', {
        disease: response.disease,
        confidence: response.confidence,
        treatment: response.treatment
      });
    } catch (error) {
      setLoading(false);
      // On error: shows an Alert with the error message
      Alert.alert("Detection Error", error.message);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.instructions}>Please capture a clear photo of the potato leaf.</Text>
      
      {/* Two buttons for choosing image source */}
      <View style={styles.buttonRow}>
        <TouchableOpacity style={styles.actionBtn} onPress={takePhoto}>
          <Text style={styles.actionBtnText}>Take Photo</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionBtn} onPress={chooseFromGallery}>
          <Text style={styles.actionBtnText}>Choose from Gallery</Text>
        </TouchableOpacity>
      </View>

      {/* Show a preview of the selected photo in a box */}
      <View style={styles.previewBox}>
        {image ? (
          <Image source={{ uri: image.uri }} style={styles.imagePreview} />
        ) : (
          <Text style={styles.placeholderText}>No photo selected</Text>
        )}
      </View>

      {/* Loading spinner or Detect Disease button */}
      {loading ? (
        <ActivityIndicator size="large" color="#1B5E20" style={{ marginTop: 20 }} />
      ) : (
        <TouchableOpacity style={styles.detectBtn} onPress={handleDetectDisease}>
          <Text style={styles.detectBtnText}>Detect Disease</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#F7F9F9',
  },
  instructions: {
    fontSize: 16,
    marginBottom: 20,
    color: '#555',
    textAlign: 'center',
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    marginBottom: 20,
  },
  actionBtn: {
    flex: 1,
    backgroundColor: '#4A148C',
    paddingVertical: 14,
    marginHorizontal: 5,
    borderRadius: 8,
    alignItems: 'center',
  },
  actionBtnText: {
    color: '#FFF',
    fontWeight: 'bold',
  },
  previewBox: {
    width: '100%',
    height: 300,
    backgroundColor: '#E0E0E0',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 30,
    overflow: 'hidden', // Ensures image stays inside rounded corners
  },
  imagePreview: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  placeholderText: {
    color: '#777',
  },
  detectBtn: {
    backgroundColor: '#1B5E20',
    width: '100%',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  detectBtnText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
  }
});

import axios from 'axios';
import * as FileSystem from 'expo-file-system';

const API_BASE_URL = process.env.API_BASE_URL || 'https://YOUR_API_GATEWAY_URL/prod';

// Convert image URI to base64
async function imageToBase64(imageUri) {
  const base64 = await FileSystem.readAsStringAsync(imageUri, {
    encoding: FileSystem.EncodingType.Base64,
  });
  return base64;
}

// Detect disease from image
export async function detectDisease(imageUri) {
  try {
    const imageBase64 = await imageToBase64(imageUri);
    const response = await axios.post(`${API_BASE_URL}/detect`, {
      image_base64: imageBase64,
      farmer_id: 'farmer001',
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Detection failed');
  }
}

// Get history for farmer
export async function getHistory(farmerId) {
  try {
    const response = await axios.get(`${API_BASE_URL}/history/${farmerId}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to fetch history');
  }
}

// Get single report
export async function getReport(detectionId) {
  try {
    const response = await axios.get(`${API_BASE_URL}/report/${detectionId}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to fetch report');
  }
}

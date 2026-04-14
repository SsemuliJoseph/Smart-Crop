import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

// Screen that displays the results of the disease detection
export default function ResultScreen({ route, navigation }) {
  // Read route.params to get disease, confidence, treatment
  // Provide fallback values in case they aren't passed
  const { disease = 'Unknown', confidence = 0, treatment = 'No treatment data given.' } = route.params || {};

  // Determine colors based on disease
  let bannerColor = '#ccc';
  if (disease === 'Healthy') {
    bannerColor = '#4CAF50'; // Green
  } else if (disease === 'Late Blight') {
    bannerColor = '#F44336'; // Red
  } else if (disease === 'Early Blight') {
    bannerColor = '#FF9800'; // Orange
  } else if (disease === 'Bacterial Wilt') {
    bannerColor = '#9C27B0'; // Purple
  }

  return (
    <View style={styles.container}>
      {/* Colored banner depending on disease */}
      <View style={[styles.banner, { backgroundColor: bannerColor }]}>
        <Text style={styles.diseaseText}>{disease}</Text>
        <Text style={styles.confidenceText}>Confidence: {confidence}%</Text>
      </View>

      {/* Treatment Advice section */}
      <View style={styles.adviceContainer}>
        <Text style={styles.adviceTitle}>Treatment Advice</Text>
        <Text style={styles.adviceText}>{treatment}</Text>
      </View>

      {/* Button to go back and scan another leaf */}
      <TouchableOpacity style={styles.scanBtn} onPress={() => navigation.navigate('Upload')}>
        <Text style={styles.scanBtnText}>Scan Another Leaf</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F7F9F9',
    alignItems: 'center',
    padding: 20,
  },
  banner: {
    width: '100%',
    paddingVertical: 30,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 30,
  },
  diseaseText: {
    // Show disease name in LARGE text (fontSize 28, bold)
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 10,
  },
  confidenceText: {
    fontSize: 18,
    color: '#FFFFFF',
  },
  adviceContainer: {
    width: '100%',
    backgroundColor: '#FFF',
    padding: 20,
    borderRadius: 12,
    marginBottom: 40,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  adviceTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  adviceText: {
    fontSize: 16,
    color: '#555',
    lineHeight: 24,
  },
  scanBtn: {
    backgroundColor: '#1B5E20',
    width: '100%',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  scanBtnText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  }
});

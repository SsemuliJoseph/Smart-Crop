import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

// A reusable card component to display a disease detection record
export default function DiseaseCard({ disease, confidence, date }) {
  // Determine what emoji to show based on the disease name
  let emoji = '❔';
  if (disease === 'Healthy') {
    emoji = '🌿';
  } else if (disease && (disease.includes('Blight') || disease.includes('Wilt'))) {
    emoji = '⚠️';
  }

  return (
    <View style={styles.card}>
      <View style={styles.row}>
        <Text style={styles.diseaseName}>{emoji} {disease}</Text>
        <Text style={styles.date}>{date}</Text>
      </View>
      <Text style={styles.confidence}>Confidence: {confidence}%</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    marginVertical: 8,
    marginHorizontal: 16,
    borderRadius: 12,
    // Rounded corners and subtle shadow styling
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  diseaseName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  date: {
    fontSize: 14,
    color: '#888',
  },
  confidence: {
    fontSize: 16,
    color: '#1B5E20',
  }
});
// Bring in React to build our user interface
import React from 'react';
// Bring in basic building blocks for mobile apps from React Native
// View is like a box, Text is for words, TouchableOpacity is a clickable button, StyleSheet is for styling, SafeAreaView keeps it away from the phone notch
import { View, Text, TouchableOpacity, StyleSheet, SafeAreaView } from 'react-native';

// Create our Home Screen and receive a special 'navigation' tool to jump to other screens
const HomeScreen = ({ navigation }) => {
  
  // This function runs when the user taps "Scan". It tells the app to go to "Upload" screen.
  const handleNavigateToUpload = () => {
    navigation.navigate('Upload');
  };

  // This function runs when the user taps "History". It tells the app to go to "History" screen.
  const handleNavigateToHistory = () => {
    navigation.navigate('History');
  };

  // Here we draw what the screen looks like
  return (
    // SafeAreaView makes sure the app doesn't go under the battery/clock on the top of the phone
    <SafeAreaView style={styles.mainContainer}>
      
      {/* A box to hold our app title and subtitle */}
      <View style={styles.headerSection}>
        {/* Big text for the app name */}
        <Text style={styles.titleText}>PotatoGuard</Text>
        {/* Smaller text explaining what the app does */}
        <Text style={styles.subtitleText}>Detect potato diseases instantly with AI</Text>
      </View>

      {/* A box to hold our two buttons */}
      <View style={styles.buttonSection}>
        
        {/* Our "Scan" button that is easy to click (it dims when touched) */}
        {/* It uses two styles: one for the shape, one for the green color */}
        <TouchableOpacity 
          style={[styles.baseButton, styles.scanButtonColor]} 
          onPress={handleNavigateToUpload}
        >
          {/* Inside the button, put this text and make it white */}
          <Text style={styles.buttonText}>Scan a Leaf Now</Text>
        </TouchableOpacity>

        {/* Our "History" button that dims when touched */}
        {/* It uses two styles: one for the shape, one for the purple color */}
        <TouchableOpacity 
          style={[styles.baseButton, styles.historyButtonColor]} 
          onPress={handleNavigateToHistory}
        >
          {/* Inside the button, put this text and make it white */}
          <Text style={styles.buttonText}>View History</Text>
        </TouchableOpacity>
        
      </View>

    </SafeAreaView>
  );
};

// Here we define all our colors, sizes, and spacing (like CSS for the web)
const styles = StyleSheet.create({
  // The main wrapper covering the whole screen
  mainContainer: {
    flex: 1, // Stretch to fill all available space
    backgroundColor: '#F7F9F9', // A very light gray/off-white background
    alignItems: 'center', // Center everything left-to-right
    justifyContent: 'center', // Center everything top-to-bottom
    paddingHorizontal: 20, // Add a little empty space on the left and right edges
  },
  // The box holding the title text
  headerSection: {
    alignItems: 'center', // Keep the text centered
    marginBottom: 60, // Push the buttons down by adding 60 units of empty space below the text
  },
  // Style for the main PotatoGuard title
  titleText: {
    fontSize: 40, // Very large text size
    fontWeight: 'bold', // Make the text thick/bold
    color: '#1B5E20', // Give it a dark green color
    marginBottom: 8, // Leave a tiny gap beneath it
  },
  // Style for the description text
  subtitleText: {
    fontSize: 16, // Normal reading size
    color: '#555555', // Grey text so it's not too harsh
    textAlign: 'center', // Make sure wrapped text stays in the middle
  },
  // The box holding the buttons
  buttonSection: {
    width: '100%', // Stretch the box across the whole screen width
    alignItems: 'center', // Center the buttons inside this box
  },
  // Shared styles that BOTH buttons will use
  baseButton: {
    width: '85%', // Make the button 85% as wide as the screen
    paddingVertical: 16, // Make the button tall enough to easily tap
    borderRadius: 12, // Curve the corners of the button
    alignItems: 'center', // Put the button text dead center
    marginBottom: 20, // Leave a gap before the next button
    // The next four lines add a tiny drop shadow to make the buttons pop out
    elevation: 3, // Shadow for Android
    shadowColor: '#000', // Shadow colour for iOS
    shadowOffset: { width: 0, height: 2 }, // How far shadow drops for iOS
    shadowOpacity: 0.15, // How dark shadow is for iOS
    shadowRadius: 3, // How blurry shadow is for iOS
  },
  // Specific style for the scan button
  scanButtonColor: {
    backgroundColor: '#1B5E20', // Dark green matching PotatoGuard branding
  },
  // Specific style for the history button
  historyButtonColor: {
    backgroundColor: '#4A148C', // Deep purple
  },
  // Style for the words inside the buttons
  buttonText: {
    color: '#FFFFFF', // White text so it stands out against dark green/purple
    fontWeight: 'bold', // Bold text just for emphasis
    fontSize: 16, // Text size inside buttons
  }
});

// We make this screen available so App.js can import and use it
export default HomeScreen;

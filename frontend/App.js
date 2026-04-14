// We bring in the React library which helps us build user interfaces
import React from 'react';
// We bring in a container that will hold all our app's screens
import { NavigationContainer } from '@react-navigation/native';
// We bring in a tool to let users move between screens in a stack (one after another)
import { createNativeStackNavigator } from '@react-navigation/native-stack';

// We bring in the Home screen that we built in another file
import HomeScreen from './src/screens/HomeScreen';
// We bring in the Upload screen for scanning leaves
import UploadScreen from './src/screens/UploadScreen';
// We bring in the Result screen to show AI results
import ResultScreen from './src/screens/ResultScreen';
// We bring in the History screen to see past scans
import HistoryScreen from './src/screens/HistoryScreen';
// We bring in the Login screen for users to sign in
import LoginScreen from './src/screens/LoginScreen';

// We create our stack navigator and save it in a variable called 'Stack'
const Stack = createNativeStackNavigator();

// This is the main part of our app that gets run first
export default function App() {
  // It returns the visual part of the app
  return (
    // NavigationContainer is like a big box that holds all our routing
    <NavigationContainer>
      {/* Stack.Navigator manages the screens. We tell it to show the "Login" screen first */}
      <Stack.Navigator initialRouteName="Login">
        
        {/* We define a screen named "Login" and tell it to use the LoginScreen component */}
        {/* The top bar will show the title "Welcome to PotatoGuard" */}
        <Stack.Screen 
          name="Login" 
          component={LoginScreen} 
          options={{ title: 'Welcome to PotatoGuard' }} 
        />
        
        {/* We define a screen named "Home" and tell it to use the HomeScreen component */}
        {/* The top bar will show the title "Home" */}
        <Stack.Screen 
          name="Home" 
          component={HomeScreen} 
          options={{ title: 'Home' }} 
        />
        
        {/* We define a screen named "Upload" for scanning */}
        {/* The top bar will show the title "Scan a Leaf" */}
        <Stack.Screen 
          name="Upload" 
          component={UploadScreen} 
          options={{ title: 'Scan a Leaf' }} 
        />
        
        {/* We define a screen named "Result" to show what the AI found */}
        {/* The top bar will show the title "Analysis Result" */}
        <Stack.Screen 
          name="Result" 
          component={ResultScreen} 
          options={{ title: 'Analysis Result' }} 
        />
        
        {/* We define a screen named "History" to see past action */}
        {/* The top bar will show the title "Scan History" */}
        <Stack.Screen 
          name="History" 
          component={HistoryScreen} 
          options={{ title: 'Scan History' }} 
        />
        
      {/* We finish defining our screens inside the Stack Navigator */}
      </Stack.Navigator>
    {/* We close our NavigationContainer box */}
    </NavigationContainer>
  );
}

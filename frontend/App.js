import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { View, Text } from 'react-native';

// Import Home Screen
import HomeScreen from './src/screens/HomeScreen';

// Dummy components for other screens to prevent crashes since they are assigned to other team members
const UploadScreen = () => <View><Text>Upload Screen Placeholder</Text></View>;
const ResultScreen = () => <View><Text>Result Screen Placeholder</Text></View>;
const HistoryScreen = () => <View><Text>History Screen Placeholder</Text></View>;
const LoginScreen = () => <View><Text>Login Screen Placeholder</Text></View>;

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen name="Home" component={HomeScreen} options={{ title: 'PotatoGuard Home' }} />
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Upload" component={UploadScreen} />
        <Stack.Screen name="Result" component={ResultScreen} />
        <Stack.Screen name="History" component={HistoryScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

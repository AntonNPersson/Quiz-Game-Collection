/**
 * Truth or Dare Mobile App
 * 
 * Main entry point for the Truth or Dare mobile application.
 * Built with React Native and Expo for cross-platform compatibility.
 */

import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Alert } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { SafeAreaProvider } from 'react-native-safe-area-context';

// Import screens
import WelcomeScreen from './src/screens/WelcomeScreen';
import SetupScreen from './src/screens/SetupScreen';
import GameScreen from './src/screens/GameScreen';

// Create navigation stack
const Stack = createStackNavigator();

// Simple loading component
function LoadingScreen() {
  return (
    <View style={styles.loadingContainer}>
      <Text style={styles.loadingText}>🎭 Truth or Dare</Text>
      <Text style={styles.loadingSubtext}>Loading...</Text>
    </View>
  );
}

// Simple error boundary
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('App Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>🚫 Something went wrong</Text>
          <Text style={styles.errorText}>
            {this.state.error?.message || 'Unknown error occurred'}
          </Text>
          <Text style={styles.errorSubtext}>
            Check the console for more details
          </Text>
        </View>
      );
    }

    return this.props.children;
  }
}

export default function App() {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    async function prepare() {
      try {
        // Simple initialization
        console.log('Truth or Dare app starting...');
        
        // Simulate loading time
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        console.log('App ready!');
      } catch (error) {
        console.error('Error during app initialization:', error);
        Alert.alert('Initialization Error', error.message);
      } finally {
        setIsReady(true);
      }
    }

    prepare();
  }, []);

  if (!isReady) {
    return <LoadingScreen />;
  }

  return (
    <ErrorBoundary>
      <SafeAreaProvider>
        <NavigationContainer>
          <StatusBar style="dark" backgroundColor="#F8FAFC" />
          <Stack.Navigator
            initialRouteName="Welcome"
            screenOptions={{
              headerStyle: {
                backgroundColor: '#FFFFFF',
              },
              headerTintColor: '#1A202C',
              headerTitleStyle: {
                fontSize: 18,
                fontWeight: 'bold',
              },
              cardStyle: {
                backgroundColor: '#F8FAFC',
              },
            }}
          >
            <Stack.Screen 
              name="Welcome" 
              component={WelcomeScreen}
              options={{ 
                headerShown: false,
              }}
            />
            <Stack.Screen 
              name="Setup" 
              component={SetupScreen}
              options={{ 
                title: '🎮 Game Setup',
                headerBackTitle: 'Back',
              }}
            />
            <Stack.Screen 
              name="Game" 
              component={GameScreen}
              options={{ 
                title: '🎭 Truth or Dare',
                headerLeft: null,
                gestureEnabled: false,
              }}
            />
          </Stack.Navigator>
        </NavigationContainer>
      </SafeAreaProvider>
    </ErrorBoundary>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
  },
  loadingText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1A202C',
    marginBottom: 10,
  },
  loadingSubtext: {
    fontSize: 16,
    color: '#718096',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FED7D7',
    padding: 20,
  },
  errorTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#C53030',
    marginBottom: 10,
    textAlign: 'center',
  },
  errorText: {
    fontSize: 16,
    color: '#742A2A',
    textAlign: 'center',
    marginBottom: 10,
  },
  errorSubtext: {
    fontSize: 14,
    color: '#A0AEC0',
    textAlign: 'center',
  },
});

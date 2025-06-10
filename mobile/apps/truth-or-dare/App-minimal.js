/**
 * Minimal Truth or Dare Mobile App
 * 
 * Ultra-simple version to test PlatformConstants error
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { StatusBar } from 'expo-status-bar';

export default function App() {
  return (
    <View style={styles.container}>
      <StatusBar style="dark" />
      <Text style={styles.title}>🎭 Truth or Dare</Text>
      <Text style={styles.subtitle}>Minimal Test Version</Text>
      <TouchableOpacity style={styles.button}>
        <Text style={styles.buttonText}>App is working!</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    padding: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1A202C',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#718096',
    marginBottom: 40,
  },
  button: {
    backgroundColor: '#E53E3E',
    paddingHorizontal: 24,
    paddingVertical: 16,
    borderRadius: 12,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

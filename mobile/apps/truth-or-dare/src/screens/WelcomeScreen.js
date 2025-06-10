/**
 * Welcome Screen - Truth or Dare Mobile App
 * 
 * Main menu screen with navigation to different app sections.
 * Simplified version without external dependencies.
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function WelcomeScreen({ navigation }) {
  const menuItems = [
    {
      title: '🎮 Start New Game',
      subtitle: 'Begin a new Truth or Dare session',
      onPress: () => navigation.navigate('Setup'),
      color: '#E53E3E',
    },
    {
      title: '⚙️ Settings',
      subtitle: 'Customize themes and preferences',
      onPress: () => {
        // For now, just show an alert
        alert('Settings coming soon!');
      },
      color: '#3182CE',
    },
    {
      title: '📊 Statistics',
      subtitle: 'View question database stats',
      onPress: () => {
        // For now, just show an alert
        alert('Statistics coming soon!');
      },
      color: '#38A169',
    },
  ];

  const renderMenuItem = (item, index) => {
    return (
      <TouchableOpacity
        key={index}
        style={[styles.menuItem, { backgroundColor: item.color }]}
        onPress={item.onPress}
        activeOpacity={0.8}
      >
        <Text style={styles.menuTitle}>
          {item.title}
        </Text>
        <Text style={styles.menuSubtitle}>
          {item.subtitle}
        </Text>
      </TouchableOpacity>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView 
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header Section */}
        <View style={styles.header}>
          <Text style={styles.title}>
            🎭 Truth or Dare 🎭
          </Text>
          <Text style={styles.subtitle}>
            The Ultimate Party Game
          </Text>
        </View>

        {/* Menu Section */}
        <View style={styles.menuContainer}>
          {menuItems.map(renderMenuItem)}
        </View>

        {/* Footer Section */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Part of Quiz Game Collection
          </Text>
          <Text style={styles.footerText}>
            v1.0.0
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 40,
  },
  header: {
    alignItems: 'center',
    marginBottom: 60,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1A202C',
    textAlign: 'center',
    marginBottom: 16,
  },
  subtitle: {
    fontSize: 18,
    color: '#4A5568',
    textAlign: 'center',
  },
  menuContainer: {
    flex: 1,
    justifyContent: 'center',
    maxWidth: 400,
    alignSelf: 'center',
    width: '100%',
  },
  menuItem: {
    paddingVertical: 20,
    paddingHorizontal: 24,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 80,
    marginBottom: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  menuTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
    textAlign: 'center',
  },
  menuSubtitle: {
    fontSize: 14,
    color: '#FFFFFF',
    opacity: 0.9,
    marginTop: 4,
    textAlign: 'center',
  },
  footer: {
    alignItems: 'center',
    marginTop: 40,
  },
  footerText: {
    fontSize: 12,
    color: '#718096',
    textAlign: 'center',
    marginBottom: 4,
  },
});

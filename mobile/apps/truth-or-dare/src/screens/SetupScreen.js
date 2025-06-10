/**
 * Setup Screen - Truth or Dare Mobile App
 * 
 * Game configuration screen for setting up players and game options.
 * Simplified version without external dependencies.
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ScrollView,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function SetupScreen({ navigation }) {
  const [players, setPlayers] = useState(['']);
  const [questionCount, setQuestionCount] = useState('15');
  const [spiceLevel, setSpiceLevel] = useState('mild');

  const addPlayer = () => {
    if (players.length < 8) {
      setPlayers([...players, '']);
    } else {
      Alert.alert('Maximum Players', 'You can add up to 8 players maximum.');
    }
  };

  const removePlayer = (index) => {
    if (players.length > 1) {
      const newPlayers = players.filter((_, i) => i !== index);
      setPlayers(newPlayers);
    }
  };

  const updatePlayer = (index, name) => {
    const newPlayers = [...players];
    newPlayers[index] = name;
    setPlayers(newPlayers);
  };

  const startGame = () => {
    // Validate players
    const validPlayers = players.filter(name => name.trim().length > 0);
    
    if (validPlayers.length < 2) {
      Alert.alert('Not Enough Players', 'You need at least 2 players to start the game.');
      return;
    }

    // Navigate to game screen with settings
    navigation.navigate('Game', {
      players: validPlayers,
      questionCount: parseInt(questionCount) || 15,
      spiceLevel: spiceLevel,
    });
  };

  const spiceLevels = [
    { id: 'mild', name: 'Mild 😊', color: '#38A169' },
    { id: 'medium', name: 'Medium 🌶️', color: '#D69E2E' },
    { id: 'spicy', name: 'Spicy 🔥', color: '#E53E3E' },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        
        {/* Players Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>👥 Players</Text>
          <Text style={styles.sectionSubtitle}>Add 2-8 players to start the game</Text>
          
          {players.map((player, index) => (
            <View key={index} style={styles.playerRow}>
              <TextInput
                style={styles.playerInput}
                placeholder={`Player ${index + 1} name`}
                value={player}
                onChangeText={(text) => updatePlayer(index, text)}
                maxLength={20}
              />
              {players.length > 1 && (
                <TouchableOpacity
                  style={styles.removeButton}
                  onPress={() => removePlayer(index)}
                >
                  <Text style={styles.removeButtonText}>✕</Text>
                </TouchableOpacity>
              )}
            </View>
          ))}
          
          {players.length < 8 && (
            <TouchableOpacity style={styles.addButton} onPress={addPlayer}>
              <Text style={styles.addButtonText}>+ Add Player</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Question Count Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🎯 Number of Questions</Text>
          <TextInput
            style={styles.numberInput}
            value={questionCount}
            onChangeText={setQuestionCount}
            keyboardType="numeric"
            placeholder="15"
            maxLength={3}
          />
        </View>

        {/* Spice Level Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🌶️ Spice Level</Text>
          <Text style={styles.sectionSubtitle}>Choose the intensity of questions</Text>
          
          <View style={styles.spiceLevelContainer}>
            {spiceLevels.map((level) => (
              <TouchableOpacity
                key={level.id}
                style={[
                  styles.spiceLevelButton,
                  { backgroundColor: level.color },
                  spiceLevel === level.id && styles.selectedSpiceLevel
                ]}
                onPress={() => setSpiceLevel(level.id)}
              >
                <Text style={styles.spiceLevelText}>{level.name}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Start Game Button */}
        <TouchableOpacity style={styles.startButton} onPress={startGame}>
          <Text style={styles.startButtonText}>🎮 Start Game</Text>
        </TouchableOpacity>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  scrollView: {
    flex: 1,
    paddingHorizontal: 20,
  },
  section: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1A202C',
    marginBottom: 8,
  },
  sectionSubtitle: {
    fontSize: 14,
    color: '#718096',
    marginBottom: 16,
  },
  playerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  playerInput: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#1A202C',
  },
  removeButton: {
    marginLeft: 12,
    backgroundColor: '#E53E3E',
    borderRadius: 20,
    width: 32,
    height: 32,
    justifyContent: 'center',
    alignItems: 'center',
  },
  removeButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  addButton: {
    backgroundColor: '#3182CE',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  addButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  numberInput: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#1A202C',
    textAlign: 'center',
    maxWidth: 100,
  },
  spiceLevelContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  spiceLevelButton: {
    flex: 1,
    paddingVertical: 16,
    marginHorizontal: 4,
    borderRadius: 8,
    alignItems: 'center',
  },
  selectedSpiceLevel: {
    borderWidth: 3,
    borderColor: '#1A202C',
  },
  spiceLevelText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  startButton: {
    backgroundColor: '#E53E3E',
    borderRadius: 12,
    paddingVertical: 20,
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 40,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  startButtonText: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: 'bold',
  },
});

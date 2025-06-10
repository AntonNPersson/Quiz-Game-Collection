/**
 * Game Screen - Truth or Dare Mobile App
 * 
 * Main gameplay screen where players answer questions.
 * Simplified version with demo questions for testing.
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

const { width } = Dimensions.get('window');

export default function GameScreen({ route, navigation }) {
  const { players, questionCount, spiceLevel } = route.params;
  
  const [currentPlayerIndex, setCurrentPlayerIndex] = useState(0);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [gameFinished, setGameFinished] = useState(false);

  // Demo questions for testing
  const demoQuestions = [
    {
      type: 'truth',
      text: 'What is your biggest fear?',
      spiceLevel: 'mild'
    },
    {
      type: 'dare',
      text: 'Do 10 jumping jacks right now!',
      spiceLevel: 'mild'
    },
    {
      type: 'truth',
      text: 'What is the most embarrassing thing that happened to you?',
      spiceLevel: 'medium'
    },
    {
      type: 'dare',
      text: 'Sing your favorite song for 30 seconds!',
      spiceLevel: 'medium'
    },
    {
      type: 'truth',
      text: 'Who was your first crush?',
      spiceLevel: 'spicy'
    },
    {
      type: 'dare',
      text: 'Call someone and tell them a funny joke!',
      spiceLevel: 'spicy'
    },
  ];

  useEffect(() => {
    loadNextQuestion();
  }, []);

  const loadNextQuestion = () => {
    if (currentQuestionIndex >= questionCount) {
      setGameFinished(true);
      return;
    }

    // Get a random question from demo questions
    const randomQuestion = demoQuestions[Math.floor(Math.random() * demoQuestions.length)];
    setCurrentQuestion(randomQuestion);
  };

  const handleCompleted = () => {
    nextTurn();
  };

  const handleSkipped = () => {
    Alert.alert(
      'Skip Question',
      'Are you sure you want to skip this question?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Skip', onPress: nextTurn },
      ]
    );
  };

  const nextTurn = () => {
    const nextQuestionIndex = currentQuestionIndex + 1;
    const nextPlayerIndex = (currentPlayerIndex + 1) % players.length;
    
    setCurrentQuestionIndex(nextQuestionIndex);
    setCurrentPlayerIndex(nextPlayerIndex);
    
    if (nextQuestionIndex >= questionCount) {
      setGameFinished(true);
    } else {
      loadNextQuestion();
    }
  };

  const endGame = () => {
    Alert.alert(
      'End Game',
      'Are you sure you want to end the game?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'End Game', 
          onPress: () => navigation.navigate('Welcome'),
          style: 'destructive'
        },
      ]
    );
  };

  const restartGame = () => {
    setCurrentPlayerIndex(0);
    setCurrentQuestionIndex(0);
    setGameFinished(false);
    loadNextQuestion();
  };

  if (gameFinished) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.finishedContainer}>
          <Text style={styles.finishedTitle}>🎉 Game Complete! 🎉</Text>
          <Text style={styles.finishedText}>
            Thanks for playing Truth or Dare!
          </Text>
          <Text style={styles.finishedStats}>
            Questions answered: {questionCount}
          </Text>
          <Text style={styles.finishedStats}>
            Players: {players.join(', ')}
          </Text>
          
          <View style={styles.finishedButtons}>
            <TouchableOpacity style={styles.restartButton} onPress={restartGame}>
              <Text style={styles.restartButtonText}>🔄 Play Again</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.homeButton} onPress={() => navigation.navigate('Welcome')}>
              <Text style={styles.homeButtonText}>🏠 Home</Text>
            </TouchableOpacity>
          </View>
        </View>
      </SafeAreaView>
    );
  }

  if (!currentQuestion) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading question...</Text>
        </View>
      </SafeAreaView>
    );
  }

  const currentPlayer = players[currentPlayerIndex];
  const progress = ((currentQuestionIndex + 1) / questionCount) * 100;

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.gameContainer}>
        
        {/* Progress Bar */}
        <View style={styles.progressContainer}>
          <View style={styles.progressBar}>
            <View style={[styles.progressFill, { width: `${progress}%` }]} />
          </View>
          <Text style={styles.progressText}>
            {currentQuestionIndex + 1} / {questionCount}
          </Text>
        </View>

        {/* Current Player */}
        <View style={styles.playerContainer}>
          <Text style={styles.playerLabel}>Current Player</Text>
          <Text style={styles.playerName}>{currentPlayer}</Text>
        </View>

        {/* Question Type */}
        <View style={[
          styles.questionTypeContainer,
          { backgroundColor: currentQuestion.type === 'truth' ? '#3182CE' : '#E53E3E' }
        ]}>
          <Text style={styles.questionType}>
            {currentQuestion.type === 'truth' ? '🤔 TRUTH' : '💪 DARE'}
          </Text>
        </View>

        {/* Question */}
        <View style={styles.questionContainer}>
          <Text style={styles.questionText}>
            {currentQuestion.text}
          </Text>
        </View>

        {/* Action Buttons */}
        <View style={styles.buttonContainer}>
          <TouchableOpacity style={styles.completedButton} onPress={handleCompleted}>
            <Text style={styles.completedButtonText}>✅ Completed</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.skipButton} onPress={handleSkipped}>
            <Text style={styles.skipButtonText}>⏭️ Skip</Text>
          </TouchableOpacity>
        </View>

        {/* End Game Button */}
        <TouchableOpacity style={styles.endGameButton} onPress={endGame}>
          <Text style={styles.endGameButtonText}>End Game</Text>
        </TouchableOpacity>

      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  gameContainer: {
    flex: 1,
    paddingHorizontal: 20,
    paddingVertical: 20,
  },
  progressContainer: {
    marginBottom: 30,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#E2E8F0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#38A169',
  },
  progressText: {
    textAlign: 'center',
    marginTop: 8,
    fontSize: 14,
    color: '#718096',
    fontWeight: 'bold',
  },
  playerContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  playerLabel: {
    fontSize: 16,
    color: '#718096',
    marginBottom: 8,
  },
  playerName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1A202C',
  },
  questionTypeContainer: {
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 30,
  },
  questionType: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  questionContainer: {
    flex: 1,
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 24,
    marginBottom: 30,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  questionText: {
    fontSize: 20,
    color: '#1A202C',
    textAlign: 'center',
    lineHeight: 28,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  completedButton: {
    flex: 1,
    backgroundColor: '#38A169',
    paddingVertical: 16,
    borderRadius: 12,
    marginRight: 10,
    alignItems: 'center',
  },
  completedButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  skipButton: {
    flex: 1,
    backgroundColor: '#D69E2E',
    paddingVertical: 16,
    borderRadius: 12,
    marginLeft: 10,
    alignItems: 'center',
  },
  skipButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  endGameButton: {
    backgroundColor: '#718096',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  endGameButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 18,
    color: '#718096',
  },
  finishedContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  finishedTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1A202C',
    textAlign: 'center',
    marginBottom: 20,
  },
  finishedText: {
    fontSize: 18,
    color: '#4A5568',
    textAlign: 'center',
    marginBottom: 30,
  },
  finishedStats: {
    fontSize: 16,
    color: '#718096',
    textAlign: 'center',
    marginBottom: 10,
  },
  finishedButtons: {
    width: '100%',
    marginTop: 40,
  },
  restartButton: {
    backgroundColor: '#E53E3E',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
  },
  restartButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  homeButton: {
    backgroundColor: '#3182CE',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  homeButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

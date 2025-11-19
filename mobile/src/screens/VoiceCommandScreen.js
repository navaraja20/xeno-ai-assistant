/**
 * Voice Command Screen
 * Voice-activated XENO commands
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import Voice from '@react-native-voice/voice';
import XenoAPI from '../services/XenoAPI';

const VoiceCommandScreen = () => {
  const [isListening, setIsListening] = useState(false);
  const [recognizedText, setRecognizedText] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    Voice.onSpeechStart = onSpeechStart;
    Voice.onSpeechEnd = onSpeechEnd;
    Voice.onSpeechResults = onSpeechResults;
    Voice.onSpeechError = onSpeechError;

    return () => {
      Voice.destroy().then(Voice.removeAllListeners);
    };
  }, []);

  const onSpeechStart = () => {
    setIsListening(true);
    setRecognizedText('');
    setResult('');
  };

  const onSpeechEnd = () => {
    setIsListening(false);
  };

  const onSpeechResults = event => {
    if (event.value && event.value[0]) {
      const text = event.value[0];
      setRecognizedText(text);
      executeCommand(text);
    }
  };

  const onSpeechError = error => {
    console.error('Speech recognition error:', error);
    setIsListening(false);
    Alert.alert('Error', 'Failed to recognize speech');
  };

  const startListening = async () => {
    try {
      await Voice.start('en-US');
    } catch (error) {
      console.error('Failed to start voice recognition:', error);
    }
  };

  const stopListening = async () => {
    try {
      await Voice.stop();
    } catch (error) {
      console.error('Failed to stop voice recognition:', error);
    }
  };

  const executeCommand = async command => {
    setLoading(true);
    try {
      const response = await XenoAPI.executeVoiceCommand(command);
      setResult(response.result || 'Command executed');
    } catch (error) {
      setResult(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const quickCommands = [
    {label: 'Check emails', command: 'check my emails'},
    {label: 'Today\'s schedule', command: "what's my schedule today"},
    {label: 'GitHub updates', command: 'check github updates'},
    {label: 'New jobs', command: 'find new jobs'},
    {label: 'Set reminder', command: 'remind me to'},
    {label: 'Send email', command: 'send email to'},
  ];

  return (
    <ScrollView style={styles.container}>
      {/* Voice Button */}
      <View style={styles.voiceContainer}>
        <TouchableOpacity
          style={[styles.voiceButton, isListening && styles.listeningButton]}
          onPress={isListening ? stopListening : startListening}>
          <Icon
            name={isListening ? 'mic' : 'mic-none'}
            size={64}
            color="white"
          />
        </TouchableOpacity>
        <Text style={styles.statusText}>
          {isListening ? 'Listening...' : 'Tap to speak'}
        </Text>
      </View>

      {/* Recognized Text */}
      {recognizedText ? (
        <View style={styles.resultCard}>
          <Text style={styles.resultLabel}>You said:</Text>
          <Text style={styles.resultText}>{recognizedText}</Text>
        </View>
      ) : null}

      {/* Command Result */}
      {loading ? (
        <View style={styles.loadingCard}>
          <ActivityIndicator size="small" color="#1a73e8" />
          <Text style={styles.loadingText}>Processing command...</Text>
        </View>
      ) : result ? (
        <View style={styles.resultCard}>
          <Text style={styles.resultLabel}>Result:</Text>
          <Text style={styles.resultText}>{result}</Text>
        </View>
      ) : null}

      {/* Quick Commands */}
      <View style={styles.quickCommandsSection}>
        <Text style={styles.sectionTitle}>Quick Commands</Text>
        <View style={styles.commandsGrid}>
          {quickCommands.map((cmd, index) => (
            <TouchableOpacity
              key={index}
              style={styles.commandButton}
              onPress={() => executeCommand(cmd.command)}>
              <Text style={styles.commandText}>{cmd.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Command Examples */}
      <View style={styles.examplesSection}>
        <Text style={styles.sectionTitle}>Command Examples</Text>
        <Text style={styles.exampleText}>• "Check my emails"</Text>
        <Text style={styles.exampleText}>• "What's my schedule today?"</Text>
        <Text style={styles.exampleText}>• "Schedule a meeting"</Text>
        <Text style={styles.exampleText}>• "Check GitHub updates"</Text>
        <Text style={styles.exampleText}>• "Find new jobs in [location]"</Text>
        <Text style={styles.exampleText}>• "Send email to [contact]"</Text>
        <Text style={styles.exampleText}>• "Remind me to [task]"</Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  voiceContainer: {
    alignItems: 'center',
    paddingVertical: 40,
    backgroundColor: 'white',
    marginBottom: 10,
  },
  voiceButton: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#1a73e8',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  listeningButton: {
    backgroundColor: '#ea4335',
  },
  statusText: {
    marginTop: 20,
    fontSize: 16,
    color: '#5f6368',
    fontWeight: '500',
  },
  resultCard: {
    backgroundColor: 'white',
    padding: 20,
    marginBottom: 10,
  },
  resultLabel: {
    fontSize: 14,
    color: '#5f6368',
    marginBottom: 8,
  },
  resultText: {
    fontSize: 16,
    color: '#202124',
  },
  loadingCard: {
    backgroundColor: 'white',
    padding: 20,
    marginBottom: 10,
    flexDirection: 'row',
    alignItems: 'center',
  },
  loadingText: {
    marginLeft: 10,
    fontSize: 14,
    color: '#5f6368',
  },
  quickCommandsSection: {
    backgroundColor: 'white',
    padding: 15,
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#202124',
    marginBottom: 15,
  },
  commandsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  commandButton: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    padding: 15,
    marginBottom: 10,
    alignItems: 'center',
  },
  commandText: {
    fontSize: 13,
    color: '#202124',
    fontWeight: '500',
  },
  examplesSection: {
    backgroundColor: 'white',
    padding: 20,
    marginBottom: 20,
  },
  exampleText: {
    fontSize: 13,
    color: '#5f6368',
    marginBottom: 8,
    paddingLeft: 5,
  },
});

export default VoiceCommandScreen;

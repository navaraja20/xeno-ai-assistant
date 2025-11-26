/**
 * Settings Screen
 * Configure XENO mobile app settings
 */

import React, {useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Switch,
  TouchableOpacity,
  Alert,
  TextInput,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import XENOAPI from '../services/XENOAPI';

const SettingsScreen = () => {
  const [pushEnabled, setPushEnabled] = useState(true);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [autoSync, setAutoSync] = useState(true);
  const [serverUrl, setServerUrl] = useState('http://localhost:5000');

  const handleSaveServer = async () => {
    try {
      await AsyncStorage.setItem('server_url', serverUrl);
      Alert.alert('Success', 'Server URL saved');
    } catch (error) {
      Alert.alert('Error', 'Failed to save server URL');
    }
  };

  const handleLogout = async () => {
    Alert.alert('Logout', 'Are you sure you want to logout?', [
      {text: 'Cancel', style: 'cancel'},
      {
        text: 'Logout',
        style: 'destructive',
        onPress: async () => {
          await XENOAPI.logout();
          // Navigation reset would happen here
          Alert.alert('Success', 'Logged out successfully');
        },
      },
    ]);
  };

  const handleClearCache = async () => {
    Alert.alert('Clear Cache', 'Are you sure?', [
      {text: 'Cancel', style: 'cancel'},
      {
        text: 'Clear',
        style: 'destructive',
        onPress: async () => {
          // Clear cache logic here
          Alert.alert('Success', 'Cache cleared');
        },
      },
    ]);
  };

  return (
    <ScrollView style={styles.container}>
      {/* Notifications Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Notifications</Text>
        <View style={styles.settingRow}>
          <View style={styles.settingInfo}>
            <Icon name="notifications" size={24} color="#5f6368" />
            <Text style={styles.settingLabel}>Push Notifications</Text>
          </View>
          <Switch
            value={pushEnabled}
            onValueChange={setPushEnabled}
            trackColor={{false: '#dadce0', true: '#8ab4f8'}}
            thumbColor={pushEnabled ? '#1a73e8' : '#f4f3f4'}
          />
        </View>
      </View>

      {/* Voice Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Voice</Text>
        <View style={styles.settingRow}>
          <View style={styles.settingInfo}>
            <Icon name="mic" size={24} color="#5f6368" />
            <Text style={styles.settingLabel}>Voice Commands</Text>
          </View>
          <Switch
            value={voiceEnabled}
            onValueChange={setVoiceEnabled}
            trackColor={{false: '#dadce0', true: '#8ab4f8'}}
            thumbColor={voiceEnabled ? '#1a73e8' : '#f4f3f4'}
          />
        </View>
      </View>

      {/* Sync Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Synchronization</Text>
        <View style={styles.settingRow}>
          <View style={styles.settingInfo}>
            <Icon name="sync" size={24} color="#5f6368" />
            <Text style={styles.settingLabel}>Auto Sync</Text>
          </View>
          <Switch
            value={autoSync}
            onValueChange={setAutoSync}
            trackColor={{false: '#dadce0', true: '#8ab4f8'}}
            thumbColor={autoSync ? '#1a73e8' : '#f4f3f4'}
          />
        </View>
      </View>

      {/* Server Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Server</Text>
        <View style={styles.settingRow}>
          <View style={styles.settingInfo}>
            <Icon name="dns" size={24} color="#5f6368" />
            <View style={styles.inputContainer}>
              <Text style={styles.settingLabel}>Server URL</Text>
              <TextInput
                style={styles.input}
                value={serverUrl}
                onChangeText={setServerUrl}
                placeholder="http://localhost:5000"
                autoCapitalize="none"
              />
            </View>
          </View>
        </View>
        <TouchableOpacity
          style={styles.saveButton}
          onPress={handleSaveServer}>
          <Text style={styles.saveButtonText}>Save Server URL</Text>
        </TouchableOpacity>
      </View>

      {/* Data Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Data</Text>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={handleClearCache}>
          <Icon name="delete-outline" size={24} color="#ea4335" />
          <Text style={[styles.settingLabel, {color: '#ea4335'}]}>
            Clear Cache
          </Text>
        </TouchableOpacity>
      </View>

      {/* Account Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account</Text>
        <TouchableOpacity style={styles.actionButton} onPress={handleLogout}>
          <Icon name="logout" size={24} color="#ea4335" />
          <Text style={[styles.settingLabel, {color: '#ea4335'}]}>
            Logout
          </Text>
        </TouchableOpacity>
      </View>

      {/* About Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        <View style={styles.aboutRow}>
          <Text style={styles.aboutLabel}>Version</Text>
          <Text style={styles.aboutValue}>1.0.0</Text>
        </View>
        <View style={styles.aboutRow}>
          <Text style={styles.aboutLabel}>Build</Text>
          <Text style={styles.aboutValue}>100</Text>
        </View>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>XENO AI Personal Assistant</Text>
        <Text style={styles.footerSubtext}>© 2024 All rights reserved</Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  section: {
    backgroundColor: 'white',
    marginBottom: 10,
    padding: 15,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#202124',
    marginBottom: 15,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
  },
  settingInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingLabel: {
    fontSize: 15,
    color: '#202124',
    marginLeft: 15,
  },
  inputContainer: {
    flex: 1,
    marginLeft: 15,
  },
  input: {
    borderWidth: 1,
    borderColor: '#dadce0',
    borderRadius: 4,
    padding: 8,
    marginTop: 5,
    fontSize: 13,
  },
  saveButton: {
    backgroundColor: '#1a73e8',
    padding: 12,
    borderRadius: 6,
    alignItems: 'center',
    marginTop: 10,
  },
  saveButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 14,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
  },
  aboutRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
  },
  aboutLabel: {
    fontSize: 14,
    color: '#5f6368',
  },
  aboutValue: {
    fontSize: 14,
    color: '#202124',
    fontWeight: '500',
  },
  footer: {
    padding: 30,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 14,
    color: '#5f6368',
    fontWeight: '500',
  },
  footerSubtext: {
    fontSize: 12,
    color: '#9aa0a6',
    marginTop: 5,
  },
});

export default SettingsScreen;

/**
 * Quick Actions Screen
 * Fast access to common XENO tasks
 */

import React, {useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import XenoAPI from '../services/XenoAPI';

const QuickActionsScreen = () => {
  const [loading, setLoading] = useState(false);

  const handleEmailQuickSend = () => {
    Alert.prompt(
      'Quick Email',
      'Enter recipient email:',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Next',
          onPress: recipient => {
            Alert.prompt(
              'Quick Email',
              'Enter subject:',
              [
                {text: 'Cancel', style: 'cancel'},
                {
                  text: 'Send',
                  onPress: async subject => {
                    try {
                      setLoading(true);
                      await XenoAPI.sendEmail(recipient, subject, '');
                      Alert.alert('Success', 'Email sent!');
                    } catch (error) {
                      Alert.alert('Error', error.message);
                    } finally {
                      setLoading(false);
                    }
                  },
                },
              ],
              'plain-text',
            );
          },
        },
      ],
      'plain-text',
    );
  };

  const handleCalendarQuickEvent = () => {
    Alert.prompt(
      'Quick Event',
      'Enter event title:',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Create',
          onPress: async title => {
            try {
              setLoading(true);
              const now = new Date();
              const later = new Date(now.getTime() + 60 * 60 * 1000); // 1 hour later
              
              await XenoAPI.createCalendarEvent({
                summary: title,
                start_time: now.toISOString(),
                end_time: later.toISOString(),
              });
              Alert.alert('Success', 'Event created!');
            } catch (error) {
              Alert.alert('Error', error.message);
            } finally {
              setLoading(false);
            }
          },
        },
      ],
      'plain-text',
    );
  };

  const handleJobSearch = () => {
    Alert.prompt(
      'Job Search',
      'Enter job keywords:',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Search',
          onPress: async keywords => {
            try {
              setLoading(true);
              const jobs = await XenoAPI.getJobs(keywords);
              Alert.alert(
                'Jobs Found',
                `Found ${jobs.length} jobs matching "${keywords}"`,
              );
            } catch (error) {
              Alert.alert('Error', error.message);
            } finally {
              setLoading(false);
            }
          },
        },
      ],
      'plain-text',
    );
  };

  const actions = [
    {
      title: 'Quick Email',
      icon: 'email',
      color: '#ea4335',
      onPress: handleEmailQuickSend,
    },
    {
      title: 'Add Event',
      icon: 'event',
      color: '#34a853',
      onPress: handleCalendarQuickEvent,
    },
    {
      title: 'Search Jobs',
      icon: 'work',
      color: '#fbbc04',
      onPress: handleJobSearch,
    },
    {
      title: 'Check GitHub',
      icon: 'code',
      color: '#5f6368',
      onPress: async () => {
        try {
          setLoading(true);
          const stats = await XenoAPI.getGitHubStats();
          Alert.alert('GitHub Stats', JSON.stringify(stats, null, 2));
        } catch (error) {
          Alert.alert('Error', error.message);
        } finally {
          setLoading(false);
        }
      },
    },
    {
      title: 'View Timeline',
      icon: 'timeline',
      color: '#1a73e8',
      onPress: async () => {
        try {
          setLoading(true);
          const timeline = await XenoAPI.getTimeline(5);
          Alert.alert(
            'Recent Activity',
            timeline.map(a => `• ${a.title}`).join('\n'),
          );
        } catch (error) {
          Alert.alert('Error', error.message);
        } finally {
          setLoading(false);
        }
      },
    },
    {
      title: 'AI Chat',
      icon: 'chat',
      color: '#9334e6',
      onPress: () => {
        Alert.prompt(
          'AI Chat',
          'Ask me anything:',
          [
            {text: 'Cancel', style: 'cancel'},
            {
              text: 'Send',
              onPress: async message => {
                try {
                  setLoading(true);
                  const response = await XenoAPI.sendMessage(message);
                  Alert.alert('AI Response', response.response);
                } catch (error) {
                  Alert.alert('Error', error.message);
                } finally {
                  setLoading(false);
                }
              },
            },
          ],
          'plain-text',
        );
      },
    },
  ];

  return (
    <View style={styles.container}>
      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#1a73e8" />
        </View>
      )}
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Quick Actions</Text>
          <Text style={styles.headerSubtitle}>
            Fast access to common tasks
          </Text>
        </View>

        <View style={styles.actionsContainer}>
          {actions.map((action, index) => (
            <TouchableOpacity
              key={index}
              style={styles.actionCard}
              onPress={action.onPress}>
              <View
                style={[
                  styles.actionIcon,
                  {backgroundColor: action.color},
                ]}>
                <Icon name={action.icon} size={32} color="white" />
              </View>
              <Text style={styles.actionTitle}>{action.title}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 999,
  },
  header: {
    backgroundColor: 'white',
    padding: 20,
    marginBottom: 10,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#202124',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#5f6368',
    marginTop: 5,
  },
  actionsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 10,
  },
  actionCard: {
    width: '48%',
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    margin: '1%',
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 1},
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  actionIcon: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  actionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#202124',
    textAlign: 'center',
  },
});

export default QuickActionsScreen;

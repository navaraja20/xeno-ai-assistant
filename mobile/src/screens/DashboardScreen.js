/**
 * Dashboard Screen
 * Main screen showing overview of XENO activity
 */

import React, {useEffect, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import XenoAPI from '../services/XenoAPI';

const DashboardScreen = ({navigation}) => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [dashboard, setDashboard] = useState(null);
  const [timeline, setTimeline] = useState([]);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [dashboardData, timelineData] = await Promise.all([
        XenoAPI.getDashboard(),
        XenoAPI.getTimeline(10),
      ]);
      setDashboard(dashboardData);
      setTimeline(timelineData);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboard();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#1a73e8" />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }>
      {/* Quick Stats */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Icon name="email" size={30} color="#1a73e8" />
          <Text style={styles.statNumber}>
            {dashboard?.unread_emails || 0}
          </Text>
          <Text style={styles.statLabel}>Unread Emails</Text>
        </View>
        <View style={styles.statCard}>
          <Icon name="notifications" size={30} color="#ea4335" />
          <Text style={styles.statNumber}>
            {dashboard?.notifications || 0}
          </Text>
          <Text style={styles.statLabel}>Notifications</Text>
        </View>
        <View style={styles.statCard}>
          <Icon name="event" size={30} color="#34a853" />
          <Text style={styles.statNumber}>
            {dashboard?.upcoming_events || 0}
          </Text>
          <Text style={styles.statLabel}>Events Today</Text>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionsGrid}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('VoiceCommand')}>
            <Icon name="mic" size={30} color="#1a73e8" />
            <Text style={styles.actionText}>Voice Command</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('Notifications')}>
            <Icon name="notifications" size={30} color="#1a73e8" />
            <Text style={styles.actionText}>Notifications</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('QuickActions')}>
            <Icon name="bolt" size={30} color="#1a73e8" />
            <Text style={styles.actionText}>Quick Actions</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('Settings')}>
            <Icon name="settings" size={30} color="#1a73e8" />
            <Text style={styles.actionText}>Settings</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Recent Activity Timeline */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Activity</Text>
        {timeline.map((activity, index) => (
          <View key={index} style={styles.timelineItem}>
            <View style={styles.timelineDot} />
            <View style={styles.timelineContent}>
              <Text style={styles.timelineTitle}>{activity.title}</Text>
              <Text style={styles.timelineDescription}>
                {activity.description}
              </Text>
              <Text style={styles.timelineTime}>{activity.timestamp}</Text>
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 15,
    backgroundColor: 'white',
    marginBottom: 10,
  },
  statCard: {
    alignItems: 'center',
    padding: 10,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#202124',
    marginTop: 5,
  },
  statLabel: {
    fontSize: 12,
    color: '#5f6368',
    marginTop: 2,
  },
  section: {
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
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionButton: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    padding: 20,
    alignItems: 'center',
    marginBottom: 10,
  },
  actionText: {
    marginTop: 8,
    fontSize: 13,
    color: '#202124',
    fontWeight: '500',
  },
  timelineItem: {
    flexDirection: 'row',
    marginBottom: 15,
  },
  timelineDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#1a73e8',
    marginTop: 5,
    marginRight: 10,
  },
  timelineContent: {
    flex: 1,
  },
  timelineTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#202124',
  },
  timelineDescription: {
    fontSize: 13,
    color: '#5f6368',
    marginTop: 2,
  },
  timelineTime: {
    fontSize: 11,
    color: '#9aa0a6',
    marginTop: 2,
  },
});

export default DashboardScreen;

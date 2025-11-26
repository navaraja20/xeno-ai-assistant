/**
 * Notifications Screen
 * Display and manage XENO notifications
 */

import React, {useEffect, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import XENOAPI from '../services/XENOAPI';

const NotificationsScreen = () => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [filter, setFilter] = useState('all'); // 'all' or 'unread'

  useEffect(() => {
    loadNotifications();
  }, [filter]);

  const loadNotifications = async () => {
    try {
      const data = await XENOAPI.getNotifications(filter === 'unread');
      setNotifications(data);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadNotifications();
  };

  const markAsRead = async notificationId => {
    try {
      await XENOAPI.markNotificationRead(notificationId);
      loadNotifications();
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  const getIcon = type => {
    switch (type) {
      case 'email':
        return 'email';
      case 'calendar':
        return 'event';
      case 'github':
        return 'code';
      case 'job':
        return 'work';
      default:
        return 'notifications';
    }
  };

  const getColor = type => {
    switch (type) {
      case 'email':
        return '#ea4335';
      case 'calendar':
        return '#34a853';
      case 'github':
        return '#5f6368';
      case 'job':
        return '#fbbc04';
      default:
        return '#1a73e8';
    }
  };

  const renderNotification = ({item}) => (
    <TouchableOpacity
      style={[styles.notificationCard, !item.read && styles.unreadCard]}
      onPress={() => !item.read && markAsRead(item.id)}>
      <View style={[styles.iconContainer, {backgroundColor: getColor(item.type)}]}>
        <Icon name={getIcon(item.type)} size={24} color="white" />
      </View>
      <View style={styles.notificationContent}>
        <Text style={styles.notificationTitle}>{item.title}</Text>
        <Text style={styles.notificationMessage}>{item.message}</Text>
        <Text style={styles.notificationTime}>{item.timestamp}</Text>
      </View>
      {!item.read && <View style={styles.unreadDot} />}
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#1a73e8" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Filter Tabs */}
      <View style={styles.filterContainer}>
        <TouchableOpacity
          style={[styles.filterTab, filter === 'all' && styles.activeTab]}
          onPress={() => setFilter('all')}>
          <Text
            style={[
              styles.filterText,
              filter === 'all' && styles.activeText,
            ]}>
            All
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.filterTab, filter === 'unread' && styles.activeTab]}
          onPress={() => setFilter('unread')}>
          <Text
            style={[
              styles.filterText,
              filter === 'unread' && styles.activeText,
            ]}>
            Unread
          </Text>
        </TouchableOpacity>
      </View>

      {/* Notifications List */}
      <FlatList
        data={notifications}
        renderItem={renderNotification}
        keyExtractor={item => item.id.toString()}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Icon name="notifications-none" size={64} color="#dadce0" />
            <Text style={styles.emptyText}>No notifications</Text>
          </View>
        }
      />
    </View>
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
  filterContainer: {
    flexDirection: 'row',
    backgroundColor: 'white',
    padding: 5,
    marginBottom: 1,
  },
  filterTab: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 8,
  },
  activeTab: {
    backgroundColor: '#e8f0fe',
  },
  filterText: {
    fontSize: 14,
    color: '#5f6368',
    fontWeight: '500',
  },
  activeText: {
    color: '#1a73e8',
    fontWeight: 'bold',
  },
  notificationCard: {
    flexDirection: 'row',
    backgroundColor: 'white',
    padding: 15,
    marginBottom: 1,
    alignItems: 'center',
  },
  unreadCard: {
    backgroundColor: '#f8f9fa',
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  notificationContent: {
    flex: 1,
  },
  notificationTitle: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#202124',
    marginBottom: 4,
  },
  notificationMessage: {
    fontSize: 13,
    color: '#5f6368',
    marginBottom: 4,
  },
  notificationTime: {
    fontSize: 11,
    color: '#9aa0a6',
  },
  unreadDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#1a73e8',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 100,
  },
  emptyText: {
    fontSize: 16,
    color: '#9aa0a6',
    marginTop: 10,
  },
});

export default NotificationsScreen;

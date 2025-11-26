/**
 * Notification Service
 * Handles push notifications setup and management
 */

import messaging from '@react-native-firebase/messaging';
import PushNotification from 'react-native-push-notification';
import XENOAPI from './XENOAPI';

export const setupNotifications = async () => {
  // Configure local notifications
  PushNotification.configure({
    onRegister: async function (token) {
      console.log('FCM Token:', token.token);
      // Register token with backend
      try {
        await XENOAPI.registerPushToken(token.token);
      } catch (error) {
        console.error('Failed to register push token:', error);
      }
    },

    onNotification: function (notification) {
      console.log('NOTIFICATION:', notification);
      notification.finish();
    },

    permissions: {
      alert: true,
      badge: true,
      sound: true,
    },
    popInitialNotification: true,
    requestPermissions: true,
  });

  // Create notification channel for Android
  PushNotification.createChannel(
    {
      channelId: 'XENO-default',
      channelName: 'XENO Notifications',
      channelDescription: 'Default notification channel for XENO',
      playSound: true,
      soundName: 'default',
      importance: 4,
      vibrate: true,
    },
    created => console.log(`Channel created: ${created}`),
  );

  // Handle background messages
  messaging().setBackgroundMessageHandler(async remoteMessage => {
    console.log('Background notification:', remoteMessage);
    showLocalNotification(remoteMessage);
  });
};

export const showLocalNotification = message => {
  PushNotification.localNotification({
    channelId: 'XENO-default',
    title: message.notification?.title || 'XENO',
    message: message.notification?.body || 'New notification',
    playSound: true,
    soundName: 'default',
    importance: 'high',
    vibrate: true,
    vibration: 300,
  });
};

export const scheduleNotification = (title, message, date) => {
  PushNotification.localNotificationSchedule({
    channelId: 'XENO-default',
    title,
    message,
    date,
    allowWhileIdle: true,
  });
};

export const cancelAllNotifications = () => {
  PushNotification.cancelAllLocalNotifications();
};

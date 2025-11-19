/**
 * XENO Mobile App
 * Main application component
 */

import React, {useEffect} from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createStackNavigator} from '@react-navigation/stack';
import {StatusBar, StyleSheet} from 'react-native';
import messaging from '@react-native-firebase/messaging';

// Screens
import DashboardScreen from './src/screens/DashboardScreen';
import NotificationsScreen from './src/screens/NotificationsScreen';
import VoiceCommandScreen from './src/screens/VoiceCommandScreen';
import QuickActionsScreen from './src/screens/QuickActionsScreen';
import SettingsScreen from './src/screens/SettingsScreen';

// Services
import {setupNotifications} from './src/services/NotificationService';

const Stack = createStackNavigator();

const App = () => {
  useEffect(() => {
    // Request notification permission
    const requestPermission = async () => {
      const authStatus = await messaging().requestPermission();
      const enabled =
        authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
        authStatus === messaging.AuthorizationStatus.PROVISIONAL;

      if (enabled) {
        console.log('Authorization status:', authStatus);
        setupNotifications();
      }
    };

    requestPermission();

    // Handle foreground messages
    const unsubscribe = messaging().onMessage(async remoteMessage => {
      console.log('Foreground notification:', remoteMessage);
    });

    return unsubscribe;
  }, []);

  return (
    <>
      <StatusBar barStyle="dark-content" backgroundColor="#1a73e8" />
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName="Dashboard"
          screenOptions={{
            headerStyle: {
              backgroundColor: '#1a73e8',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          }}>
          <Stack.Screen
            name="Dashboard"
            component={DashboardScreen}
            options={{title: 'XENO Assistant'}}
          />
          <Stack.Screen
            name="Notifications"
            component={NotificationsScreen}
            options={{title: 'Notifications'}}
          />
          <Stack.Screen
            name="VoiceCommand"
            component={VoiceCommandScreen}
            options={{title: 'Voice Commands'}}
          />
          <Stack.Screen
            name="QuickActions"
            component={QuickActionsScreen}
            options={{title: 'Quick Actions'}}
          />
          <Stack.Screen
            name="Settings"
            component={SettingsScreen}
            options={{title: 'Settings'}}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});

export default App;

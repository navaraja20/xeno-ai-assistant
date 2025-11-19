# XENO Mobile Companion App

React Native mobile application for XENO AI Personal Assistant.

## Features

### 📱 Core Functionality
- **Dashboard**: Overview of emails, notifications, and calendar events
- **Notifications**: Real-time push notifications with Firebase Cloud Messaging
- **Voice Commands**: Voice-activated commands with speech recognition
- **Quick Actions**: Fast access to common tasks
- **Settings**: Configure app preferences and server connection

### 🎯 Quick Actions
- Send quick emails
- Add calendar events
- Search for jobs
- Check GitHub stats
- View activity timeline
- AI chat conversations

### 🎤 Voice Commands
Supported voice commands:
- "Check my emails"
- "What's my schedule today?"
- "Schedule a meeting"
- "Check GitHub updates"
- "Find new jobs in [location]"
- "Send email to [contact]"
- "Remind me to [task]"

## Setup Instructions

### Prerequisites
- Node.js (v16 or higher)
- React Native CLI
- Android Studio (for Android) or Xcode (for iOS)
- XENO desktop application running

### Installation

1. Navigate to mobile directory:
```bash
cd mobile
```

2. Install dependencies:
```bash
npm install
```

3. Install iOS dependencies (macOS only):
```bash
cd ios && pod install && cd ..
```

### Configuration

1. **Update Server URL**:
   - Open `src/services/XenoAPI.js`
   - Change `API_BASE_URL` to your XENO server IP
   - Example: `http://192.168.1.100:5000/api`

2. **Firebase Setup** (for push notifications):
   - Create a Firebase project
   - Add Android/iOS apps in Firebase console
   - Download `google-services.json` (Android) and `GoogleService-Info.plist` (iOS)
   - Place files in respective directories

3. **Android Configuration**:
   - Place `google-services.json` in `android/app/`
   - Update `android/app/build.gradle` if needed

4. **iOS Configuration**:
   - Place `GoogleService-Info.plist` in `ios/XenoMobile/`
   - Update push notification capabilities in Xcode

### Running the App

#### Android
```bash
npm run android
```

#### iOS (macOS only)
```bash
npm run ios
```

#### Development Server
```bash
npm start
```

## Project Structure

```
mobile/
├── src/
│   ├── screens/           # App screens
│   │   ├── DashboardScreen.js
│   │   ├── NotificationsScreen.js
│   │   ├── VoiceCommandScreen.js
│   │   ├── QuickActionsScreen.js
│   │   └── SettingsScreen.js
│   ├── services/          # API and services
│   │   ├── XenoAPI.js
│   │   └── NotificationService.js
│   ├── components/        # Reusable components
│   └── utils/            # Utility functions
├── App.js                # Main app component
├── index.js              # Entry point
└── package.json          # Dependencies
```

## API Integration

The mobile app communicates with the XENO backend via REST API.

### Authentication
Login to get JWT token:
```javascript
const response = await XenoAPI.login(email, password);
```

### Dashboard Data
```javascript
const dashboard = await XenoAPI.getDashboard();
```

### Send Email
```javascript
await XenoAPI.sendEmail(to, subject, body);
```

### Calendar Events
```javascript
const events = await XenoAPI.getCalendarEvents(7);
```

### Voice Commands
```javascript
const result = await XenoAPI.executeVoiceCommand(command);
```

## Push Notifications

### Setup
1. Firebase Cloud Messaging is configured in `App.js`
2. Token is automatically registered with backend
3. Notifications handled by `NotificationService.js`

### Testing Notifications
Send a test notification from Firebase Console or backend API.

## Troubleshooting

### Cannot Connect to Server
- Ensure XENO desktop app and API server are running
- Check firewall settings
- Verify server URL in settings
- Use your computer's local IP, not `localhost`

### Voice Recognition Not Working
- Grant microphone permissions
- Check device settings
- Ensure `react-native-voice` is properly installed

### Push Notifications Not Received
- Verify Firebase configuration
- Check notification permissions
- Ensure token is registered with backend

## Building for Production

### Android APK
```bash
cd android
./gradlew assembleRelease
```

APK will be in `android/app/build/outputs/apk/release/`

### iOS IPA
1. Open `ios/XenoMobile.xcworkspace` in Xcode
2. Select "Any iOS Device"
3. Product → Archive
4. Distribute App

## Features Roadmap

- [ ] Biometric authentication (Face ID / Fingerprint)
- [ ] Offline mode with local storage
- [ ] Widget support for quick stats
- [ ] Dark mode theme
- [ ] Multi-account support
- [ ] File attachments for emails
- [ ] Calendar conflict detection
- [ ] Job application tracking

## Dependencies

### Core
- `react-native`: ^0.72.6
- `react-navigation`: Navigation system
- `axios`: HTTP client

### Features
- `@react-native-firebase/messaging`: Push notifications
- `react-native-voice`: Voice recognition
- `react-native-push-notification`: Local notifications
- `@react-native-async-storage/async-storage`: Local storage
- `react-native-vector-icons`: Icons

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API server logs
3. Check XENO desktop app console

## License

Part of XENO AI Personal Assistant project.

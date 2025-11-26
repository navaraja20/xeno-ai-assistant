# XENO Browser Extension 🌐

A powerful Chrome/Edge browser extension that extends XENO's personal assistant capabilities directly into your browser workflow.

## Features ✨

### 🚀 Quick Actions
- **Quick Email**: Compose and send emails from any webpage
- **Quick Calendar**: Create calendar events instantly
- **Quick Task**: Add tasks on the go
- **Voice Commands**: Use voice to control XENO from your browser

### 💼 LinkedIn Integration
- **One-Click Apply**: Auto-fill job applications with stored profile data
- **Profile Scraper**: Save LinkedIn profiles to XENO
- **Connection Automation**: Send personalized connection requests
- **Job Tracking**: Automatically create follow-up tasks for applications

### 💻 GitHub Integration
- **Repository Quick Actions**: Star, watch, and analyze repos with one click
- **Quick Info Copy**: Copy formatted repository information
- **Save to XENO**: Archive interesting repositories
- **AI Analysis**: Get AI-powered insights on codebases

### 📧 Gmail Enhancements
- **AI Email Assistant**: Rewrite emails to be professional, friendly, concise, or expanded
- **Quick Reply Templates**: Pre-written responses for common scenarios
- **Priority Indicators**: ML-powered email importance predictions
- **Email to Task/Event**: Convert emails to calendar events or tasks

### 🔄 Real-Time Sync
- WebSocket connection to XENO desktop app
- Bidirectional communication
- Activity synchronization
- Live notifications

## Installation 📦

### Prerequisites
- Chrome or Edge browser (Manifest V3 compatible)
- XENO Desktop Application running
- Python 3.9+ (for WebSocket server)

### Step 1: Install Dependencies
```bash
pip install websockets
```

### Step 2: Start WebSocket Server
```bash
python src/websocket_server.py
```

The server will start on `ws://localhost:8765` by default.

### Step 3: Load Extension in Browser

**Chrome:**
1. Open `chrome://extensions/`
2. Enable "Developer mode" (top-right toggle)
3. Click "Load unpacked"
4. Select the `browser-extension` folder
5. Extension will appear in toolbar

**Edge:**
1. Open `edge://extensions/`
2. Enable "Developer mode" (left sidebar)
3. Click "Load unpacked"
4. Select the `browser-extension` folder
5. Extension will appear in toolbar

### Step 4: Configure Settings
1. Click XENO extension icon
2. Click "Settings" at bottom
3. Verify WebSocket URL: `ws://localhost:8765`
4. Enter your personal information for auto-fill
5. Click "Test Connection" to verify
6. Save settings

## Usage 🎯

### Keyboard Shortcuts
- `Ctrl+Shift+E` - Quick Email
- `Ctrl+Shift+C` - Quick Calendar
- `Ctrl+Shift+X` - Open XENO Dashboard

### Context Menu
Right-click on any webpage for XENO actions:
- Send Quick Email
- Create Calendar Event
- Create Task
- Save to XENO

### LinkedIn Quick Apply
1. Navigate to LinkedIn job posting
2. Look for "⚡ XENO Quick Apply" button on job cards
3. Click to auto-fill application
4. Review pre-filled data and submit

### GitHub Repository Actions
1. Visit any GitHub repository
2. Click the floating XENO panel (bottom-right)
3. Choose action:
   - 💾 Save to XENO
   - ✅ Create Task
   - 📋 Copy Info
   - 🔍 Analyze Repo

### Gmail AI Assistant
1. Open Gmail compose window
2. Write your email draft
3. Click "⚡ XENO AI" button in toolbar
4. Choose enhancement:
   - Make it professional
   - Make it friendly
   - Make it concise
   - Expand details
   - Fix grammar

## Architecture 🏗️

```
browser-extension/
├── manifest.json              # Extension configuration (Manifest V3)
├── popup/
│   ├── popup.html            # Main popup interface
│   ├── popup.css             # Dark theme styling
│   └── popup.js              # Popup logic & WebSocket client
├── background/
│   └── service-worker.js     # Background processes & message routing
├── content/
│   ├── linkedin-quick-apply.js   # LinkedIn automation
│   ├── github-quick-view.js      # GitHub enhancements
│   └── gmail-integration.js      # Gmail AI features
├── options/
│   ├── options.html          # Settings page
│   └── options.js            # Settings management
└── icons/
    ├── icon16.png
    ├── icon32.png
    ├── icon48.png
    └── icon128.png
```

## WebSocket Protocol 📡

### Message Types

**From Browser to Desktop:**
```javascript
{
  type: 'send_email',
  data: { to, subject, body }
}

{
  type: 'create_calendar_event',
  data: { title, startTime, endTime, description }
}

{
  type: 'create_task',
  data: { title, notes, priority }
}
```

**From Desktop to Browser:**
```javascript
{
  type: 'activity_update',
  timestamp: '2024-01-15T10:30:00'
}

{
  type: 'notification',
  title: 'XENO',
  body: 'Task completed'
}
```

## Configuration ⚙️

### Settings Storage
- **Sync Storage**: User preferences, server URL, user data (synced across devices)
- **Local Storage**: Activity history, statistics (device-specific)

### Default Settings
```javascript
{
  serverUrl: 'ws://localhost:8765',
  userData: {
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    linkedInUrl: ''
  },
  features: {
    enableQuickApply: true,
    enableGitHub: true,
    enableGmail: true,
    enableAiAssist: true,
    enablePriority: true
  }
}
```

## Permissions 🔒

The extension requires the following permissions:

- **storage**: Save settings and activity
- **tabs**: Detect current website for context actions
- **activeTab**: Access current page content
- **notifications**: Show desktop notifications
- **contextMenus**: Add right-click menu items

**Host Permissions:**
- `mail.google.com` - Gmail integration
- `linkedin.com` - LinkedIn automation
- `github.com` - GitHub enhancements
- `calendar.google.com` - Calendar access

All permissions are used exclusively for stated features. No data is collected or transmitted to third parties.

## Privacy & Security 🔐

- ✅ All data stored locally
- ✅ WebSocket connection only to localhost
- ✅ No analytics or tracking
- ✅ No third-party API calls (except Google services you use)
- ✅ Open source - audit the code yourself
- ✅ Manifest V3 compliant (latest security standards)

## Troubleshooting 🔧

### Extension Not Connecting
1. Check WebSocket server is running: `python src/websocket_server.py`
2. Verify URL in settings: `ws://localhost:8765`
3. Check firewall isn't blocking port 8765
4. Look for errors in browser console (F12)

### LinkedIn Quick Apply Not Working
1. Ensure you're on an "Easy Apply" job posting
2. Check that auto-fill data is configured in settings
3. Verify LinkedIn content scripts are enabled
4. Try refreshing the page

### Gmail AI Features Missing
1. Confirm you're logged into Gmail
2. Check Gmail integration is enabled in settings
3. Ensure content script loaded (check browser console)
4. Verify desktop app is connected

### Context Menu Items Not Appearing
1. Check context menu feature is enabled in settings
2. Reload extension: `chrome://extensions/` → Click reload
3. Right-click on page (not on images/links for some items)

## Development 🛠️

### Debug Mode
1. Open `chrome://extensions/`
2. Find XENO extension
3. Click "Inspect views: service worker" for background debugging
4. Click "Inspect" on popup for popup debugging
5. Use F12 on web pages to debug content scripts

### Testing WebSocket
```bash
# Start server with verbose logging
python src/websocket_server.py

# In browser console:
ws = new WebSocket('ws://localhost:8765')
ws.onopen = () => console.log('Connected')
ws.send(JSON.stringify({type: 'handshake', source: 'test', version: '1.0'}))
```

### Building for Production
1. Update version in `manifest.json`
2. Test all features thoroughly
3. Package: Zip entire `browser-extension` folder
4. Upload to Chrome Web Store or Edge Add-ons

## Future Enhancements 🚀

- [ ] Firefox support (Manifest V2/V3 compatibility)
- [ ] Safari extension
- [ ] Custom keyboard shortcuts
- [ ] Offline mode with queue
- [ ] Calendar.google.com integration
- [ ] Slack/Discord integrations
- [ ] Notion/Evernote save actions
- [ ] Advanced AI features (summarization, translation)

## Support 💬

For issues, questions, or feature requests:
- Check the main XENO documentation
- Review browser console for errors
- Ensure desktop app is running
- Verify WebSocket connection

## License 📄

Part of the XENO Personal Assistant project.

---

**Built with ❤️ for productivity enthusiasts**

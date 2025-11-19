# Browser Extension Quick Start Guide

## Installation (5 minutes)

### 1. Install WebSocket Dependency
```bash
pip install websockets==12.0
```

### 2. Start WebSocket Server
```bash
python src/websocket_server.py
```

You should see:
```
INFO - XENO Browser Server started on ws://localhost:8765
```

### 3. Load Extension in Chrome/Edge

**Chrome:**
1. Open `chrome://extensions/`
2. Toggle "Developer mode" ON (top-right)
3. Click "Load unpacked"
4. Select `E:\Personal assistant\browser-extension` folder

**Edge:**
1. Open `edge://extensions/`
2. Toggle "Developer mode" ON (left sidebar)
3. Click "Load unpacked"
4. Select `E:\Personal assistant\browser-extension` folder

### 4. Configure Extension
1. Click XENO icon in toolbar
2. Status should show "Connected" (green dot)
3. Click "Settings" at bottom
4. Fill in your info for auto-fill (optional):
   - First Name
   - Last Name
   - Email
   - Phone
   - LinkedIn URL
5. Click "Save Settings"

## Features & Usage

### 🚀 Quick Actions (Any Webpage)
- **Keyboard Shortcuts:**
  - `Ctrl+Shift+E` → Quick Email
  - `Ctrl+Shift+C` → Quick Calendar
  - `Ctrl+Shift+X` → Open XENO

- **Right-Click Menu:**
  - Select text → Right-click → XENO actions

### 💼 LinkedIn
- Visit job posting
- Click "⚡ XENO Quick Apply" button on job card
- Auto-fills your saved profile data
- Creates follow-up task automatically

### 💻 GitHub
- Visit any repository
- XENO panel appears bottom-right
- Click actions:
  - 💾 Save repo to XENO
  - ✅ Create task to review
  - 📋 Copy repo info
  - 🔍 AI analysis

### 📧 Gmail
- **Compose Window:**
  - Click "⚡ XENO AI" button
  - Choose rewrite style
  - AI rewrites email instantly

- **Email Threads:**
  - "⚡ Quick Reply" → Template responses
  - "✅ Task" → Create task from email
  - "📅 Schedule" → Event from email

### 🔴 High Priority Emails
- Red dots appear on important emails
- ML predicts priority based on content
- Focus on what matters

## Architecture

```
Browser Extension (Frontend)
      ↕ WebSocket (ws://localhost:8765)
WebSocket Server (Python)
      ↕ Message Passing
XENO Desktop App (Backend)
```

All browser actions are forwarded to desktop app for processing.

## Troubleshooting

### "Offline" Status
1. Check server is running: `python src/websocket_server.py`
2. Check URL in settings: `ws://localhost:8765`
3. Click "Test Connection" in settings

### Features Not Working
1. Reload extension: `chrome://extensions/` → Click reload icon
2. Refresh webpage
3. Check browser console (F12) for errors

### LinkedIn Auto-Fill Empty
1. Open extension settings
2. Fill in "User Information" section
3. Save settings
4. Try again

## File Structure

```
browser-extension/
├── manifest.json              # Extension config
├── popup/
│   ├── popup.html            # Main UI
│   ├── popup.css             # Dark theme
│   └── popup.js              # Logic
├── background/
│   └── service-worker.js     # Background tasks
├── content/
│   ├── linkedin-quick-apply.js
│   ├── github-quick-view.js
│   └── gmail-integration.js
├── options/
│   ├── options.html          # Settings page
│   └── options.js
└── icons/                    # Extension icons
```

## Next Steps

1. Test on LinkedIn job posting
2. Test on GitHub repository
3. Test Gmail compose
4. Customize keyboard shortcuts in browser settings
5. Add your personal info for auto-fill

## Tips

- Extension icon turns green when connected
- Badge "✓" appears on supported sites (LinkedIn, GitHub, Gmail)
- All data stays local - no cloud sync
- WebSocket server must run for real-time features

## Support

Check main README.md for detailed documentation and troubleshooting.

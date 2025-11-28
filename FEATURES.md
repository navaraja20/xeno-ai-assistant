# XENO - Complete Feature List

## 🎮 Discord-Style Gaming UI

Your XENO assistant now features a beautiful, modern interface inspired by Discord and gaming software!

### Visual Design
- **Dark Theme**: Professional dark mode with charcoal backgrounds (#1e1e1e, #141414)
- **Accent Colors**: Striking cyan blue (#00d4ff) and purple (#7c3aed) accents
- **Smooth Animations**: Hover effects, transitions, and polished interactions
- **Gaming Aesthetics**: Clean, modern design that feels like premium gaming software

### Main Window Layout
```
┌───────────────────────────────────────────────────┐
│ SIDEBAR (250px)     │  MAIN CONTENT AREA          │
│ ─────────────────   │  ───────────────────        │
│                     │                              │
│ XENO                │  [Active Page Content]       │
│ ● Online            │                              │
│                     │  • Chat Interface            │
│ 💬 Chat             │  • Dashboard Overview        │
│ 📊 Dashboard        │  • Email Management          │
│ 📧 Email            │  • Job Applications          │
│ 💼 Jobs             │  • GitHub Repos              │
│ ⚙️ GitHub           │  • Settings Panel            │
│ ⚙️ Settings         │                              │
│                     │                              │
│ [User Profile]      │                              │
│ Master [Name]       │                              │
│ Administrator       │                              │
└───────────────────────────────────────────────────┘
```

### Pages & Features

#### 1. 💬 Chat Page
- **AI Chat Interface**: Full-screen chat with your AI assistant
- **Message History**: Scrollable conversation history
- **Input Box**: Type and send messages with Enter key
- **Send Button**: Stylish cyan button for sending
- **Coming Soon**: AI integration for intelligent responses

#### 2. 📊 Dashboard
- **Stats Panels**: 4 beautiful stat cards showing:
  - Emails Processed 📧
  - Jobs Applied 💼
  - GitHub Repos ⚙️
  - Tasks Completed ✓
- **Recent Activity**: Live feed of XENO actions
- **Overview**: Quick glance at all your automation

#### 3. 📧 Email Management
- **Placeholder**: Email automation coming soon
- **Future Features**: Auto-replies, filtering, inbox management

#### 4. 💼 Job Applications
- **Placeholder**: Job search automation coming soon
- **Future Features**: Auto-apply, job matching, tracking

#### 5. ⚙️ GitHub Management
- **Placeholder**: GitHub automation coming soon
- **Future Features**: Repo updates, PR reviews, commits

#### 6. ⚙️ Settings
- **Voice Settings**: Voice enabled/disabled status
- **AI Configuration**: Current AI provider
- **User Profile**: Your master name and preferences

---

## 🖱️ System Tray Integration

XENO runs minimized in your system tray for quick access!

### Tray Icon
- **Custom Icon**: Cyan "X" on dark background
- **Tooltip**: "XENO - Personal AI Assistant"
- **Status**: Shows online/offline status

### Tray Menu (Right-Click)
```
📊 Open Dashboard
───────────────────
📧 Check Emails
💼 Find Jobs
⚙️ Update GitHub
───────────────────
⚙️ Settings
ℹ️ About
───────────────────
🚪 Exit
```

### Tray Interactions
- **Single Click**: Show context menu
- **Double Click**: Open main dashboard window
- **Minimize**: Main window minimizes to tray (doesn't close app)

---

## 🖥️ Desktop Shortcut

### Automatic Creation
During setup, XENO creates a desktop shortcut automatically!

**Windows**: `XENO.lnk` (with custom icon)
**Mac**: `XENO.command` (executable script)
**Linux**: `XENO.desktop` (application file)

### Manual Creation
If automatic creation fails, you can create manually:

**Windows**:
1. Right-click Desktop → New → Shortcut
2. Target: `"C:\Path\To\python.exe" "E:\Personal assistant\src\jarvis.py"`
3. Name: XENO
4. Change Icon → Browse to `E:\Personal assistant\assets\XENO.ico`

---

## 🎤 Voice Features

### Natural Pronunciation
- XENO now says its name as "XENOo" (natural word)
- No more letter-by-letter spelling (X-E-N-O)
- Smooth, professional voice output

### Voice Settings
- **Engine**: pyttsx3 (text-to-speech)
- **Voice**: Deep male voice (David/similar)
- **Speech Rate**: 150 WPM (slower for dramatic effect)
- **Volume**: 90%
- **Style**: Optimus Prime-inspired (deep, authoritative)

### Voice Greetings
XENO greets you based on time of day:
- **Morning** (5am-12pm): "Good morning, Master [Name]. XENOo is online and ready."
- **Afternoon** (12pm-6pm): "Good afternoon, Master [Name]. XENOo is at your service."
- **Evening** (6pm-9pm): "Good evening, Master [Name]. XENOo is here to assist."
- **Night** (9pm-5am): "Greetings, Master [Name]. XENOo is operational."

---

## 🚀 Startup & Autostart

### Auto-Start on Boot
XENO automatically starts when you log into Windows!

**Enabled via**:
- Windows Registry: `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
- Entry: "XENO" = `"python.exe" "E:\Personal assistant\src\jarvis.py"`

**Disable Auto-Start**:
```python
from utils.system import disable_autostart
disable_autostart()
```

### First Run Detection
- XENO detects first run and shows setup wizard
- Creates `~/.XENO/.first_run_complete` marker file
- Subsequent runs skip wizard and go straight to main UI

---

## 📁 File Structure

```
E:\Personal assistant\
├── assets/
│   ├── XENO.ico          # Windows icon (auto-generated)
│   ├── XENO.png          # PNG icon (auto-generated)
│   ├── generate_icon.py  # Icon generator script
│   └── README.md         # Icon documentation
│
├── src/
│   ├── jarvis.py         # Main entry point
│   │
│   ├── core/
│   │   ├── config.py     # Configuration management
│   │   ├── daemon.py     # Background service
│   │   └── logger.py     # Logging system
│   │
│   ├── ui/
│   │   ├── main_window.py    # Discord-style main window
│   │   ├── tray.py           # System tray app
│   │   └── setup_wizard.py   # First-time setup
│   │
│   ├── models/
│   │   └── database.py   # SQLAlchemy models
│   │
│   └── utils/
│       └── system.py     # System utilities (autostart, shortcuts)
│
├── .env                  # API keys (OpenAI, etc.)
├── requirements.txt      # Python dependencies
├── SETUP_GUIDE.md       # Installation guide
└── README.md            # Project documentation
```

---

## ⌨️ Commands to Launch XENO

### From Desktop
- **Double-click** the XENO icon on your desktop

### From PowerShell/Terminal
```powershell
# Navigate to project
cd 'E:\Personal assistant'

# Normal launch (with UI)
python src\jarvis.py

# Force setup wizard
python src\jarvis.py --setup

# Headless mode (no UI)
python src\jarvis.py --no-ui

# Debug mode (verbose logging)
python src\jarvis.py --debug

# Combined flags
python src\jarvis.py --debug --no-ui
```

### From System Tray
- Look for XENO icon in system tray (bottom-right, Windows)
- **Double-click** icon to open dashboard
- **Right-click** icon for quick actions

### From Start Menu (Windows)
- After autostart is enabled, XENO appears in startup programs
- Search "XENO" in Windows Search

---

## 🔧 Configuration Files

### Main Config: `~/.XENO/config.yaml`
```yaml
app_name: XENO
app_version: 0.1.0
debug: false

user:
  name: "Your Name"
  voice_enabled: true

email:
  enabled: true
  provider: "gmail"
  # ... email settings

jobs:
  enabled: true
  # ... job search settings

github:
  enabled: true
  # ... GitHub settings

ai:
  provider: "openai"
  model: "gpt-4"
  # ... AI settings
```

### Environment: `.env`
```env
OPENAI_API_KEY=sk-proj-...
GITHUB_TOKEN=ghp_...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

### Database: `~/.XENO/data/XENO.db`
SQLite database storing:
- User profile
- Conversation history
- Email data
- Job applications
- GitHub repos
- Tasks and schedules

---

## 🎨 Customization

### Color Scheme
Edit `src/ui/main_window.py` to change colors:

```python
BG_DARK = "#1e1e1e"          # Main background
BG_DARKER = "#141414"        # Sidebar
ACCENT_BLUE = "#00d4ff"      # Primary accent
ACCENT_PURPLE = "#7c3aed"    # Secondary accent
TEXT_PRIMARY = "#ffffff"     # Text
```

### Window Size
```python
self.setMinimumSize(1200, 800)  # Width x Height
```

### Voice Settings
Edit `src/ui/tray.py`:
```python
self.voice_engine.setProperty('rate', 150)  # Speech speed
self.voice_engine.setProperty('volume', 0.9)  # Volume
```

### Icon
Replace `assets/XENO.ico` and `assets/XENO.png` with your own designs!

---

## 🐛 Troubleshooting

### UI Not Showing?
1. Check system tray for XENO icon
2. Double-click the tray icon
3. Verify PyQt6 is installed: `pip install PyQt6`

### Voice Not Working?
1. Install pyttsx3: `pip install pyttsx3`
2. Check volume settings
3. Verify voice engine initializes (check logs)

### Desktop Shortcut Missing?
1. Run: `python src\jarvis.py --setup`
2. Or manually create shortcut (see instructions above)
3. Ensure `assets/XENO.ico` exists

### Icons Not Showing?
1. Run: `python assets\generate_icon.py`
2. Install Pillow: `pip install pillow`

### Auto-Start Not Working?
1. Check Windows Registry: `Win+R` → `regedit`
2. Navigate to: `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
3. Verify "XENO" entry exists

---

## 📊 What's Working Now

✅ **Discord-style dark gaming UI**
✅ **6-page navigation** (Chat, Dashboard, Email, Jobs, GitHub, Settings)
✅ **System tray integration** with context menu
✅ **Desktop shortcut** auto-creation
✅ **Custom icons** (auto-generated)
✅ **Voice greetings** with natural pronunciation ("XENOo")
✅ **Auto-start on boot**
✅ **First-run setup wizard**
✅ **Configuration management**
✅ **Database integration**
✅ **Beautiful animations and hover effects**

---

## 🔄 Coming Next

🔜 **AI Chat Integration** - Connect OpenAI GPT-4 for intelligent conversations
🔜 **Email Automation** - Auto-reply, filtering, smart inbox
🔜 **Job Application Bot** - Automated job search and applications
🔜 **GitHub Automation** - Repo management, PR reviews
🔜 **LinkedIn Integration** - Profile updates, networking
🔜 **Calendar Sync** - Google Calendar integration
🔜 **Voice Commands** - Wake word detection ("Hey XENO")
🔜 **Advanced Voice** - ElevenLabs integration for ultra-realistic Optimus Prime voice
🔜 **Notifications** - Smart alerts and reminders
🔜 **Plugins System** - Extensible module architecture

---

## 🎯 Usage Examples

### Opening Dashboard
- **Method 1**: Double-click desktop XENO icon
- **Method 2**: Double-click system tray icon
- **Method 3**: `python src\jarvis.py` in terminal

### Chatting with XENO
1. Open dashboard
2. Click "💬 Chat" in sidebar
3. Type message in input box
4. Press Enter or click Send

### Viewing Stats
1. Open dashboard
2. Click "📊 Dashboard" in sidebar
3. See stats cards and recent activity

### Changing Settings
1. Open dashboard
2. Click "⚙️ Settings" in sidebar
3. View/edit voice and AI configuration

---

Enjoy your premium AI assistant! 🤖✨

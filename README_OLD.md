# JARVIS - Personal AI Assistant

A highly capable, proactive personal assistant AI inspired by Jarvis from Iron Man. Runs natively on your laptop, auto-starts on boot, and actively assists throughout your day.

## 🎯 Vision

Create an intelligent digital companion that welcomes you on startup, handles routine tasks, and intelligently suggests/automates actions to maximize productivity.

## ✨ Features

### MVP Features (Phase 1)
- ✅ **Autostart & Greeting**: Automatically starts on boot with personalized welcome
- ✅ **Conversational Interface**: Natural voice and text dialogue
- ✅ **Email Automation**: Read, summarize, reply, and manage emails
- ✅ **Job Application**: Auto-scrape, tailor resume, and apply to internships/jobs
- ✅ **GitHub Management**: Monitor repos, update documentation, sync to LinkedIn
- ✅ **LinkedIn Automation**: Profile updates, post drafting, networking
- ✅ **Daily Scheduling**: Calendar monitoring, reminders, productivity suggestions
- ✅ **Proactive Assistance**: Daily summaries, intelligent nudges

### Advanced Features (Future)
- Voice recognition and Optimus Prime-style synthesis
- Health tracking and wellness tips
- Smart home integration
- On-device AI for enhanced privacy

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    JARVIS AI Assistant                       │
├─────────────────────────────────────────────────────────────┤
│  UI Layer                                                    │
│  ├── System Tray Widget                                     │
│  ├── Desktop Dashboard                                      │
│  └── Notification System                                    │
├─────────────────────────────────────────────────────────────┤
│  Core Engine                                                 │
│  ├── Daemon Service (Auto-start)                           │
│  ├── Conversational AI (LLM Integration)                   │
│  └── Context & Memory Manager                              │
├─────────────────────────────────────────────────────────────┤
│  Integration Modules                                         │
│  ├── Email Module (Gmail, Outlook)                         │
│  ├── Job Platform Module (LinkedIn, Indeed)                │
│  ├── GitHub Module (API Integration)                       │
│  ├── LinkedIn Module (Profile & Networking)                │
│  └── Calendar Module (Google, Outlook)                     │
├─────────────────────────────────────────────────────────────┤
│  Automation Engine                                           │
│  ├── Task Scheduler                                        │
│  ├── Resume Tailor Engine                                  │
│  ├── Document Generator                                    │
│  └── Workflow Orchestrator                                 │
├─────────────────────────────────────────────────────────────┤
│  Security & Privacy                                          │
│  ├── Credential Manager (Encrypted)                        │
│  ├── Authentication System                                 │
│  └── Secure API Client                                     │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Core Technologies
- **Language**: Python 3.11+
- **UI Framework**: PyQt6 / PySide6 (cross-platform)
- **Voice**: pyttsx3, ElevenLabs API (for Optimus Prime voice)
- **LLM**: OpenAI GPT-4 / Google Gemini
- **Database**: SQLite (local), Redis (caching)

### Key Libraries
- **Email**: `imaplib`, `smtplib`, `google-api-python-client`
- **Web Scraping**: `selenium`, `beautifulsoup4`, `playwright`
- **GitHub**: `PyGithub`, `GitPython`
- **LinkedIn**: `linkedin-api`, custom scraper
- **Calendar**: `google-calendar-api`, `O365`
- **Scheduling**: `APScheduler`
- **Voice**: `speechrecognition`, `pyttsx3`, `elevenlabs`
- **AI/ML**: `openai`, `langchain`, `anthropic`

## 📋 Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Personal assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run initial setup
python src/jarvis.py --setup
```

## 🚀 Quick Start

### First Time Setup
1. Run the assistant: `python src/jarvis.py`
2. Enter your name when prompted (master registration)
3. Configure API keys and credentials
4. Select integrations to enable
5. Set preferences and schedule

### Daily Usage
- The assistant auto-starts on boot
- Interact via system tray icon or voice command
- Access dashboard for overview and controls

## 📖 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [Development Roadmap](docs/ROADMAP.md)
- [API Documentation](docs/API.md)
- [Configuration Guide](docs/CONFIGURATION.md)
- [Security & Privacy](docs/SECURITY.md)

## 🗓️ Development Timeline

### Phase 1: Foundation (Weeks 1-2)
- Core daemon service
- Basic UI and system tray
- User registration and config
- LLM integration

### Phase 2: Email & Calendar (Weeks 3-4)
- Email automation
- Calendar integration
- Daily scheduling

### Phase 3: Job Automation (Weeks 5-7)
- Job scraping
- Resume tailoring
- Auto-application system

### Phase 4: GitHub & LinkedIn (Weeks 8-9)
- GitHub monitoring
- LinkedIn automation
- Cross-platform sync

### Phase 5: Voice & Polish (Weeks 10-12)
- Voice recognition
- Optimus Prime TTS
- UI/UX refinement
- Beta testing

## 🔐 Security

- All credentials encrypted locally
- API keys stored in secure vault
- Optional biometric authentication
- Privacy-first design (local processing when possible)

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📄 License

MIT License

## 🙏 Acknowledgments

Inspired by Jarvis from Iron Man and designed to be your ultimate digital companion.

---

**Made with ❤️ for personal productivity**

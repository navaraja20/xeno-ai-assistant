# XENO AI Assistant 🤖

> *A fully-featured, Iron Man-inspired personal AI assistant with Discord-style gaming UI*

**XENO** (formerly JARVIS) is a proactive AI assistant that automates your daily tasks, manages your emails, helps with job applications, and integrates with GitHub, LinkedIn, and Google Calendar - all for **FREE**!

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![AI](https://img.shields.io/badge/AI-Gemini%20%7C%20OpenAI-orange.svg)](https://makersuite.google.com/app/apikey)

![XENO Dashboard](https://via.placeholder.com/800x400/1e1e1e/00d4ff?text=XENO+AI+Assistant+Dashboard)

---

## ✨ Features

### 🎯 Core Capabilities

- **🤖 AI Chat** - Powered by FREE Google Gemini or OpenAI GPT
- **📧 Email Automation** - Read, send, auto-reply, search emails (Gmail/Outlook/Yahoo)
- **💼 Job Search** - Search Indeed & LinkedIn, save jobs, track applications
- **🐙 GitHub Management** - Manage repos, issues, PRs, update READMEs
- **💼 LinkedIn Automation** - Post updates, send connections, get notifications
- **📅 Calendar Sync** - Google Calendar integration with event management
- **🎨 Discord-Style UI** - Beautiful dark gaming interface
- **🔐 OAuth Integration** - One-click credential setup with helper buttons

### 🚀 Automation Features

- Auto-start on Windows boot
- System tray integration
- Real-time email monitoring
- Job application tracking
- GitHub statistics dashboard
- LinkedIn profile automation
- Smart notifications
- Context-aware AI conversations

---

## 🎬 Quick Start

### Prerequisites

- **Windows** 10/11
- **Python** 3.9 or higher
- **Git** (for cloning)

### Installation

```powershell
# Clone the repository
git clone https://github.com/YOUR_USERNAME/xeno-ai-assistant.git
cd xeno-ai-assistant

# Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run XENO
python src\jarvis.py
```

### First-Time Setup

1. **Setup Wizard** will launch automatically
2. Enter your name
3. Select modules to enable
4. **Get FREE AI** (no credit card needed!):
   - Click "Get FREE Gemini Key" or visit https://makersuite.google.com/app/apikey
   - Copy API key and paste
5. **Add Credentials** (optional):
   - Gmail: Click OAuth button for app password
   - GitHub: Click OAuth button for token
   - LinkedIn: Enter credentials

**Done!** XENO is now running! 🎉

---

## 🆓 FREE AI Setup (Recommended)

XENO supports **FREE Google Gemini** - no credit card required!

### Quick Setup (2 minutes)

```powershell
python setup_free_ai.py
```

This automated script will:
1. Open Gemini API page in your browser
2. Guide you to get your FREE API key
3. Save it automatically
4. Test it for you

**Or manually:**
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google (free)
3. Click "Create API key"
4. Copy key (starts with `AIzaSy...`)
5. Add to `C:\Users\YOUR_USERNAME\.xeno\.env`:
   ```
   GEMINI_API_KEY=AIzaSy...your_key_here
   ```

See [GET_FREE_AI.md](GET_FREE_AI.md) for detailed instructions.

---

## 📖 Usage

### Dashboard

Navigate between pages using the sidebar:
- **🏠 Dashboard** - Overview, stats, recent activity
- **💬 Chat** - AI conversations with JARVIS personality
- **📧 Email** - View recent emails, refresh inbox
- **💼 Jobs** - Search jobs, track applications
- **⚙️ GitHub** - Manage repositories, view stats
- **⚙️ Settings** - Configure modules and credentials

### Email Automation

```python
# In Chat, ask XENO:
"Check my emails"
"Send an email to john@example.com"
"Show me unread emails"
```

Or use the Email page to browse emails directly.

### Job Search

1. Go to **Jobs** page
2. Enter job title (e.g., "Python Developer")
3. Enter location (optional)
4. Click **Search Jobs**
5. View results from Indeed & LinkedIn

### GitHub Management

1. Go to **GitHub** page
2. Click **Refresh Repositories**
3. Click **View Stats** for account statistics
4. Ask AI: "Create a new repository" or "Update README"

---

## 🔧 Configuration

### Environment Variables

Create/edit `C:\Users\YOUR_USERNAME\.xeno\.env`:

```bash
# AI Provider (choose one - Gemini is FREE!)
GEMINI_API_KEY=AIzaSy...your_key_here
OPENAI_API_KEY=sk-proj-...your_key_here

# Email (optional - for automation)
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_app_password

# GitHub (optional - for repo management)
GITHUB_USERNAME=your_username
GITHUB_TOKEN=ghp_...your_token

# LinkedIn (optional - for automation)
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password
```

### Modules Configuration

Enable/disable modules in Settings or during setup wizard:
- ✅ AI Chat
- ✅ Email Automation
- ✅ Job Search
- ✅ GitHub Integration
- ✅ LinkedIn Automation
- ✅ Calendar Sync

---

## 📁 Project Structure

```
xeno-ai-assistant/
├── src/
│   ├── modules/           # Automation modules
│   │   ├── ai_chat.py          # AI chat (Gemini/OpenAI)
│   │   ├── email_handler.py    # Email automation
│   │   ├── github_manager.py   # GitHub integration
│   │   ├── job_automation.py   # Job searching
│   │   ├── linkedin_automation.py  # LinkedIn automation
│   │   ├── calendar_sync.py    # Google Calendar
│   │   └── oauth_helper.py     # OAuth flows
│   ├── ui/                # User interface
│   │   ├── main_window.py      # Main dashboard
│   │   ├── setup_wizard.py     # First-time setup
│   │   └── tray.py            # System tray
│   ├── core/              # Core functionality
│   │   ├── daemon.py          # Background service
│   │   └── config.py          # Configuration
│   ├── models/            # Database models
│   │   └── database.py        # SQLAlchemy models
│   └── jarvis.py          # Main entry point
├── assets/                # Icons and resources
├── docs/                  # Documentation
├── tests/                 # Test files
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

---

## 🎨 Screenshots

### Main Dashboard
Beautiful Discord-inspired dark UI with real-time stats.

### AI Chat
Chat with XENO in JARVIS style - proactive, intelligent, slightly witty.

### Email Management
View recent emails, refresh inbox, see from/subject/date.

### Job Search
Search multiple platforms, save jobs, track applications.

---

## 🛠️ Development

### Running Tests

```powershell
# Run comprehensive tests
python test_all_modules.py

# Test specific features
python test_features.py
```

### Adding New Modules

1. Create module in `src/modules/your_module.py`
2. Add configuration in `src/core/config.py`
3. Integrate in `src/ui/main_window.py`
4. Update setup wizard if needed

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📚 Documentation

- [Complete Features Guide](COMPLETE_FEATURES_GUIDE.md) - Detailed usage for all features
- [Free AI Setup](GET_FREE_AI.md) - How to get free Gemini API key
- [Implementation Details](IMPLEMENTATION_COMPLETE.md) - Technical implementation
- [Architecture](docs/ARCHITECTURE.md) - System architecture
- [Configuration](docs/CONFIGURATION.md) - Advanced configuration

---

## 🔐 Security & Privacy

- **Credentials stored locally** in `~/.xeno/.env`
- **No data sent** to third parties (except chosen AI provider)
- **OAuth support** for secure authentication
- **Optional encryption** for sensitive data
- **Open source** - audit the code yourself

**Note:** Never commit `.env` files to version control!

---

## 🆘 Troubleshooting

### "API quota exceeded"
→ Switch to FREE Gemini: Run `python setup_free_ai.py`

### "Email not configured"
→ Add Gmail App Password in setup wizard using OAuth button

### "GitHub not configured"
→ Generate GitHub token using OAuth button in setup

### "Module not found"
→ Install dependencies: `pip install -r requirements.txt`

### XENO won't start
→ Check Python version: `python --version` (needs 3.9+)

See [FAQ](docs/FAQ.md) for more help.

---

## 🗺️ Roadmap

- [x] Core AI chat functionality
- [x] Email automation
- [x] Job search integration
- [x] GitHub management
- [x] LinkedIn automation
- [x] Google Calendar sync
- [x] OAuth integration
- [x] Free AI support (Gemini)
- [ ] Voice recognition
- [ ] Optimus Prime voice synthesis
- [ ] Mobile app companion
- [ ] Advanced analytics dashboard
- [ ] Multi-language support

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by **JARVIS** from Iron Man
- UI design inspired by **Discord**
- Powered by **Google Gemini** (free!) or **OpenAI**
- Built with **PyQt6**, **SQLAlchemy**, **Playwright**

---

## 💡 Why XENO?

**X** - eXceptional  
**E** - Executive  
**N** - Network  
**O** - Operator

Your exceptional executive assistant for everything! 🚀

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/xeno-ai-assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/xeno-ai-assistant/discussions)

---

**⭐ Star this repo if you find it useful!**

**Made with ❤️ for productivity enthusiasts and Iron Man fans**

---

<p align="center">
  <sub>XENO - Your proactive AI assistant, ready to serve. 🤖</sub>
</p>

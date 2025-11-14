# JARVIS Configuration Guide

## Initial Setup

After installation, run JARVIS for the first time to launch the setup wizard:

```bash
python src/jarvis.py
```

## Configuration File

The main configuration is stored in `~/.jarvis/config.yaml` (Windows: `%USERPROFILE%\.jarvis\config.yaml`)

### User Profile

```yaml
user:
  name: "Your Name"
  email: "your.email@example.com"
  timezone: "America/New_York"
  language: "en"
  voice_enabled: true
  voice_name: "optimus_prime"
```

### Email Module

```yaml
email:
  enabled: true
  provider: "gmail"  # or "outlook"
  check_interval: 300  # seconds (5 minutes)
  auto_summarize: true
  notify_important: true
```

**Gmail Setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download credentials and save to `~/.jarvis/credentials/gmail_credentials.json`

**Outlook Setup:**
1. Go to [Azure Portal](https://portal.azure.com/)
2. Register an application
3. Add Microsoft Graph permissions (Mail.Read, Mail.Send)
4. Note down Client ID and Client Secret

### Job Application Module

```yaml
jobs:
  enabled: true
  platforms:
    - linkedin
    - indeed
  role_types:
    - "Software Engineer"
    - "Data Scientist"
  locations:
    - "New York, NY"
    - "Remote"
  remote_only: false
  min_salary: 80000
  daily_application_limit: 5
  auto_apply: false  # Set to true for fully automated applications
```

**Resume Template:**
Place your base resume template in `~/.jarvis/templates/resume.docx`

The AI will tailor this template for each job application.

### GitHub Module

```yaml
github:
  enabled: true
  username: "your-github-username"
  auto_update_readme: true
  sync_to_linkedin: true
  check_interval: 3600  # seconds (1 hour)
```

**GitHub Token Setup:**
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Generate new token with scopes: `repo`, `read:user`, `user:email`
3. Save token in environment variable or credential vault

### LinkedIn Module

```yaml
linkedin:
  enabled: true
  auto_update_profile: false  # Requires manual approval
  suggest_connections: true
```

**LinkedIn Authentication:**
LinkedIn doesn't provide official API for automation. JARVIS uses a secure scraper.
Credentials are stored encrypted in the system keyring.

### Calendar Module

```yaml
calendar:
  enabled: true
  provider: "google"  # or "outlook"
  sync_interval: 600  # seconds (10 minutes)
  reminder_minutes: 15
```

**Google Calendar Setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Calendar API
3. Create OAuth 2.0 credentials
4. Download and save credentials

### AI/LLM Configuration

```yaml
ai:
  provider: "openai"  # or "gemini"
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 2000
  context_window: 10
```

**Supported Models:**
- OpenAI: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- Google: `gemini-pro`, `gemini-pro-vision`

**API Keys:**
- OpenAI: [Get API Key](https://platform.openai.com/api-keys)
- Google Gemini: [Get API Key](https://makersuite.google.com/app/apikey)

## Voice Configuration

JARVIS supports multiple voice options:

### Built-in TTS (pyttsx3)
Free, offline, but limited voice quality.

### ElevenLabs (Recommended for Optimus Prime voice)
High-quality voice cloning and synthesis.

1. Sign up at [ElevenLabs](https://elevenlabs.io/)
2. Get API key
3. Clone Optimus Prime voice or use pre-made voice
4. Set `ELEVENLABS_API_KEY` in `.env`

### Azure Speech Services
High-quality, customizable voices.

1. Create Azure account
2. Create Speech resource
3. Get subscription key and region
4. Configure in settings

## Security Best Practices

### Credential Storage

JARVIS uses the OS keyring for secure credential storage:

- **Windows**: Windows Credential Manager
- **macOS**: Keychain
- **Linux**: Secret Service (GNOME Keyring, KWallet)

### API Keys

Store API keys in `.env` file (never commit to git):

```bash
cp .env.example .env
# Edit .env with your keys
```

### Master Password

Optional master password for additional encryption layer:

```bash
python src/jarvis.py --setup
# Follow prompts to set master password
```

## Auto-Start Configuration

### Windows

JARVIS automatically adds itself to Windows startup via Registry.

**Manual method:**
1. Press `Win+R`
2. Type `shell:startup`
3. Create shortcut to `python C:\path\to\jarvis.py`

### macOS

JARVIS creates a Launch Agent.

**Manual method:**
```bash
cp jarvis.plist ~/Library/LaunchAgents/com.jarvis.assistant.plist
launchctl load ~/Library/LaunchAgents/com.jarvis.assistant.plist
```

### Linux

JARVIS creates a `.desktop` file in autostart.

**Manual method:**
```bash
mkdir -p ~/.config/autostart
cp jarvis.desktop ~/.config/autostart/
```

## Troubleshooting

### JARVIS won't start
- Check logs in `~/.jarvis/logs/`
- Verify Python version (3.11+ required)
- Ensure all dependencies installed: `pip install -r requirements.txt`

### Voice not working
- Check audio output device
- Verify pyttsx3 installation
- Try different TTS engine in settings

### Email not connecting
- Verify OAuth credentials
- Check internet connection
- Re-authenticate in settings

### Job applications failing
- Check platform credentials
- Verify resume template exists
- Review application logs
- Some sites may have CAPTCHA

### GitHub sync issues
- Verify GitHub token permissions
- Check rate limits
- Ensure username is correct

## Advanced Configuration

### Custom Plugins

Place custom plugins in `~/.jarvis/plugins/`:

```python
# ~/.jarvis/plugins/my_plugin.py
from jarvis.plugin import JarvisPlugin

class MyPlugin(JarvisPlugin):
    name = "my_plugin"
    version = "1.0.0"
    
    def initialize(self, context):
        # Setup code
        return True
    
    def handle_command(self, command):
        # Handle user commands
        pass
```

### Workflow Automation

Define custom workflows in `~/.jarvis/workflows/`:

```yaml
# ~/.jarvis/workflows/morning_routine.yaml
name: "Morning Routine"
trigger:
  type: "schedule"
  time: "08:00"
  days: ["monday", "tuesday", "wednesday", "thursday", "friday"]

actions:
  - type: "email"
    action: "summarize"
  - type: "calendar"
    action: "show_today"
  - type: "speak"
    message: "Good morning, Master. Here's your day."
  - type: "notification"
    title: "Daily Briefing"
    message: "Your morning briefing is ready."
```

### Custom Voice Commands

Add custom voice commands in settings:

```yaml
voice_commands:
  "what's my schedule":
    module: "calendar"
    action: "show_today"
  
  "check my inbox":
    module: "email"
    action: "summarize_unread"
  
  "find me a job":
    module: "jobs"
    action: "search_and_notify"
```

## Environment Variables

All configuration can be overridden with environment variables:

```bash
# Windows (PowerShell)
$env:JARVIS_CONFIG_DIR = "C:\custom\path"
$env:JARVIS_DEBUG = "true"

# Linux/macOS
export JARVIS_CONFIG_DIR="/custom/path"
export JARVIS_DEBUG=true
```

## Backup and Restore

### Backup

```bash
# Backup all data
cp -r ~/.jarvis ~/.jarvis.backup

# Backup only config
cp ~/.jarvis/config.yaml ~/jarvis_config_backup.yaml
```

### Restore

```bash
# Restore from backup
cp -r ~/.jarvis.backup ~/.jarvis

# Or restore just config
cp ~/jarvis_config_backup.yaml ~/.jarvis/config.yaml
```

## Performance Tuning

### Resource Limits

```yaml
performance:
  max_cpu_percent: 10
  max_memory_mb: 500
  check_interval_min: 5  # Minimum interval for API checks
```

### Cache Settings

```yaml
cache:
  enabled: true
  ttl: 3600  # seconds
  max_size_mb: 100
```

## Privacy Settings

```yaml
privacy:
  store_conversation_history: true
  history_retention_days: 30
  local_processing_only: false
  telemetry_enabled: false
```

---

For more help, see:
- [Architecture Documentation](ARCHITECTURE.md)
- [Development Roadmap](ROADMAP.md)
- [API Documentation](API.md)

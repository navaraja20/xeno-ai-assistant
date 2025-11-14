# JARVIS Architecture Documentation

## System Overview

JARVIS is a modular, event-driven personal AI assistant designed for maximum extensibility, security, and user experience. The architecture follows a layered approach with clear separation of concerns.

---

## Core Architecture Layers

### 1. Presentation Layer (UI/UX)
**Responsibility**: User interaction, visual feedback, notifications

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
├─────────────────────────────────────────┤
│  • System Tray Widget (PyQt6)           │
│  • Desktop Dashboard (Web/Native)       │
│  • Notification Manager                 │
│  • Voice Interface                      │
│  • Settings Panel                       │
└─────────────────────────────────────────┘
```

**Components**:
- **System Tray**: Always-visible icon with quick actions menu
- **Dashboard**: Main UI for overview, controls, and insights
- **Notifications**: OS-native notifications for events and reminders
- **Voice UI**: Visual feedback for voice interactions
- **Settings**: Configuration panel for all modules

---

### 2. Application Layer (Core Engine)
**Responsibility**: Business logic, orchestration, AI processing

```
┌─────────────────────────────────────────┐
│         Application Layer               │
├─────────────────────────────────────────┤
│  • Daemon Service Manager               │
│  • Conversational AI Engine             │
│  • Context & Memory Manager             │
│  • Intent Router                        │
│  • Workflow Orchestrator                │
└─────────────────────────────────────────┘
```

**Components**:
- **Daemon**: Background service that coordinates all modules
- **AI Engine**: LLM integration for natural language understanding
- **Context Manager**: Maintains conversation state and user preferences
- **Intent Router**: Routes commands to appropriate modules
- **Orchestrator**: Manages complex multi-step workflows

---

### 3. Integration Layer (Modules)
**Responsibility**: External service integration, data fetching

```
┌─────────────────────────────────────────┐
│         Integration Layer               │
├─────────────────────────────────────────┤
│  Email Module    │  Job Module          │
│  GitHub Module   │  LinkedIn Module     │
│  Calendar Module │  Custom Modules      │
└─────────────────────────────────────────┘
```

**Module Structure** (Plugin-based):
```python
class BaseModule:
    def initialize(self) -> bool
    def execute(self, command: Command) -> Result
    def schedule_tasks(self) -> List[Task]
    def shutdown(self) -> None
```

---

### 4. Automation Layer (Scripting Engine)
**Responsibility**: Task scheduling, automation workflows

```
┌─────────────────────────────────────────┐
│         Automation Layer                │
├─────────────────────────────────────────┤
│  • Task Scheduler (APScheduler)         │
│  • Workflow Engine                      │
│  • Resume Tailor Engine                 │
│  • Document Generator                   │
│  • Web Automation (Selenium)            │
└─────────────────────────────────────────┘
```

**Key Features**:
- Cron-style scheduling for recurring tasks
- Event-driven triggers (email received, calendar update)
- Workflow definitions in YAML/JSON
- Template-based document generation

---

### 5. Data Layer (Storage & Security)
**Responsibility**: Data persistence, credentials, caching

```
┌─────────────────────────────────────────┐
│         Data Layer                      │
├─────────────────────────────────────────┤
│  • SQLite Database (User, History)      │
│  • Redis Cache (Optional)               │
│  • Secure Credential Vault              │
│  • File System (Documents, Templates)   │
└─────────────────────────────────────────┘
```

**Data Stores**:
- **SQLite**: User profile, settings, conversation history, job applications
- **Redis**: Session cache, temporary data (optional)
- **Keyring**: Encrypted storage for API keys and passwords
- **File System**: Templates, generated documents, logs

---

## Detailed Component Architecture

### Daemon Service Architecture

```
┌────────────────────────────────────────────────┐
│              Daemon Manager                     │
├────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐            │
│  │  Init Service│  │ Auto-Start   │            │
│  │  - Load Config│  │ - Boot Hook  │            │
│  │  - Start Mods│  │ - Registry   │            │
│  └──────────────┘  └──────────────┘            │
│                                                 │
│  ┌──────────────────────────────────────┐      │
│  │       Event Loop (asyncio)           │      │
│  │  - Listen for commands               │      │
│  │  - Process scheduled tasks           │      │
│  │  - Handle module events              │      │
│  └──────────────────────────────────────┘      │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐            │
│  │ Health Check │  │  Shutdown    │            │
│  │ - Monitor CPU│  │ - Graceful   │            │
│  │ - Check Mods │  │ - Cleanup    │            │
│  └──────────────┘  └──────────────┘            │
└────────────────────────────────────────────────┘
```

**Lifecycle**:
1. **Boot**: OS starts → Auto-start trigger → Daemon launches
2. **Init**: Load config → Initialize modules → Start event loop
3. **Run**: Listen for commands → Execute tasks → Monitor health
4. **Shutdown**: Save state → Close connections → Exit gracefully

---

### Conversational AI Engine

```
┌────────────────────────────────────────────────┐
│         Conversational AI Engine                │
├────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────┐      │
│  │      Input Processing                │      │
│  │  - Voice → Text (Speech Recognition) │      │
│  │  - Text Normalization                │      │
│  │  - Language Detection                │      │
│  └──────────────────────────────────────┘      │
│                    ↓                            │
│  ┌──────────────────────────────────────┐      │
│  │      Context Manager                 │      │
│  │  - Conversation History (last N)     │      │
│  │  - User Preferences                  │      │
│  │  - Current Task Context              │      │
│  └──────────────────────────────────────┘      │
│                    ↓                            │
│  ┌──────────────────────────────────────┐      │
│  │      LLM Client                      │      │
│  │  - OpenAI GPT-4 / Gemini            │      │
│  │  - System Prompt (Jarvis Persona)   │      │
│  │  - Function Calling for Actions     │      │
│  └──────────────────────────────────────┘      │
│                    ↓                            │
│  ┌──────────────────────────────────────┐      │
│  │      Intent Recognition              │      │
│  │  - Extract Intent (email, job, etc.) │      │
│  │  - Extract Entities (dates, names)   │      │
│  │  - Route to Module                   │      │
│  └──────────────────────────────────────┘      │
│                    ↓                            │
│  ┌──────────────────────────────────────┐      │
│  │      Response Generation             │      │
│  │  - Format Response                   │      │
│  │  - Text → Voice (TTS)                │      │
│  │  - Display in UI                     │      │
│  └──────────────────────────────────────┘      │
└────────────────────────────────────────────────┘
```

**Example Flow**:
```
User: "Jarvis, check my emails"
  ↓
Input: Transcribe voice → Normalize text
  ↓
Context: Load last conversation + email preferences
  ↓
LLM: Process with Jarvis persona + function calling
  ↓
Intent: { action: "check_email", filter: "unread" }
  ↓
Route: email_module.execute(intent)
  ↓
Response: "You have 5 unread emails. 2 are important..."
  ↓
Output: Speak + Display in UI
```

---

### Email Module Architecture

```
┌────────────────────────────────────────────────┐
│            Email Module                         │
├────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐            │
│  │ Gmail Client │  │Outlook Client│            │
│  │  - OAuth2    │  │  - IMAP/SMTP │            │
│  │  - API Calls │  │  - O365 API  │            │
│  └──────────────┘  └──────────────┘            │
│           ↓              ↓                      │
│  ┌──────────────────────────────────────┐      │
│  │      Email Fetcher                   │      │
│  │  - Fetch unread/important            │      │
│  │  - Apply filters                     │      │
│  │  - Deduplication                     │      │
│  └──────────────────────────────────────┘      │
│                    ↓                            │
│  ┌──────────────────────────────────────┐      │
│  │      AI Summarizer                   │      │
│  │  - Extract key points                │      │
│  │  - Categorize (work, personal, etc.) │      │
│  │  - Priority scoring                  │      │
│  └──────────────────────────────────────┘      │
│                    ↓                            │
│  ┌──────────────────────────────────────┐      │
│  │      Reply Generator                 │      │
│  │  - Analyze email content             │      │
│  │  - Generate contextual reply         │      │
│  │  - User approval workflow            │      │
│  └──────────────────────────────────────┘      │
│                    ↓                            │
│  ┌──────────────────────────────────────┐      │
│  │      Actions                         │      │
│  │  - Send Reply                        │      │
│  │  - Archive/Delete                    │      │
│  │  - Mark Read/Unread                  │      │
│  │  - Set Reminder                      │      │
│  └──────────────────────────────────────┘      │
└────────────────────────────────────────────────┘
```

**Scheduled Tasks**:
- Every 5 minutes: Check for new emails
- Morning (8 AM): Generate daily email summary
- Evening (6 PM): Remind about unanswered important emails

---

### Job Application Module Architecture

```
┌────────────────────────────────────────────────┐
│         Job Application Module                  │
├────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────┐      │
│  │      Job Scrapers                    │      │
│  │  ┌────────────┐  ┌────────────┐      │      │
│  │  │  LinkedIn  │  │   Indeed   │      │      │
│  │  │  Scraper   │  │  Scraper   │      │      │
│  │  └────────────┘  └────────────┘      │      │
│  │  - Search based on preferences       │      │
│  │  - Extract job details (JD, company) │      │
│  │  - Store in database                 │      │
│  └──────────────────────────────────────┘      │
│                    ↓                            │
│  ┌──────────────────────────────────────┐      │
│  │      Job Matcher                     │      │
│  │  - Match skills to JD                │      │
│  │  - Score relevance (AI-powered)      │      │
│  │  - Filter by location, salary, etc.  │      │
│  └──────────────────────────────────────┘      │
│                    ↓                            │
│  ┌──────────────────────────────────────┐      │
│  │      Resume Tailor Engine            │      │
│  │  - Parse base resume                 │      │
│  │  - Extract JD keywords               │      │
│  │  - AI-enhanced resume generation     │      │
│  │  - ATS optimization                  │      │
│  └──────────────────────────────────────┘      │
│                    ↓                            │
│  ┌──────────────────────────────────────┐      │
│  │      Cover Letter Generator          │      │
│  │  - Analyze company & role            │      │
│  │  - Generate personalized letter      │      │
│  │  - Template-based with AI fill       │      │
│  └──────────────────────────────────────┘      │
│                    ↓                            │
│  ┌──────────────────────────────────────┐      │
│  │      Application Submitter           │      │
│  │  - Auto-fill forms (Selenium)        │      │
│  │  - Upload resume & cover letter      │      │
│  │  - Handle CAPTCHA (human fallback)   │      │
│  │  - Track submission status           │      │
│  └──────────────────────────────────────┘      │
│                    ↓                            │
│  ┌──────────────────────────────────────┐      │
│  │      Application Tracker             │      │
│  │  - Store application history         │      │
│  │  - Monitor status changes            │      │
│  │  - Send notifications                │      │
│  │  - Analytics & insights              │      │
│  └──────────────────────────────────────┘      │
└────────────────────────────────────────────────┘
```

**Database Schema**:
```sql
jobs (
    id, title, company, location, salary,
    description, url, scraped_at, relevance_score
)

applications (
    id, job_id, resume_path, cover_letter_path,
    applied_at, status, notes
)

user_preferences (
    id, role_types, locations, min_salary,
    remote_only, keywords
)
```

**Workflow**:
1. **Daily Scrape** (9 AM): Search platforms for new jobs
2. **Match & Score**: AI evaluates relevance to user profile
3. **Generate Docs**: Tailor resume and create cover letter
4. **User Review**: Notify user of top matches for approval
5. **Auto-Apply**: Submit applications (with daily limits)
6. **Track**: Monitor application status and follow-ups

---

### GitHub Module Architecture

```
┌────────────────────────────────────────────────┐
│            GitHub Module                        │
├────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────┐      │
│  │      GitHub API Client               │      │
│  │  - Authentication (PAT)              │      │
│  │  - Rate limit handling               │      │
│  │  - GraphQL & REST API                │      │
│  └──────────────────────────────────────┘      │
│                    ↓                            │
│  ┌──────────────────────────────────────┐      │
│  │      Repository Monitor              │      │
│  │  - Watch for new commits/PRs/issues  │      │
│  │  - Track stars, forks, watchers      │      │
│  │  - Contributor activity              │      │
│  └──────────────────────────────────────┘      │
│                    ↓                            │
│  ┌──────────────────────────────────────┐      │
│  │      Documentation Analyzer          │      │
│  │  - Check README quality              │      │
│  │  - Suggest badges                    │      │
│  │  - Documentation coverage            │      │
│  │  - Code comment analysis             │      │
│  └──────────────────────────────────────┘      │
│                    ↓                            │
│  ┌──────────────────────────────────────┐      │
│  │      README Generator/Updater        │      │
│  │  - AI-powered README creation        │      │
│  │  - Auto-update sections              │      │
│  │  - Add badges (CI, coverage, etc.)   │      │
│  │  - Generate table of contents        │      │
│  └──────────────────────────────────────┘      │
│                    ↓                            │
│  ┌──────────────────────────────────────┐      │
│  │      LinkedIn Sync                   │      │
│  │  - Extract project highlights        │      │
│  │  - Generate project descriptions     │      │
│  │  - Sync to LinkedIn profile          │      │
│  └──────────────────────────────────────┘      │
└────────────────────────────────────────────────┘
```

**Notifications**:
- New stars/forks on your repos
- PRs needing review
- Issues assigned to you
- Security vulnerabilities detected
- README quality below threshold

---

### Security Architecture

```
┌────────────────────────────────────────────────┐
│            Security Layer                       │
├────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────┐      │
│  │      Credential Vault                │      │
│  │  - OS Keyring Integration            │      │
│  │  - AES-256 Encryption                │      │
│  │  - API Keys (OpenAI, Gmail, etc.)    │      │
│  │  - OAuth Tokens with Refresh         │      │
│  └──────────────────────────────────────┘      │
│                                                 │
│  ┌──────────────────────────────────────┐      │
│  │      Authentication                  │      │
│  │  - First-time master password        │      │
│  │  - Optional biometric (Windows Hello)│      │
│  │  - Session management                │      │
│  └──────────────────────────────────────┘      │
│                                                 │
│  ┌──────────────────────────────────────┐      │
│  │      Data Protection                 │      │
│  │  - Local DB encryption               │      │
│  │  - Secure communication (HTTPS/TLS)  │      │
│  │  - No plaintext credential storage   │      │
│  └──────────────────────────────────────┘      │
│                                                 │
│  ┌──────────────────────────────────────┐      │
│  │      Privacy Controls                │      │
│  │  - Local processing preference       │      │
│  │  - Data retention policies           │      │
│  │  - Conversation history opt-out      │      │
│  └──────────────────────────────────────┘      │
└────────────────────────────────────────────────┘
```

**Security Best Practices**:
1. All credentials encrypted at rest
2. OAuth2 with PKCE for external services
3. No hardcoded secrets
4. Minimal permission scopes
5. Regular token rotation
6. Audit logging for sensitive actions

---

## Data Flow Diagram

### User Command to Execution

```
┌─────────┐
│  User   │
└────┬────┘
     │ "Check my emails"
     ↓
┌────────────────┐
│  Voice/Text UI │
└────┬───────────┘
     │ Transcribe/Parse
     ↓
┌──────────────────┐
│  AI Engine       │
│  - Load Context  │
│  - LLM Process   │
│  - Extract Intent│
└────┬─────────────┘
     │ Intent: check_email
     ↓
┌──────────────────┐
│  Intent Router   │
└────┬─────────────┘
     │ Route to Email Module
     ↓
┌──────────────────┐
│  Email Module    │
│  - Fetch Emails  │
│  - Summarize     │
└────┬─────────────┘
     │ Results
     ↓
┌──────────────────┐
│  AI Engine       │
│  - Format Reply  │
└────┬─────────────┘
     │ Response
     ↓
┌──────────────────┐
│  UI + Voice      │
│  - Display       │
│  - Speak         │
└──────────────────┘
```

---

## Technology Stack Summary

### Core Technologies
| Layer | Technology | Purpose |
|-------|------------|---------|
| **UI** | PyQt6 | Cross-platform desktop UI |
| **Backend** | Python 3.11+ | Core application logic |
| **AI** | OpenAI GPT-4, Gemini | Conversational intelligence |
| **Voice** | SpeechRecognition, ElevenLabs | Voice I/O |
| **Database** | SQLite, SQLAlchemy | Local data storage |
| **Scheduling** | APScheduler | Task automation |
| **Web** | Selenium, Playwright | Browser automation |

### External APIs
- **Email**: Gmail API, Microsoft Graph
- **Jobs**: LinkedIn (scraper), Indeed (scraper)
- **GitHub**: GitHub REST/GraphQL API
- **Calendar**: Google Calendar API, Microsoft Graph
- **Voice**: ElevenLabs, Azure Speech (optional)

---

## Deployment & Distribution

### Packaging
- **Windows**: PyInstaller → `.exe` + MSI installer
- **macOS**: PyInstaller → `.app` bundle + DMG
- **Linux**: PyInstaller → AppImage or snap

### Auto-start Configuration
- **Windows**: Registry `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
- **macOS**: `~/Library/LaunchAgents/com.jarvis.assistant.plist`
- **Linux**: `~/.config/autostart/jarvis.desktop`

### Updates
- Built-in update checker
- GitHub Releases for distribution
- Automatic background updates (optional)

---

## Performance Considerations

### Optimization Strategies
1. **Lazy Loading**: Load modules only when needed
2. **Caching**: Cache API responses (Redis/in-memory)
3. **Async I/O**: Non-blocking operations with asyncio
4. **Rate Limiting**: Respect API limits, queue requests
5. **Resource Monitoring**: CPU/Memory thresholds, auto-throttle

### Resource Targets
- **Idle CPU**: < 1%
- **Active CPU**: < 10%
- **Memory**: < 200 MB (idle), < 500 MB (active)
- **Startup Time**: < 5 seconds

---

## Extensibility & Plugins

### Plugin Interface
```python
class JarvisPlugin:
    """Base class for JARVIS plugins"""
    
    name: str
    version: str
    
    def initialize(self, context: PluginContext) -> bool:
        """Called when plugin loads"""
        pass
    
    def handle_command(self, command: Command) -> Optional[Response]:
        """Handle user commands"""
        pass
    
    def schedule_tasks(self) -> List[ScheduledTask]:
        """Return scheduled tasks"""
        pass
    
    def shutdown(self) -> None:
        """Cleanup before plugin unloads"""
        pass
```

### Plugin Discovery
- Plugins in `~/.jarvis/plugins/` directory
- Auto-discovery on startup
- Hot-reload support (development mode)

---

**Last Updated**: November 14, 2025
**Version**: 1.0.0-alpha

# XENO API Quick Reference Guide 🔧

Quick reference for common XENO APIs to help with integration and testing.

---

## 🔐 Security APIs

### Authentication Manager

```python
from src.security.enterprise_security import AuthenticationManager

auth = AuthenticationManager()

# User Registration
auth.register_user(username="alice", password="SecureP@ss1", email="alice@example.com")

# Authentication
result = auth.authenticate(username="alice", password="SecureP@ss1")
token = result["session_token"]

# Enable MFA (returns URI for QR code)
uri = auth.enable_mfa("alice")
# Get secret from user data
secret = auth.users["alice"]["mfa_secret"]

# Authenticate with MFA
import pyotp
totp = pyotp.TOTP(secret)
result = auth.authenticate(username="alice", password="SecureP@ss1", mfa_code=totp.now())

# Session Management
session = auth.verify_session(token)  # Returns payload or None
auth.revoke_session(token)  # Invalidate session
```

### Security Configuration

```python
from src.security.security_config import (
    PasswordValidator, InputSanitizer, RateLimiter, AuditLogger
)

# Password Validation
validator = PasswordValidator()
is_valid = validator.validate_password("SecureP@ss1")  # Returns bool

# Input Sanitization
sanitizer = InputSanitizer()
clean_email = sanitizer.sanitize_email("user@example.com")
clean_username = sanitizer.sanitize_username("alice123")
clean_filename = sanitizer.sanitize_filename("document.pdf")

# Rate Limiting
limiter = RateLimiter(max_requests=5, window_seconds=60)
allowed = limiter.check_rate_limit("user_alice")  # Returns bool

# Audit Logging
logger = AuditLogger()
logger.log_auth_attempt("alice", success=True)
logger.log_event("action", "alice", "create_team", "info")
logger.log_data_access("alice", "emails", "read")
```

---

## 👥 Collaboration APIs

### Team Manager

```python
from src.collaboration.team_features import TeamManager

team_mgr = TeamManager()

# Create Team (returns Team object, not string!)
team = team_mgr.create_team(
    team_id="dev_team",
    name="Development Team",
    description="Core developers",
    owner="alice"
)
team_id = team.team_id  # Access team_id from returned object

# Add Member (signature: team_id, username, added_by)
team_mgr.add_member("dev_team", "bob", "alice")

# Remove Member (signature: team_id, username, removed_by)
team_mgr.remove_member("dev_team", "bob", "alice")

# Update Settings (signature: team_id, settings_dict, updated_by)
team_mgr.update_team_settings(
    "dev_team",
    {"visibility": "private"},
    "alice"
)

# Get User's Teams
teams = team_mgr.get_user_teams("alice")  # Returns List[Team]

# Check Membership
is_member = team_mgr.is_team_member("dev_team", "bob")  # Returns bool
```

### Shared Calendar Manager

```python
from src.collaboration.team_features import SharedCalendarManager

cal_mgr = SharedCalendarManager()

# Create Calendar (no 'created_by' parameter!)
calendar = cal_mgr.create_calendar(
    calendar_id="team_cal",
    team_id="dev_team",
    name="Team Calendar",
    description="Shared events"
)

# Add Event (requires permission in calendar.permissions)
calendar.permissions["alice"] = "edit"
cal_mgr.add_event(
    calendar_id="team_cal",
    event_id="standup_1",
    title="Daily Standup",
    start_time="2025-11-23T09:00:00",
    end_time="2025-11-23T09:15:00",
    added_by="alice"
)

# Get Team Calendars
calendars = cal_mgr.get_team_calendars("dev_team")  # Returns List[SharedCalendar]
```

### Task Delegation Manager

```python
from src.collaboration.team_features import TaskDelegationManager

task_mgr = TaskDelegationManager()

# Assign Task
task = task_mgr.assign_task(
    task_id="task_001",
    title="Implement Feature",
    description="Build new feature",
    assigned_to="bob",
    assigned_by="alice",
    team_id="dev_team",
    due_date="2025-12-01",
    priority="high"
)

# Update Status (signature: task_id, new_status, updated_by)
task_mgr.update_task_status("task_001", "in_progress", "bob")

# Reassign Task (signature: task_id, new_assignee, reassigned_by)
task_mgr.reassign_task("task_001", "charlie", "alice")

# Get Tasks
user_tasks = task_mgr.get_user_tasks("bob")  # Returns List[TaskAssignment]
team_tasks = task_mgr.get_team_tasks("dev_team")
status_tasks = task_mgr.get_tasks_by_status("in_progress")
```

---

## 🏠 Smart Home / IoT APIs

### Smart Home Hub

```python
from src.iot.smart_home_integration import SmartHomeHub, Scene, Automation

hub = SmartHomeHub()

# Add Devices
light = hub.add_light("light_1", "Living Room Light")
thermostat = hub.add_thermostat("thermo_1", "Main Thermostat")
lock = hub.add_lock("lock_1", "Front Door")
camera = hub.add_camera("cam_1", "Driveway Camera")

# Get Device
device = hub.get_device("light_1")

# Device Control (via device methods)
light.turn_on()
light.set_brightness(75)
thermostat.set_temperature(72)
lock.lock()

# Create Device Group (method is 'create_group', not 'create_device_group')
hub.create_group("living_room", ["light_1", "light_2"])

# Create Scene (using Scene class constructor, then hub.create_scene)
scene = Scene(
    name="Movie Night",
    description="Dim lights for movies",
    hub=hub
)
scene.add_action("light_1", "set_brightness", brightness=20)
scene.add_action("light_2", "turn_off")
hub.create_scene(scene)  # Takes Scene object

# Activate Scene
hub.activate_scene("Movie Night")

# Create Automation (using Automation class, then hub.add_automation)
automation = Automation(
    name="Morning Routine",
    description="Lights on at sunrise",
    hub=hub
)
automation.add_condition("time", hour=6, minute=0)
automation.add_action("light_1", "turn_on")
automation.add_action("thermo_1", "set_temperature", temperature=68)
hub.add_automation(automation)  # Takes Automation object (method is 'add_automation')
```

### Device Classes

```python
from src.iot.smart_home_integration import SmartLight, SmartThermostat, SmartLock, SmartCamera

# Smart Light
light.turn_on()
light.turn_off()
light.set_brightness(50)  # 0-100
light.set_color(255, 0, 0)  # RGB

# Smart Thermostat
thermostat.set_temperature(72)  # Fahrenheit
thermostat.set_mode("heat")  # heat, cool, auto
temp = thermostat.get_temperature()

# Smart Lock
lock.lock()
lock.unlock()
is_locked = lock.is_locked()

# Smart Camera
camera.start_recording()
camera.stop_recording()
is_recording = camera.is_recording()
```

---

## 🎤 Voice Engine APIs

### Advanced Voice Engine

```python
from src.voice.advanced_voice_engine import AdvancedVoiceEngine

engine = AdvancedVoiceEngine()

# Initialize (required before use)
engine.initialize()

# Enroll User for Voice Biometrics
import numpy as np
audio_sample = np.random.randn(16000)  # 1 second at 16kHz
profile = engine.enroll_user("alice", audio_sample)

# Verify Speaker
is_alice = engine.verify_speaker("alice", audio_sample)

# Add Custom Wake Word
engine.add_custom_wake_word("hey assistant")

# Set Language
engine.set_language("es")  # Spanish

# Process Audio (mock - real implementation needs audio)
engine.process_audio(audio_sample)

# Respond (text-to-speech)
engine.respond("Hello, how can I help?", emotion="happy")

# Shutdown
engine.shutdown()
```

### Voice Components

```python
from src.voice.advanced_voice_engine import (
    EmotionAnalyzer,
    VoiceBiometrics,
    ConversationManager,
    WakeWordDetector
)

# Emotion Detection
emotion_analyzer = EmotionAnalyzer()
emotion = emotion_analyzer.detect_emotion_text("I'm so happy!")  # Returns emotion dict
audio_emotion = emotion_analyzer.detect_emotion_audio(audio_sample)
combined = emotion_analyzer.analyze_emotion(audio_sample, "Great news!")

# Voice Biometrics
biometrics = VoiceBiometrics()
profile = biometrics.enroll_user("alice", audio_sample)
features = biometrics.extract_voice_features(audio_sample)
verified = biometrics.verify_speaker("alice", audio_sample)
identified = biometrics.identify_speaker(audio_sample)
biometrics.update_profile("alice", audio_sample)

# Conversation Manager
conv_mgr = ConversationManager()
# Add message (signature: user_id, role, content)
conv_mgr.add_message("alice", "user", "What's the weather?")
conv_mgr.add_message("alice", "assistant", "It's sunny today")
context = conv_mgr.get_context("alice")
entities = conv_mgr.extract_entities("Book a flight to Paris")
topic_changed = conv_mgr.detect_topic_change("alice", "What about dinner?")

# Wake Word Detection
detector = WakeWordDetector()
detected = detector.detect_wake_word(audio_sample)  # Returns bool
detector.add_wake_word("computer")  # Add custom wake word
```

---

## 🤖 AI Personalization APIs

```python
from src.ml.model_finetuning import PersonalizationEngine

engine = PersonalizationEngine(user_id="alice")

# Update Preferences
engine.update_preference("communication_style", "formal")
engine.update_preference("ui.theme", "dark")  # Nested preferences

# Get Preferences
style = engine.get_preference("communication_style")
theme = engine.get_preference("ui.theme", default="light")

# Record Interactions (signature: query, response, context, rating)
engine.record_interaction(
    query="What's the weather?",
    response="It's 72°F and sunny",
    context="weather_check",
    rating=5
)

# Learn from Interactions
engine.learn_from_interaction(
    query="Schedule meeting",
    response_type="brief"  # or "detailed"
)

# Get Personalized Prompts
prompt = engine.get_personalized_prompt("weather")
formatted = engine.get_personalized_prompt("greeting", format_style="formal")

# Analyze Expertise
level = engine.analyze_expertise_level("python")  # Returns "beginner", "intermediate", "advanced"

# Save/Load
engine.save_preferences()
engine.save_interactions()
```

---

## 📊 Analytics APIs

```python
from src.ml.analytics_collector import AnalyticsCollector
from src.ml.predictive_analytics import PredictiveAnalytics

# Analytics Collection
collector = AnalyticsCollector()
collector.log_email_opened("email_123")
collector.log_email_clicked("email_123")
collector.log_job_viewed("job_456")
collector.log_job_applied("job_456")

# Predictive Analytics
predictor = PredictiveAnalytics()

# Job Success Prediction
features = {
    "skills_match": 0.85,
    "experience_match": 0.9,
    "location_match": 1.0,
    "salary_match": 0.8
}
success_prob = predictor.predict_job_success(features)

# Email Priority
email_features = {
    "sender_importance": 0.9,
    "keyword_relevance": 0.7,
    "time_sensitivity": 0.6
}
priority = predictor.predict_email_priority(email_features)
```

---

## 🔑 Common Patterns

### Error Handling

```python
try:
    result = auth.authenticate(username="alice", password="wrong")
    if not result["success"]:
        print(f"Auth failed: {result['error']}")
except Exception as e:
    print(f"Error: {e}")
```

### Type Checking

```python
from typing import Optional, List, Dict, Any
from src.collaboration.team_features import Team

# Function returns Team object
team: Team = team_mgr.create_team(...)

# Function returns Optional
session: Optional[Dict[str, Any]] = auth.verify_session(token)
if session:
    username = session["username"]
```

### Context Managers

```python
# Database operations
from src.models.database import Session

with Session() as session:
    # Perform database operations
    session.commit()
```

---

## ⚠️ Common Mistakes

### ❌ Wrong: Expecting string from create_team
```python
team_id = team_mgr.create_team(...)  # Returns Team object, not string!
```

### ✅ Correct: Get team_id from returned object
```python
team = team_mgr.create_team(...)
team_id = team.team_id
```

### ❌ Wrong: Using non-existent parameters
```python
calendar = cal_mgr.create_calendar(..., created_by="alice")  # No such parameter!
```

### ✅ Correct: Use actual parameters
```python
calendar = cal_mgr.create_calendar(calendar_id="...", team_id="...", name="...", description="...")
```

### ❌ Wrong: Wrong parameter order
```python
team_mgr.update_team_settings(team_id, "alice", settings)  # Wrong order!
```

### ✅ Correct: Settings dict comes before updated_by
```python
team_mgr.update_team_settings(team_id, settings, "alice")
```

### ❌ Wrong: Method doesn't exist
```python
hub.create_device_group("group", devices)  # Method is 'create_group'!
```

### ✅ Correct: Use actual method name
```python
hub.create_group("group", devices)
```

### ❌ Wrong: Using factory method for Scene
```python
scene = hub.create_scene(scene_name="...", ...)  # Scene uses constructor!
```

### ✅ Correct: Create Scene object, then add to hub
```python
scene = Scene(name="...", description="...", hub=hub)
scene.add_action(...)
hub.create_scene(scene)
```

---

## 📝 Tips for Testing

1. **Check return types**: Many methods return objects, not primitives
2. **Verify parameter order**: Especially for methods with optional parameters
3. **Use actual method names**: `grep` the source if unsure
4. **Check class constructors**: Some objects (Scene, Automation) use constructors
5. **Read unit tests**: They show correct usage patterns

---

## 🔍 Finding APIs

```powershell
# Search for method definitions
grep -r "def method_name" src/

# Search for class definitions
grep -r "class ClassName" src/

# Find all methods in a class
grep "def " src/path/to/file.py

# Find method signatures with parameters
grep -A 5 "def method_name" src/path/to/file.py
```

---

**For complete API documentation, see:**
- Source code in `src/` directories
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- [ARCHITECTURE.md](ARCHITECTURE.md) for system design

---

*Last updated: November 2025*
*API Version: 1.0*

# XENO Voice Commands - Quick Reference

## 🎤 Starting a Session

```
"Hey XENO"  →  Activates continuous listening mode
```

After activation, XENO listens for **30 seconds** of continuous commands. No need to repeat "Hey XENO"!

## 📧 Email Commands

| Command | Action |
|---------|--------|
| `Open my Gmail` | Opens Gmail inbox |
| `Check my email` | Shows unread count |
| `Read my emails` | Starts reading unread emails one by one |
| `Next email` | Reads next email |
| `Previous email` | Goes back to previous email |
| `Draft a reply` | Creates a reply to current email |
| `Send reply` | Sends the drafted reply |

### Email Reading Format:
```
"Email 1 of 5"
"From: John Smith"
"Subject: Project Update"
"Received on: November 26 at 9:30 AM"
"The email says: [first 300 characters]"
```

## 💼 GitHub Commands

| Command | Action |
|---------|--------|
| `Open GitHub` | Opens GitHub page |
| `Check my repositories` | Lists all your repos |
| `Check the readme files` | Reviews README files |
| `Check if my repos are up to date` | Verifies repo status |
| `Show recent commits` | Displays recent activity |

## 💼 LinkedIn/Jobs Commands

| Command | Action |
|---------|--------|
| `Open LinkedIn` | Opens LinkedIn page |
| `Check LinkedIn for new internships` | Searches internship opportunities |
| `Check LinkedIn jobs` | Browses job listings |
| `Search for [job title] jobs` | Custom job search |
| `Check my applications` | Views job applications |

## 🗂️ Navigation Commands

| Command | Action |
|---------|--------|
| `Open dashboard` | Main dashboard view |
| `Open chat` | AI chat interface |
| `Open calendar` | Calendar view |
| `Open settings` | Settings page |

## 🤖 AI Commands

| Command | Action |
|---------|--------|
| `Give me my daily briefing` | Generates daily summary |
| `What is [topic]?` | Asks AI a question |
| `How to [task]?` | Gets help from AI |
| `Tell me about [subject]` | Information query |

## 📅 Calendar Commands

| Command | Action |
|---------|--------|
| `What's my schedule?` | Shows today's schedule |
| `Schedule a meeting about [topic]` | Creates meeting |
| `Remind me to [task]` | Sets reminder |
| `Any upcoming events?` | Shows future events |

## ⚙️ System Commands

| Command | Action |
|---------|--------|
| `What time is it?` | Current time |
| `What's the date?` | Current date |
| `System status` | System health check |
| `Refresh` | Refreshes dashboard |
| `Help` | Shows available commands |

## 🛑 Ending a Session

Say any of these to pause listening:

- `Sleep`
- `Go to sleep`
- `Stop listening`
- `Pause`
- `That's all`
- `Thanks` / `Thank you`

**Or:** Session auto-pauses after 30 seconds of silence.

---

## 💡 Example Workflows

### Morning Email Check
```
"Hey XENO"
"Open my Gmail"
"Read my emails"
[listens to email 1]
"Next email"
[listens to email 2]
"Draft a reply"
[reviews draft]
"Send reply"
"Thanks"
```

### GitHub Maintenance
```
"Hey XENO"
"Open GitHub"
"Check my repositories"
"Check if my repos are up to date"
"Check the readme files"
"Thanks"
```

### Job Search
```
"Hey XENO"
"Open LinkedIn"
"Check for new internship opportunities"
"Search for Python developer jobs"
"Check my applications"
"Thanks"
```

### Multi-Platform Check
```
"Hey XENO"
"Give me my daily briefing"
"Check my email"
"Open LinkedIn"
"Check for new jobs"
"Open GitHub"
"Show recent commits"
"Thanks"
```

---

## ⚙️ Configuration

### Session Timeout
Default: **30 seconds** of silence

To change, edit `src/voice/recognition.py`:
```python
self.session_timeout = 30  # seconds
```

### Wake Word Timeout
Default: **10 seconds** after wake word

To change:
```python
self.wake_timeout = 10  # seconds
```

### Disable Continuous Mode
If you prefer traditional "Hey XENO" before each command:
```python
voice = VoiceRecognition(continuous_mode=False)
```

---

## 🎯 Tips for Best Results

✅ **Speak clearly** but naturally  
✅ **Wait** for XENO to finish speaking before next command  
✅ **Use natural language** - no need for exact phrases  
✅ **Chain commands** - do multiple tasks in one session  
✅ **Say "thanks"** when done to end session cleanly  

❌ **Avoid** speaking while XENO is responding  
❌ **Don't** shout or whisper - normal volume works best  
❌ **Minimize** background noise for better recognition  

---

## 🐛 Troubleshooting

**XENO not responding?**
- Check if you said "Hey XENO" first
- Ensure microphone is working
- Check internet connection (needed for speech recognition)

**Session keeps ending?**
- Speak within 30 seconds
- Check background noise levels
- Increase session_timeout if needed

**Email commands not working?**
- Verify email configured in `.env`
- Check EMAIL_ADDRESS and EMAIL_PASSWORD set
- Gmail users: use app-specific password

---

**For complete documentation, see [CONTINUOUS_MODE.md](CONTINUOUS_MODE.md)**

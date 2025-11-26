# XENO Continuous Listening Mode

## Overview

XENO now supports **Continuous Listening Mode** - once activated with the wake word, you can give multiple commands without saying "Hey XENO" each time. This creates a natural conversation flow for automation tasks.

## How It Works

### Activation
1. Say **"Hey XENO"** to activate continuous mode
2. XENO responds and enters an active listening session
3. Give your commands naturally without repeating the wake word

### Example Flow

```
You: "Hey XENO"
XENO: *beep* (ready)

You: "Open my Gmail"
XENO: "Opening Gmail."

You: "Read my emails"
XENO: "Email 1 of 5. From John Smith. Subject: Project Update..."

You: "Next email"
XENO: "Email 2 of 5. From Sarah Johnson. Subject: Meeting Tomorrow..."

You: "Draft a reply"
XENO: "I've drafted a reply: Thank you for your email..."

You: "Send reply"
XENO: "Reply sent successfully."

You: "Open GitHub"
XENO: "Opening GitHub."

You: "Check if my repos are up to date"
XENO: "Checking 12 repositories for updates..."

You: "Thanks"
XENO: *session ends, returns to wake word listening*
```

## Session Control

### Session Timeout
- Automatically pauses after **30 seconds of silence**
- Prevents accidental command capture
- Say "Hey XENO" again to reactivate

### Manual Pause
End the session anytime by saying:
- "Sleep"
- "Go to sleep"
- "Stop listening"
- "Pause"
- "That's all"
- "Thanks" / "Thank you"

## Enhanced Email Commands

### Reading Emails

**Check email count:**
```
"Check my email"
"How many unread emails?"
```

**Read through emails:**
```
"Read my emails"           # Starts reading unread emails
"Next email"               # Move to next email
"Previous email"           # Go back to previous email
```

**Email details provided:**
- Sender name/email
- Subject line
- Date and time received
- Email content (first 300 characters)
- Email number (e.g., "Email 3 of 10")

### Replying to Emails

**Draft a reply:**
```
"Draft a reply"
"Write a reply"
"Compose a reply"
```

XENO will:
1. Generate a professional reply based on the email context
2. Read the draft back to you
3. Wait for confirmation

**Send the reply:**
```
"Send reply"
"Send that reply"
```

## GitHub Commands

### Repository Management

**Check repositories:**
```
"Open my GitHub"
"Check my repositories"
"List my repositories"
```

**Check README files:**
```
"Check the readme files"
"Check readme files of each repo"
```

**Verify repos are current:**
```
"Check if my repos are up to date"
"Are my repos up to date?"
```

**Recent activity:**
```
"Show recent commits"
"Check recent commits"
```

## LinkedIn/Job Commands

### Job Searching

**Search for opportunities:**
```
"Check LinkedIn for new internship opportunities"
"Check LinkedIn jobs"
"Search for software engineer jobs"
"Find internships"
```

**Check applications:**
```
"Check my applications"
"Check my job applications"
```

## Navigation Commands

All these work without repeating "Hey XENO":

```
"Open my Gmail"           # Opens Gmail inbox
"Open my GitHub"          # Opens GitHub page
"Open LinkedIn"           # Opens LinkedIn page
"Open calendar"           # Opens calendar view
"Open dashboard"          # Opens main dashboard
"Open chat"               # Opens AI chat
"Open settings"           # Opens settings
```

## AI Commands

**Ask questions:**
```
"What is machine learning?"
"How to create a Python virtual environment?"
"Tell me about Docker containers"
```

**Daily briefing:**
```
"Give me my daily briefing"
"Show my daily briefing"
```

## Calendar Commands

```
"What's my schedule?"
"Schedule a meeting about project review"
"Remind me to submit report"
"Any upcoming events?"
```

## System Commands

```
"What time is it?"
"What's the date?"
"System status"
"Help"
"Refresh"
```

## Configuration

### Enable/Disable Continuous Mode

In `src/voice/recognition.py`:

```python
# Enable continuous mode (default)
voice = VoiceRecognition(continuous_mode=True)

# Disable continuous mode (traditional wake word each time)
voice = VoiceRecognition(continuous_mode=False)
```

### Adjust Timeouts

```python
self.wake_timeout = 10        # Seconds after wake word
self.session_timeout = 30     # Seconds of silence before pause
```

### Customize Exit Words

```python
self.exit_words = [
    "sleep", "go to sleep", "stop listening", 
    "pause", "that's all", "thanks", "thank you"
]
```

## Benefits

### Natural Workflow
✅ Chain multiple commands without interruption  
✅ Natural conversation flow  
✅ Faster task completion  

### Email Automation
✅ Read through emails like a human assistant  
✅ Get full context (sender, date, subject, content)  
✅ Draft and send replies with voice commands  

### Multi-Platform Management
✅ Switch between Gmail, GitHub, LinkedIn seamlessly  
✅ Check multiple systems in one session  
✅ Automate repetitive checking tasks  

### Productivity
✅ Hands-free operation  
✅ Voice-first automation  
✅ Reduced context switching  

## Privacy & Security

- Voice commands processed locally
- Only activates after wake word
- Sessions timeout automatically
- Can be paused instantly with voice
- No always-on recording

## Troubleshooting

### XENO not responding to commands
- Check microphone is working
- Ensure wake word was detected (listen for confirmation beep)
- Speak clearly and wait for response before next command

### Session keeps timing out
- Increase `session_timeout` value
- Ensure you're speaking within 30 seconds
- Check background noise isn't too loud

### Commands not recognized
- Speak naturally but clearly
- Wait for XENO to finish speaking before next command
- Check internet connection (needed for speech recognition)

### Email commands not working
- Verify email is configured in settings
- Check `.env` file has EMAIL_ADDRESS and EMAIL_PASSWORD
- Ensure using app-specific password for Gmail

## Future Enhancements

🔮 Context-aware AI replies (personalized to your writing style)  
🔮 Calendar integration for meeting scheduling  
🔮 Smart email categorization and filtering  
🔮 Voice-activated job application automation  
🔮 Multi-language support  
🔮 Custom wake words  
🔮 Voice profile training for better accuracy  

## Example Automation Workflows

### Morning Routine
```
"Hey XENO"
"Give me my daily briefing"
"Check my email"
"Read my emails"
[listens to each email]
"Open LinkedIn"
"Check for new internship opportunities"
"Open GitHub"
"Check if my repos are up to date"
"Thanks"
```

### Email Processing
```
"Hey XENO"
"Open my Gmail"
"Read my emails"
"Next email"
"Next email"
"Draft a reply"
"Send reply"
"Thanks"
```

### Job Search
```
"Hey XENO"
"Open LinkedIn"
"Search for Python developer internships"
"Check my applications"
"Thanks"
```

---

**Note:** Continuous mode is enabled by default. You can still use traditional "Hey XENO" before each command if you prefer by setting `continuous_mode=False`.

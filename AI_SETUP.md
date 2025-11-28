# XENO AI Agent Setup Guide

## 🎯 Transform XENO into an AI Agent

XENO now includes powerful AI capabilities with local LLM support (Ollama) and cloud fallback (Gemini).

---

## 📋 Prerequisites

### Hardware Requirements
- **GPU**: RTX 4050 (6GB VRAM) or better
- **CPU**: Ryzen 7 or equivalent
- **RAM**: 16GB+ recommended for local AI
- **Storage**: 10GB+ for models

### Software Requirements
- Python 3.10+
- PyQt6
- Internet connection (for Gemini fallback)

---

## 🚀 Quick Setup

### Option 1: Local AI with Ollama (Recommended)

**Why Ollama?**
- ✅ Runs locally on your RTX 4050
- ✅ 100% free forever
- ✅ Privacy-focused (no data sent to cloud)
- ✅ Fast inference on GPU
- ✅ Multiple models available

**Installation:**

1. **Download Ollama**
   - Windows: https://ollama.ai/download/windows
   - Download and run the installer

2. **Install a Model**
   ```powershell
   # Open PowerShell and run:
   ollama pull llama3.1:8b
   ```

   **Recommended models for RTX 4050 (6GB VRAM):**
   - `llama3.1:8b` - Best overall (8GB, runs well)
   - `phi3:mini` - Faster, smaller (3.8GB)
   - `gemma:7b` - Good for code (5GB)

3. **Verify Installation**
   ```powershell
   ollama list
   ```

   You should see your installed models.

4. **Test Ollama**
   ```powershell
   ollama run llama3.1:8b
   ```

   Type a question, press Enter. Type `/bye` to exit.

5. **✅ Done!** XENO will automatically detect and use Ollama.

---

### Option 2: Cloud AI with Gemini

**Why Gemini?**
- ✅ No hardware requirements
- ✅ Very powerful (GPT-4 level)
- ✅ Free tier available
- ⚠️  Requires internet
- ⚠️  Data sent to Google

**Setup:**

1. **Get API Key**
   - Go to: https://makersuite.google.com/app/apikey
   - Sign in with Google account
   - Click "Create API Key"
   - Copy the key

2. **Add to XENO**
   - Open `E:\Personal assistant\.env`
   - Find `GEMINI_API_KEY=` line
   - Paste your key:
     ```
     GEMINI_API_KEY=AIzaSy...your_key_here
     ```
   - Save file

3. **✅ Done!** XENO will use Gemini for AI features.

---

### Option 3: Hybrid (Best of Both Worlds)

Use both Ollama AND Gemini:
- Ollama for simple queries (fast, private, free)
- Gemini for complex tasks (powerful, when needed)

XENO automatically uses the best provider for each task!

---

## 🧪 Test Your Setup

### Method 1: Run Demo
```powershell
cd "E:\Personal assistant"
python demos\demo_ai_agent.py
```

### Method 2: Python Test
```python
from src.ai.ai_agent import get_ai_agent

agent = get_ai_agent()
print(agent.get_status())  # Check what's available

# Test chat
response = agent.chat("What is machine learning?")
print(response)
```

---

## 💬 Using XENO AI

### 1. Interactive Chat UI
```powershell
python demos\demo_ai_agent.py
# Choose option 4: Launch Chat UI
```

Features:
- Natural conversation
- Provider selection (Auto/Local/Cloud)
- Model switching
- Code generation
- Text analysis

### 2. Python API
```python
from src.ai.ai_agent import get_ai_agent, ModelProvider

agent = get_ai_agent()

# Natural chat
response = agent.chat("Help me find Data Science internships")

# Force local AI
response = agent.chat("Explain Python", provider=ModelProvider.LOCAL)

# Force cloud AI
response = agent.chat("Complex question", provider=ModelProvider.GEMINI)

# Generate code
code = agent.generate_code("Create a web scraper for job sites")

# Tailor resume
tailored = agent.tailor_resume(my_resume, job_description)

# Write cover letter
letter = agent.write_cover_letter(my_resume, job_desc, "Company", "Position")
```

### 3. Job Hunter Integration
```python
from src.jobs.job_hunter import get_job_hunter

hunter = get_job_hunter()
hunter.load_resume("my_resume.txt")

# AI automatically tailors resume for each job!
hunter.search_jobs(keywords=["Data Science"], location="France")
hunter.batch_apply([0, 1, 2])  # Apply to first 3 jobs
```

---

## 🎯 Job Hunting with AI

### Complete Workflow

1. **Load Your Resume**
   ```python
   hunter.load_resume("path/to/resume.txt")
   ```

2. **Search Jobs**
   ```python
   jobs = hunter.search_jobs(
       keywords=["Data Science", "Machine Learning"],
       location="France",
       sources=["indeed"],
   )
   ```

3. **Export to Excel**
   ```python
   hunter.export_to_excel("internships.xlsx")
   ```

4. **Review and Select Jobs**
   - Open `internships.xlsx`
   - Mark jobs you want to apply to

5. **Auto-Create Applications**
   ```python
   hunter.batch_apply([0, 5, 12])  # AI tailors resume per job
   ```

6. **Find Applications**
   - Check `data/jobs/applications/`
   - Resume and cover letter for each job
   - Customized to match job description

---

## 🔧 Configuration

### Change Local Model
```python
agent.set_local_model("phi3:mini")  # Faster model
agent.set_local_model("llama3.1:8b")  # Better quality
```

### List Available Models
```python
models = agent.list_local_models()
print(models)
```

### Download New Models
```powershell
ollama pull mistral:7b
ollama pull codellama:7b
ollama pull neural-chat:7b
```

### Clear Conversation History
```python
agent.clear_history()
```

---

## 📊 Performance Guide

### RTX 4050 (6GB VRAM) Performance

| Model | Size | Speed (tokens/sec) | Quality | Recommendation |
|-------|------|-------------------|---------|----------------|
| llama3.1:8b | 8GB | ~15 | Excellent | ⭐ Best overall |
| phi3:mini | 3.8GB | ~25 | Good | Fast responses |
| gemma:7b | 5GB | ~18 | Very Good | Good for code |
| mistral:7b | 4GB | ~20 | Very Good | Alternative |

### Optimization Tips

1. **Close other GPU apps** (games, video editing)
2. **Use smaller models** for simple tasks
3. **Use cloud (Gemini)** for complex analysis
4. **Enable Auto mode** - XENO chooses best provider

---

## 🆘 Troubleshooting

### Ollama Not Detected

**Problem:** XENO says "Ollama not available"

**Solution:**
```powershell
# 1. Check if Ollama is running
ollama list

# 2. If error, restart Ollama
# Right-click Ollama tray icon → Quit
# Start Ollama from Start Menu

# 3. Test connection
curl http://localhost:11434/api/tags
```

### Model Too Large for GPU

**Problem:** Out of memory error

**Solution:**
```powershell
# Use smaller model
ollama pull phi3:mini

# In Python:
agent.set_local_model("phi3:mini")
```

### Slow Inference

**Problem:** Responses take too long

**Solutions:**
1. Use smaller model (`phi3:mini`)
2. Close GPU-heavy apps
3. Use Gemini for that query
4. Reduce `max_tokens` parameter

### Gemini API Error

**Problem:** "Gemini not available"

**Check:**
1. API key in `.env` is correct
2. No extra spaces in `.env`
3. Internet connection works
4. API key not expired

---

## 🎓 Use Cases

### 1. Job Applications
```python
# Search internships
jobs = hunter.search_jobs(["Data Science"], "France")

# Auto-tailor resume + cover letter
hunter.batch_apply([0, 1, 2, 3, 4])

# Result: 5 customized applications in seconds!
```

### 2. Code Generation
```python
code = agent.generate_code("""
Create a Python function that:
1. Scrapes Indeed job listings
2. Filters Data Science positions
3. Returns DataFrame with title, company, location
""")
```

### 3. Learning Assistant
```python
response = agent.chat("""
Explain the difference between supervised and unsupervised learning.
Give examples in Data Science context.
""")
```

### 4. Text Analysis
```python
analysis = agent.analyze_text(job_description, "extract requirements")
```

---

## 📚 Advanced Features

### Custom System Prompts
```python
response = agent.chat(
    "Review this code",
    system_prompt="You are an expert Python code reviewer. Be thorough but concise."
)
```

### Temperature Control
```python
# Creative (0.9)
creative = agent.chat("Write a cover letter", temperature=0.9)

# Precise (0.1)
precise = agent.chat("Extract data from text", temperature=0.1)
```

### Conversation Context
```python
# First message
agent.chat("I'm learning machine learning")

# Follows context
agent.chat("What should I learn first?")  # Knows you mean ML

# Clear context
agent.clear_history()
```

---

## 🚀 Next Steps

1. **Setup AI** - Choose Ollama or Gemini (or both!)
2. **Test Chat** - Run `demo_ai_agent.py`
3. **Load Resume** - Add your resume to XENO
4. **Search Jobs** - Find Data Science internships
5. **Auto-Apply** - Let AI tailor applications

---

## 📞 Support

**Issues?**
- Check this guide first
- Run `demo_ai_agent.py` for diagnostics
- Check `.env` configuration
- Verify Ollama is running (if using local AI)

**Resources:**
- Ollama: https://ollama.ai/
- Gemini API: https://ai.google.dev/
- XENO Docs: See `README.md`

---

**✨ You now have a personal AI agent that can:**
- Chat naturally like Claude
- Generate code
- Analyze text
- Tailor resumes
- Write cover letters
- Auto-apply to jobs

**All running on your RTX 4050 for FREE! 🎉**

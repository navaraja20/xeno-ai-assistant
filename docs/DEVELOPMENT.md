# JARVIS Development Guide

## 🛠️ Setting Up Development Environment

### Prerequisites
- Python 3.11 or higher
- Git
- Code editor (VS Code recommended)
- Virtual environment

### Initial Setup

```bash
# Navigate to project
cd "e:\Personal assistant"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio black flake8 mypy
```

### Running JARVIS in Development Mode

```bash
# Run with debug logging
python src/jarvis.py --debug

# Run without UI (for testing daemon)
python src/jarvis.py --no-ui --debug

# Force setup wizard
python src/jarvis.py --setup
```

## 📝 Code Style Guidelines

### Python Style
- Follow PEP 8
- Use type hints
- Document with docstrings
- Use Black for formatting
- Use flake8 for linting

```bash
# Format code
black src/

# Check linting
flake8 src/

# Type checking
mypy src/
```

### Example Code

```python
"""
Module docstring explaining purpose
"""
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class MyClass:
    """Class docstring"""
    
    def __init__(self, config: dict):
        """
        Initialize MyClass
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
    
    def process(self, data: str) -> Optional[str]:
        """
        Process data
        
        Args:
            data: Input data string
            
        Returns:
            Processed string or None if failed
        """
        try:
            result = self._do_processing(data)
            return result
        except Exception as e:
            logger.error(f"Processing failed: {e}", exc_info=True)
            return None
    
    def _do_processing(self, data: str) -> str:
        """Internal processing method"""
        return data.upper()
```

## 🧩 Module Development Template

### Creating a New Module

```python
# src/modules/my_module/__init__.py
"""
My Module - Brief description
"""
from .client import MyModuleClient

__all__ = ['MyModuleClient']


# src/modules/my_module/client.py
"""
MyModule client implementation
"""
import logging
from typing import Optional, Dict, Any
from core.config import Config

logger = logging.getLogger(__name__)


class MyModuleClient:
    """Client for MyModule integration"""
    
    def __init__(self, config: Config):
        """
        Initialize MyModule client
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.enabled = config.get('my_module.enabled', False)
        logger.info("MyModule client initialized")
    
    def initialize(self) -> bool:
        """
        Initialize the module
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.info("MyModule is disabled")
            return False
        
        try:
            # Setup code here
            logger.info("MyModule initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize MyModule: {e}")
            return False
    
    def execute(self, command: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute a command
        
        Args:
            command: Command dictionary with action and parameters
            
        Returns:
            Result dictionary or None if failed
        """
        action = command.get('action')
        
        if action == 'test':
            return self._test_action(command)
        else:
            logger.warning(f"Unknown action: {action}")
            return None
    
    def _test_action(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute test action"""
        return {'status': 'success', 'message': 'Test action completed'}
    
    def shutdown(self):
        """Cleanup when shutting down"""
        logger.info("MyModule shutting down")
```

### Registering Module with Daemon

```python
# src/core/daemon.py

def _initialize_modules(self):
    """Initialize all enabled modules"""
    self.logger.info("Initializing modules...")
    
    # Import and initialize your module
    if self.config.my_module.enabled:
        from modules.my_module import MyModuleClient
        self.modules['my_module'] = MyModuleClient(self.config)
        if self.modules['my_module'].initialize():
            self.logger.info("  ✓ MyModule enabled")
```

## 🤖 Implementing the AI Engine

### Step 1: Create LLM Client

```python
# src/ai/llm_client.py
"""
LLM Client for AI interactions
"""
import os
import logging
from typing import List, Dict, Optional
import openai
from core.config import Config

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for LLM interactions"""
    
    def __init__(self, config: Config):
        """Initialize LLM client"""
        self.config = config
        self.provider = config.ai.provider
        self.model = config.ai.model
        
        # Setup API key
        if self.provider == 'openai':
            openai.api_key = os.getenv('OPENAI_API_KEY')
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None
    ) -> Optional[str]:
        """
        Send chat request to LLM
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            
        Returns:
            Assistant's response or None if failed
        """
        if temperature is None:
            temperature = self.config.ai.temperature
        if max_tokens is None:
            max_tokens = self.config.ai.max_tokens
        
        try:
            if self.provider == 'openai':
                response = await openai.ChatCompletion.acreate(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            else:
                logger.error(f"Unsupported provider: {self.provider}")
                return None
                
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            return None
    
    def get_system_prompt(self) -> str:
        """Get Jarvis system prompt"""
        name = self.config.user.name
        return f"""You are JARVIS, a highly capable personal AI assistant 
inspired by Jarvis from Iron Man. You are assisting your master, {name}.

Your personality:
- Professional yet friendly
- Proactive and intelligent
- Efficient and concise
- Respectful (address user as "Master {name}")

Your capabilities:
- Email management and summarization
- Job search and application automation
- GitHub repository management
- LinkedIn profile optimization
- Calendar and schedule management
- General assistance and conversation

Always be helpful, accurate, and maintain context of the conversation."""
```

### Step 2: Context Manager

```python
# src/ai/context_manager.py
"""
Context manager for maintaining conversation state
"""
import logging
from typing import List, Dict
from collections import deque
from models.database import get_session, ConversationHistory

logger = logging.getLogger(__name__)


class ContextManager:
    """Manages conversation context"""
    
    def __init__(self, user_id: int, max_history: int = 10):
        """
        Initialize context manager
        
        Args:
            user_id: User ID
            max_history: Maximum messages to keep in context
        """
        self.user_id = user_id
        self.max_history = max_history
        self.context = deque(maxlen=max_history)
        self._load_history()
    
    def _load_history(self):
        """Load recent conversation history from database"""
        session = get_session()
        try:
            history = session.query(ConversationHistory)\
                .filter_by(user_id=self.user_id)\
                .order_by(ConversationHistory.timestamp.desc())\
                .limit(self.max_history)\
                .all()
            
            for msg in reversed(history):
                self.context.append({
                    'role': msg.role,
                    'content': msg.content
                })
        finally:
            session.close()
    
    def add_message(self, role: str, content: str):
        """Add message to context"""
        message = {'role': role, 'content': content}
        self.context.append(message)
        
        # Save to database
        session = get_session()
        try:
            msg = ConversationHistory(
                user_id=self.user_id,
                role=role,
                content=content
            )
            session.add(msg)
            session.commit()
        finally:
            session.close()
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in context"""
        return list(self.context)
    
    def clear(self):
        """Clear context"""
        self.context.clear()
```

### Step 3: Intent Parser

```python
# src/ai/intent_parser.py
"""
Intent parser for understanding user commands
"""
import logging
from typing import Optional, Dict, Any
import re

logger = logging.getLogger(__name__)


class IntentParser:
    """Parse user intents from natural language"""
    
    # Intent patterns
    PATTERNS = {
        'check_email': [
            r'check.*(email|inbox|mail)',
            r'read.*(email|mail)',
            r'any.*(email|mail)',
        ],
        'find_jobs': [
            r'find.*(job|position|role)',
            r'search.*(job|position)',
            r'look for.*(job|position)',
        ],
        'update_github': [
            r'update.*github',
            r'check.*github',
            r'github.*(update|check)',
        ],
        'show_schedule': [
            r'(show|display|what).*(schedule|calendar)',
            r'what.*today',
            r'(meeting|appointment).*today',
        ],
    }
    
    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Parse user input to extract intent
        
        Args:
            text: User input text
            
        Returns:
            Intent dictionary or None
        """
        text = text.lower().strip()
        
        # Check each intent pattern
        for intent, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return {
                        'intent': intent,
                        'original_text': text,
                        'confidence': 0.8  # Could use ML for better confidence
                    }
        
        # No intent matched
        return {
            'intent': 'unknown',
            'original_text': text,
            'confidence': 0.0
        }
```

## 🧪 Testing

### Unit Tests

```python
# tests/test_my_module.py
"""
Tests for MyModule
"""
import pytest
from src.modules.my_module import MyModuleClient
from src.core.config import Config


@pytest.fixture
def config():
    """Create test configuration"""
    return Config()


@pytest.fixture
def client(config):
    """Create MyModule client"""
    return MyModuleClient(config)


def test_initialization(client):
    """Test client initialization"""
    assert client is not None
    assert hasattr(client, 'config')


def test_execute_test_action(client):
    """Test executing test action"""
    result = client.execute({'action': 'test'})
    assert result is not None
    assert result['status'] == 'success'


def test_unknown_action(client):
    """Test unknown action handling"""
    result = client.execute({'action': 'unknown'})
    assert result is None
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_my_module.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v
```

## 🔍 Debugging

### Enable Debug Logging

```bash
python src/jarvis.py --debug
```

### Check Logs

```bash
# Windows
type %USERPROFILE%\.jarvis\logs\jarvis_*.log

# macOS/Linux
cat ~/.jarvis/logs/jarvis_*.log

# Tail logs in real-time
# macOS/Linux
tail -f ~/.jarvis/logs/jarvis_*.log
```

### Interactive Debugging

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use built-in breakpoint() (Python 3.7+)
breakpoint()
```

## 📦 Building Distribution

### Create Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --icon=icon.ico src/jarvis.py

# Executable will be in dist/jarvis.exe
```

### Create Installer (Windows)

Use Inno Setup or NSIS to create installer package.

## 🚀 Deployment Checklist

- [ ] All tests passing
- [ ] Code formatted (black)
- [ ] Linting clean (flake8)
- [ ] Type checking passed (mypy)
- [ ] Documentation updated
- [ ] Version bumped
- [ ] Changelog updated
- [ ] Build tested on target platforms
- [ ] Installation tested
- [ ] Auto-start verified

## 📚 Additional Resources

### Python Libraries
- [PyQt6 Docs](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [OpenAI Python](https://github.com/openai/openai-python)
- [APScheduler](https://apscheduler.readthedocs.io/)

### APIs
- [Gmail API](https://developers.google.com/gmail/api)
- [GitHub API](https://docs.github.com/en/rest)
- [Google Calendar API](https://developers.google.com/calendar)
- [OpenAI API](https://platform.openai.com/docs)

### Tools
- [VS Code](https://code.visualstudio.com/)
- [Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [GitHub Desktop](https://desktop.github.com/)

---

## Next Steps

1. **Implement AI Engine** (Priority 1)
   - Create `src/ai/` package
   - Implement LLM client
   - Add context manager
   - Build intent parser

2. **Build Email Module** (Priority 2)
   - Gmail API integration
   - Email fetching
   - AI summarization

3. **Add Job Module** (Priority 3)
   - Web scraping
   - Resume tailoring
   - Application automation

Happy coding! 🚀

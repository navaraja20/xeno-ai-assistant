"""
Configuration Manager for XENO
Handles loading, saving, and accessing configuration
"""
import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(override=True)


class UserProfile(BaseModel):
    """User profile configuration"""
    name: str = ""
    email: str = ""
    timezone: str = "UTC"
    language: str = "en"
    voice_enabled: bool = True
    voice_name: str = "optimus_prime"


class EmailConfig(BaseModel):
    """Email configuration"""
    enabled: bool = False
    provider: str = "gmail"  # gmail, outlook
    address: str = ""  # User's email address
    password: str = ""  # App password (loaded from .env if empty)
    check_interval: int = 300  # seconds
    auto_summarize: bool = True
    notify_important: bool = True
    
    def __init__(self, **data):
        """Initialize with .env fallback"""
        super().__init__(**data)
        # Load from .env if not provided
        if not self.password:
            self.password = os.getenv('EMAIL_PASSWORD', '')
        if not self.address:
            self.address = os.getenv('EMAIL_ADDRESS', '')


class JobConfig(BaseModel):
    """Job application configuration"""
    enabled: bool = False
    platforms: list[str] = Field(default_factory=lambda: ["linkedin", "indeed"])
    role_types: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    remote_only: bool = False
    min_salary: Optional[int] = None
    daily_application_limit: int = 5
    auto_apply: bool = False


class GitHubConfig(BaseModel):
    """GitHub configuration"""
    enabled: bool = False
    username: str = ""
    token: str = ""  # Personal access token (loaded from .env if empty)
    auto_update_readme: bool = True
    sync_to_linkedin: bool = True
    check_interval: int = 3600  # seconds
    
    def __init__(self, **data):
        """Initialize with .env fallback"""
        super().__init__(**data)
        # Load from .env if not provided
        if not self.token:
            self.token = os.getenv('GITHUB_TOKEN', '')
        if not self.username:
            self.username = os.getenv('GITHUB_USERNAME', '')


class LinkedInConfig(BaseModel):
    """LinkedIn configuration"""
    enabled: bool = False
    email: str = ""  # LinkedIn login email
    password: str = ""  # LinkedIn password (loaded from .env if empty)
    auto_update_profile: bool = False
    suggest_connections: bool = True
    
    def __init__(self, **data):
        """Initialize with .env fallback"""
        super().__init__(**data)
        # Load from .env if not provided
        if not self.password:
            self.password = os.getenv('LINKEDIN_PASSWORD', '')
        if not self.email:
            self.email = os.getenv('LINKEDIN_EMAIL', '')


class CalendarConfig(BaseModel):
    """Calendar configuration"""
    enabled: bool = False
    provider: str = "google"  # google, outlook
    sync_interval: int = 600  # seconds
    reminder_minutes: int = 15


class AIConfig(BaseModel):
    """AI/LLM configuration"""
    provider: str = "openai"  # openai, gemini
    model: str = "gpt-4o-mini"  # gpt-4o-mini, gpt-4o, gpt-4-turbo
    api_key: str = ""  # API key (loaded from .env if empty)
    temperature: float = 0.7
    max_tokens: int = 2000
    context_window: int = 10  # number of previous messages
    
    def __init__(self, **data):
        """Initialize with .env fallback"""
        super().__init__(**data)
        # Load from .env if not provided
        if not self.api_key:
            # Try both OpenAI and Gemini keys
            if self.provider == "gemini":
                self.api_key = os.getenv('GEMINI_API_KEY', '')
            else:
                self.api_key = os.getenv('OPENAI_API_KEY', '')


class Config(BaseSettings):
    """Main configuration class"""
    
    # Application settings
    app_name: str = "XENO"
    app_version: str = "1.0.0-alpha"
    debug: bool = False
    
    # User profile
    user: UserProfile = Field(default_factory=UserProfile)
    
    # Module configurations
    email: EmailConfig = Field(default_factory=EmailConfig)
    jobs: JobConfig = Field(default_factory=JobConfig)
    github: GitHubConfig = Field(default_factory=GitHubConfig)
    linkedin: LinkedInConfig = Field(default_factory=LinkedInConfig)
    calendar: CalendarConfig = Field(default_factory=CalendarConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    
    # Paths
    config_dir: Path = Field(default_factory=lambda: Path.home() / ".XENO")
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".XENO" / "data")
    log_dir: Path = Field(default_factory=lambda: Path.home() / ".XENO" / "logs")
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration"""
        super().__init__()
        
        # Create directories
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration from file if exists
        if config_path:
            self.load_from_file(config_path)
        else:
            default_config = self.config_dir / "config.yaml"
            if default_config.exists():
                self.load_from_file(str(default_config))
    
    def load_from_file(self, path: str):
        """Load configuration from YAML or JSON file"""
        path_obj = Path(path)
        if not path_obj.exists():
            return
        
        with open(path_obj, 'r') as f:
            if path_obj.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif path_obj.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported config format: {path_obj.suffix}")
        
        # Update configuration
        if data:
            self._update_from_dict(data)
    
    def _update_from_dict(self, data: Dict[str, Any]):
        """Update configuration from dictionary"""
        if 'user' in data:
            self.user = UserProfile(**data['user'])
        if 'email' in data:
            self.email = EmailConfig(**data['email'])
        if 'jobs' in data:
            self.jobs = JobConfig(**data['jobs'])
        if 'github' in data:
            self.github = GitHubConfig(**data['github'])
        if 'linkedin' in data:
            self.linkedin = LinkedInConfig(**data['linkedin'])
        if 'calendar' in data:
            self.calendar = CalendarConfig(**data['calendar'])
        if 'ai' in data:
            self.ai = AIConfig(**data['ai'])
    
    def save(self, data: Optional[Dict[str, Any]] = None):
        """Save configuration to file"""
        if data:
            self._update_from_dict(data)
        
        config_file = self.config_dir / "config.yaml"
        
        config_dict = {
            'user': self.user.model_dump(),
            'email': self.email.model_dump(),
            'jobs': self.jobs.model_dump(),
            'github': self.github.model_dump(),
            'linkedin': self.linkedin.model_dump(),
            'calendar': self.calendar.model_dump(),
            'ai': self.ai.model_dump(),
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        keys = key.split('.')
        value = self
        for k in keys:
            value = getattr(value, k, None)
            if value is None:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value by key"""
        keys = key.split('.')
        obj = self
        for k in keys[:-1]:
            obj = getattr(obj, k)
        setattr(obj, keys[-1], value)

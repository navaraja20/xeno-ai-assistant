"""
Database models for XENO
SQLAlchemy ORM models for persistent storage
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

Base = declarative_base()


class User(Base):
    """User profile"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255))
    timezone = Column(String(50), default='UTC')
    language = Column(String(10), default='en')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConversationHistory(Base):
    """Conversation history with AI"""
    __tablename__ = 'conversation_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    role = Column(String(20))  # 'user' or 'assistant'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSON)  # Additional context (renamed from metadata)


class Job(Base):
    """Job posting"""
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255))
    location = Column(String(255))
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    description = Column(Text)
    requirements = Column(Text)
    url = Column(String(500))
    source = Column(String(50))  # 'linkedin', 'indeed', etc.
    relevance_score = Column(Float)  # AI-calculated match score
    scraped_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default='new')  # new, reviewed, applied, rejected


class JobApplication(Base):
    """Job application tracking"""
    __tablename__ = 'job_applications'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    resume_path = Column(String(500))
    cover_letter_path = Column(String(500))
    applied_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default='applied')  # applied, interview, offer, rejected, accepted
    follow_up_date = Column(DateTime)
    notes = Column(Text)
    extra_data = Column(JSON)  # Additional tracking data (renamed from metadata)


class Email(Base):
    """Email tracking"""
    __tablename__ = 'emails'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    message_id = Column(String(255), unique=True)
    sender = Column(String(255))
    recipient = Column(String(255))
    subject = Column(String(500))
    body = Column(Text)
    category = Column(String(50))  # work, personal, promotional, social
    priority = Column(String(20))  # high, medium, low
    sentiment = Column(String(20))  # positive, neutral, negative, urgent
    action_required = Column(Boolean, default=False)
    received_at = Column(DateTime)
    read_at = Column(DateTime)
    replied_at = Column(DateTime)
    archived_at = Column(DateTime)


class GitHubRepository(Base):
    """GitHub repository tracking"""
    __tablename__ = 'github_repositories'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    repo_name = Column(String(255), nullable=False)
    repo_url = Column(String(500))
    description = Column(Text)
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    watchers = Column(Integer, default=0)
    last_commit = Column(DateTime)
    readme_quality_score = Column(Float)
    last_checked = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSON)  # Additional data (renamed from metadata)


class Task(Base):
    """Task and reminder tracking"""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # email, job, github, linkedin, calendar, custom
    priority = Column(String(20), default='medium')
    status = Column(String(50), default='pending')  # pending, in_progress, completed, cancelled
    due_date = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSON)  # Additional data (renamed from metadata)


class Settings(Base):
    """Application settings"""
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    key = Column(String(255), nullable=False, unique=True)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_database(db_path: str = None):
    """Initialize database"""
    if db_path is None:
        db_path = str(Path.home() / ".xeno" / "data" / "xeno.db")
    
    # Create directory if not exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Create engine
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session factory
    Session = sessionmaker(bind=engine)
    
    return engine, Session


def get_session(db_path: str = None):
    """Get database session"""
    _, Session = init_database(db_path)
    return Session()

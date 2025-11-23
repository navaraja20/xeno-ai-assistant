"""
Unit tests for AI Model Fine-tuning
Tests personalization engine and model training capabilities
"""

import pytest
import os
import tempfile
import shutil
from datetime import datetime

from src.ai.model_finetuning import (
    PersonalizationEngine,
    TrainingExample,
    FineTuneConfig
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for test data"""
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp)


@pytest.fixture
def personalization_engine(temp_dir):
    """Create PersonalizationEngine instance"""
    return PersonalizationEngine(user_id="user123", data_dir=temp_dir)


# ==================== PersonalizationEngine Tests ====================

def test_personalization_engine_init(personalization_engine):
    """Test personalization engine initialization"""
    assert personalization_engine.user_id == "user123"
    assert personalization_engine.preferences["communication_style"] == "professional"
    assert personalization_engine.preferences["detail_level"] == "medium"


def test_update_preference_simple(personalization_engine):
    """Test updating simple preference"""
    personalization_engine.update_preference("communication_style", "casual")
    
    assert personalization_engine.preferences["communication_style"] == "casual"


def test_update_preference_nested(personalization_engine):
    """Test updating nested preference"""
    personalization_engine.update_preference("expertise_level.python", "expert")
    
    assert personalization_engine.preferences["expertise_level"]["python"] == "expert"


def test_get_preference_simple(personalization_engine):
    """Test getting simple preference"""
    value = personalization_engine.get_preference("communication_style")
    
    assert value == "professional"


def test_get_preference_nested(personalization_engine):
    """Test getting nested preference"""
    personalization_engine.update_preference("expertise_level.python", "expert")
    
    value = personalization_engine.get_preference("expertise_level.python")
    
    assert value == "expert"


def test_get_preference_with_default(personalization_engine):
    """Test getting non-existent preference with default"""
    value = personalization_engine.get_preference("nonexistent", default="default_value")
    
    assert value == "default_value"


def test_record_interaction(personalization_engine):
    """Test recording user interaction"""
    personalization_engine.record_interaction(
        query="What's the weather?",
        response="It's sunny and 75°F",
        context={"location": "San Francisco"},
        user_feedback=5
    )
    
    assert len(personalization_engine.interactions) == 1
    interaction = personalization_engine.interactions[0]
    assert interaction["query"] == "What's the weather?"
    assert interaction["feedback"] == 5


def test_record_interaction_limit(personalization_engine):
    """Test interaction history limit"""
    # Add more than 1000 interactions
    for i in range(1100):
        personalization_engine.record_interaction(
            query=f"Query {i}",
            response=f"Response {i}",
            context={}
        )
    
    # Should keep only last 1000
    assert len(personalization_engine.interactions) == 1000


def test_learn_from_interaction_brief(personalization_engine):
    """Test learning preference for brief responses"""
    personalization_engine.record_interaction(
        query="Give me a brief summary",
        response="Summary here",
        context={}
    )
    
    assert personalization_engine.preferences["detail_level"] == "brief"


def test_learn_from_interaction_detailed(personalization_engine):
    """Test learning preference for detailed responses"""
    personalization_engine.record_interaction(
        query="Please explain in detail how this works",
        response="Detailed explanation...",
        context={}
    )
    
    assert personalization_engine.preferences["detail_level"] == "detailed"


def test_get_personalized_prompt_prefix(personalization_engine):
    """Test generating personalized prompt prefix"""
    personalization_engine.update_preference("communication_style", "professional")
    personalization_engine.update_preference("tone", "formal")
    personalization_engine.update_preference("detail_level", "brief")
    
    prefix = personalization_engine.get_personalized_prompt_prefix()
    
    assert "formal" in prefix
    assert "professional" in prefix
    assert "concise" in prefix or "brief" in prefix.lower()


def test_get_personalized_prompt_with_format(personalization_engine):
    """Test prompt generation with specific format preference"""
    personalization_engine.update_preference("response_format", "bullet-points")
    
    prefix = personalization_engine.get_personalized_prompt_prefix()
    
    assert "bullet" in prefix.lower()


def test_analyze_expertise_level_beginner(personalization_engine):
    """Test analyzing beginner expertise level"""
    # Record interactions with basic questions
    personalization_engine.record_interaction(
        query="What is Python?",
        response="Python is a programming language",
        context={}
    )
    personalization_engine.record_interaction(
        query="How to install Python?",
        response="Download from python.org",
        context={}
    )
    
    level = personalization_engine.analyze_expertise_level("python")
    
    assert level == "beginner"


def test_analyze_expertise_level_advanced(personalization_engine):
    """Test analyzing advanced expertise level"""
    # Record interactions with advanced questions
    personalization_engine.record_interaction(
        query="How to optimize Python performance?",
        response="Use profiling and caching",
        context={}
    )
    personalization_engine.record_interaction(
        query="Best practices for Python architecture?",
        response="Follow SOLID principles",
        context={}
    )
    
    level = personalization_engine.analyze_expertise_level("python")
    
    assert level == "advanced"


def test_analyze_expertise_level_no_history(personalization_engine):
    """Test expertise analysis with no interaction history"""
    level = personalization_engine.analyze_expertise_level("javascript")
    
    assert level == "beginner"


def test_save_and_load_preferences(temp_dir):
    """Test saving and loading preferences"""
    # Create engine and set preferences
    engine1 = PersonalizationEngine(user_id="user123", data_dir=temp_dir)
    engine1.update_preference("communication_style", "casual")
    engine1.update_preference("expertise_level.python", "expert")
    
    # Create new engine instance to test loading
    engine2 = PersonalizationEngine(user_id="user123", data_dir=temp_dir)
    
    assert engine2.preferences["communication_style"] == "casual"
    assert engine2.preferences["expertise_level"]["python"] == "expert"


def test_save_and_load_interactions(temp_dir):
    """Test saving and loading interactions"""
    # Create engine and record interactions
    engine1 = PersonalizationEngine(user_id="user123", data_dir=temp_dir)
    engine1.record_interaction("Query 1", "Response 1", {})
    engine1.record_interaction("Query 2", "Response 2", {})
    
    # Create new engine instance to test loading
    engine2 = PersonalizationEngine(user_id="user123", data_dir=temp_dir)
    
    assert len(engine2.interactions) == 2


# ==================== TrainingExample Tests ====================

def test_training_example_creation():
    """Test creating training example"""
    example = TrainingExample(
        input_text="What's the weather?",
        output_text="It's sunny",
        context={"location": "SF"},
        user_rating=5
    )
    
    assert example.input_text == "What's the weather?"
    assert example.output_text == "It's sunny"
    assert example.context["location"] == "SF"
    assert example.user_rating == 5
    assert example.timestamp is not None


def test_training_example_default_values():
    """Test training example default values"""
    example = TrainingExample(
        input_text="Test input",
        output_text="Test output"
    )
    
    assert example.context == {}
    assert example.user_rating is None
    assert isinstance(example.timestamp, str)


# ==================== FineTuneConfig Tests ====================

def test_finetune_config_creation():
    """Test creating fine-tune configuration"""
    config = FineTuneConfig(
        model_name="my_model",
        base_model="gpt-4",
        learning_rate=0.001,
        epochs=5
    )
    
    assert config.model_name == "my_model"
    assert config.base_model == "gpt-4"
    assert config.learning_rate == 0.001
    assert config.epochs == 5


def test_finetune_config_defaults():
    """Test fine-tune configuration defaults"""
    config = FineTuneConfig(model_name="my_model")
    
    assert config.base_model == "gpt-3.5-turbo"
    assert config.learning_rate == 0.001
    assert config.batch_size == 32
    assert config.epochs == 10
    assert config.validation_split == 0.2
    assert config.min_examples == 50


# ==================== Integration Tests ====================

def test_personalization_workflow(personalization_engine):
    """Test complete personalization workflow"""
    # 1. User starts with default preferences
    assert personalization_engine.get_preference("communication_style") == "professional"
    
    # 2. User interacts and system learns
    personalization_engine.record_interaction(
        query="Give me a quick summary",
        response="Brief summary here",
        context={},
        user_feedback=5
    )
    
    # 3. Preferences updated
    assert personalization_engine.get_preference("detail_level") == "brief"
    
    # 4. Generate personalized prompt
    prompt = personalization_engine.get_personalized_prompt_prefix()
    assert "concise" in prompt.lower() or "brief" in prompt.lower()
    
    # 5. Track expertise
    personalization_engine.record_interaction(
        query="Advanced Python design patterns",
        response="Singleton, Factory...",
        context={}
    )
    level = personalization_engine.analyze_expertise_level("python")
    assert level in ["intermediate", "advanced"]


def test_multi_user_personalization(temp_dir):
    """Test personalization for multiple users"""
    # Create engines for different users
    user1 = PersonalizationEngine(user_id="user1", data_dir=temp_dir)
    user2 = PersonalizationEngine(user_id="user2", data_dir=temp_dir)
    
    # Set different preferences
    user1.update_preference("communication_style", "casual")
    user2.update_preference("communication_style", "formal")
    
    # Verify isolation
    assert user1.get_preference("communication_style") == "casual"
    assert user2.get_preference("communication_style") == "formal"
    
    # Reload and verify persistence
    user1_reload = PersonalizationEngine(user_id="user1", data_dir=temp_dir)
    user2_reload = PersonalizationEngine(user_id="user2", data_dir=temp_dir)
    
    assert user1_reload.get_preference("communication_style") == "casual"
    assert user2_reload.get_preference("communication_style") == "formal"


def test_preference_evolution(personalization_engine):
    """Test how preferences evolve over time"""
    # Start with medium detail
    assert personalization_engine.get_preference("detail_level") == "medium"
    
    # Multiple interactions requesting brief responses
    for _ in range(3):
        personalization_engine.record_interaction(
            query="Quick summary please",
            response="Summary",
            context={}
        )
    
    # Should learn to prefer brief
    assert personalization_engine.get_preference("detail_level") == "brief"
    
    # Now user wants detailed
    for _ in range(3):
        personalization_engine.record_interaction(
            query="Explain in detail",
            response="Detailed explanation",
            context={}
        )
    
    # Should update to detailed
    assert personalization_engine.get_preference("detail_level") == "detailed"

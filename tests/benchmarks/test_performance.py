"""
Performance Benchmark Tests for XENO
Uses pytest-benchmark for consistent performance testing
Run with: pytest tests/benchmarks/ -v --benchmark-only
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))


# ==================== Security Benchmarks ====================

@pytest.fixture
def encryption_manager():
    """Fixture for encryption manager"""
    from src.security.enterprise_security import EncryptionManager
    return EncryptionManager()


@pytest.fixture
def password_validator():
    """Fixture for password validator"""
    from src.security.security_config import PasswordValidator
    return PasswordValidator


def test_encryption_performance(benchmark, encryption_manager):
    """Benchmark encryption/decryption"""
    test_data = "This is test data " * 50  # 900 bytes
    
    def encrypt_decrypt():
        encrypted = encryption_manager.encrypt_data(test_data)
        decrypted = encryption_manager.decrypt_data(encrypted)
        return decrypted
    
    result = benchmark(encrypt_decrypt)
    assert result == test_data


def test_password_hashing_performance(benchmark, encryption_manager):
    """Benchmark password hashing"""
    password = "SecurePassword123!@#"
    
    def hash_password():
        return encryption_manager.hash_password(password)
    
    result = benchmark(hash_password)
    assert len(result) == 2  # (hash, salt)


def test_password_validation_performance(benchmark, password_validator):
    """Benchmark password validation"""
    password = "C0mpl3x!P@ssW0RD"  # No sequential chars
    
    def validate():
        return password_validator.validate(password)
    
    is_valid, errors = benchmark(validate)
    assert is_valid


# ==================== AI/ML Benchmarks ====================

@pytest.fixture
def personalization_engine():
    """Fixture for personalization engine"""
    from src.ai.model_finetuning import PersonalizationEngine
    return PersonalizationEngine("benchmark_user")


def test_preference_update_performance(benchmark, personalization_engine):
    """Benchmark preference updates"""
    
    def update_preference():
        personalization_engine.update_preference("test_key", "test_value")
    
    benchmark(update_preference)


def test_interaction_recording_performance(benchmark, personalization_engine):
    """Benchmark interaction recording"""
    
    def record():
        personalization_engine.record_interaction(
            query="test query",
            response="test response",
            context={"test": "context"}
        )
    
    benchmark(record)


# ==================== Collaboration Benchmarks ====================

@pytest.fixture
def team_manager():
    """Fixture for team manager"""
    from src.collaboration.team_features import TeamManager
    mgr = TeamManager()
    # Pre-create a test team
    mgr.create_team(
        team_id="bench_team",
        name="Benchmark Team",
        description="For benchmarking",
        owner="bench_owner"
    )
    return mgr


def test_team_creation_performance(benchmark):
    """Benchmark team creation"""
    from src.collaboration.team_features import TeamManager
    
    counter = [0]
    
    def create_team():
        mgr = TeamManager()
        team_id = f"team_{counter[0]}"
        counter[0] += 1
        return mgr.create_team(
            team_id=team_id,
            name=f"Test Team {team_id}",
            description="Test team",
            owner="test_owner"
        )
    
    result = benchmark(create_team)
    assert result is not None


def test_member_addition_performance(benchmark, team_manager):
    """Benchmark adding team members"""
    
    counter = [0]
    
    def add_member():
        member_id = f"member_{counter[0]}"
        counter[0] += 1
        return team_manager.add_member("bench_team", member_id, "member")
    
    result = benchmark(add_member)
    assert result is True


# ==================== IoT Benchmarks ====================

@pytest.fixture
def iot_hub():
    """Fixture for IoT hub"""
    from src.iot.smart_home_integration import SmartHomeHub
    return SmartHomeHub()


@pytest.fixture
def smart_light():
    """Fixture for smart light"""
    from src.iot.smart_home_integration import SmartLight
    return SmartLight("test_light", "Test Light", "http://test.local", "test_key")


def test_device_registration_performance(benchmark, iot_hub, smart_light):
    """Benchmark device registration"""
    
    def register():
        iot_hub.register_device(smart_light)
    
    benchmark(register)


def test_device_lookup_performance(benchmark, iot_hub):
    """Benchmark device lookup"""
    from src.iot.smart_home_integration import SmartLight
    
    # Pre-populate with devices
    for i in range(100):
        light = SmartLight(f"light_{i}", f"Light {i}", "http://test.local", "key")
        iot_hub.register_device(light)
    
    def lookup():
        return iot_hub.get_device("light_50")
    
    result = benchmark(lookup)
    assert result is not None


# ==================== Input Sanitization Benchmarks ====================

@pytest.fixture
def input_sanitizer():
    """Fixture for input sanitizer"""
    from src.security.security_config import InputSanitizer
    return InputSanitizer


def test_email_sanitization_performance(benchmark, input_sanitizer):
    """Benchmark email sanitization"""
    email = "  Test.User@EXAMPLE.COM  "
    
    def sanitize():
        return input_sanitizer.sanitize_email(email)
    
    result = benchmark(sanitize)
    assert result == "test.user@example.com"


def test_username_sanitization_performance(benchmark, input_sanitizer):
    """Benchmark username sanitization"""
    username = "test_user_123"
    
    def sanitize():
        return input_sanitizer.sanitize_username(username)
    
    result = benchmark(sanitize)
    assert result == username


def test_filename_sanitization_performance(benchmark, input_sanitizer):
    """Benchmark filename sanitization"""
    filename = "my_file_name.txt"
    
    def sanitize():
        return input_sanitizer.sanitize_filename(filename)
    
    result = benchmark(sanitize)
    assert result == filename


# ==================== Rate Limiting Benchmarks ====================

@pytest.fixture
def rate_limiter():
    """Fixture for rate limiter"""
    from src.security.security_config import RateLimiter
    return RateLimiter()


def test_rate_limit_check_performance(benchmark, rate_limiter):
    """Benchmark rate limit checking"""
    
    counter = [0]
    
    def check_limit():
        user = f"user_{counter[0] % 10}"  # Rotate through 10 users
        counter[0] += 1
        return rate_limiter.is_allowed(user, max_requests=100, window_seconds=60)
    
    result = benchmark(check_limit)
    assert isinstance(result, bool)


# ==================== Complex Workflow Benchmarks ====================

def test_full_authentication_workflow_performance(benchmark):
    """Benchmark complete authentication workflow"""
    from src.security.enterprise_security import AuthenticationManager
    
    auth_mgr = AuthenticationManager(secret_key="benchmark_secret_key_123")
    
    # Pre-register one user to avoid registration overhead in benchmark
    auth_mgr.register_user("bench_user", "SecurePass123!@#", "bench@test.com")
    
    def auth_workflow():
        # Just authenticate (registration is file I/O heavy)
        result = auth_mgr.authenticate("bench_user", "SecurePass123!@#")
        return result["success"]
    
    result = benchmark(auth_workflow)
    assert result is True


def test_team_task_workflow_performance(benchmark):
    """Benchmark team and task creation workflow"""
    from src.collaboration.team_features import TeamManager, TaskDelegationManager
    
    counter = [0]
    
    def workflow():
        team_mgr = TeamManager()
        task_mgr = TaskDelegationManager()
        
        team_id = f"team_{counter[0]}"
        counter[0] += 1
        
        # Create team
        team_mgr.create_team(
            team_id=team_id,
            name=f"Team {team_id}",
            description="Benchmark team",
            owner="owner"
        )
        
        # Add member
        team_mgr.add_member(team_id, "member1", "member")
        
        # Assign task
        task_mgr.assign_task(
            task_id=f"task_{counter[0]}",
            title="Benchmark Task",
            description="Test task",
            assigned_to="member1",
            assigned_by="owner",
            team_id=team_id
        )
        
        return team_id
    
    result = benchmark(workflow)
    assert result is not None

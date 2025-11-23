"""
End-to-End Authentication Flow Tests
Tests complete user authentication workflows from registration to session management
"""

import pytest
from pathlib import Path
import sys
import tempfile
import shutil
import pyotp

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from src.security.enterprise_security import (
    AuthenticationManager,
    EncryptionManager
)
from src.security.security_config import (
    PasswordValidator,
    RateLimiter,
    AuditLogger
)


@pytest.fixture
def auth_manager():
    """Fixture for authentication manager"""
    return AuthenticationManager(secret_key="e2e_test_secret_key_12345")


@pytest.fixture
def temp_dir():
    """Fixture for temporary directory"""
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp, ignore_errors=True)


# ==================== Registration Flow ====================

def test_e2e_user_registration_flow(auth_manager):
    """E2E: Complete user registration process"""
    # Step 1: Validate password strength
    password = "SecureP@ssW9rD!"
    is_valid, errors = PasswordValidator.validate(password)
    assert is_valid, f"Password validation failed: {errors}"
    
    # Step 2: Register user
    result = auth_manager.register_user(
        username="test_user",
        password=password,
        email="test@example.com",
        role="user"
    )
    
    assert result["success"] is True
    assert result["username"] == "test_user"
    
    # Step 3: Verify user exists
    assert "test_user" in auth_manager.users
    user = auth_manager.users["test_user"]
    assert user["email"] == "test@example.com"
    assert user["role"] == "user"
    assert user["mfa_enabled"] is False


def test_e2e_duplicate_registration_prevention(auth_manager):
    """E2E: Prevent duplicate user registration"""
    # Register first time
    auth_manager.register_user(
        username="duplicate_user",
        password="SecureP@sW9D!!",
        email="dup@test.com"
    )
    
    # Attempt duplicate registration
    with pytest.raises(ValueError, match="Username already exists"):
        auth_manager.register_user(
            username="duplicate_user",
            password="DifferentP@ss456!",
            email="different@test.com"
        )


# ==================== Authentication Flow ====================

def test_e2e_successful_authentication_flow(auth_manager):
    """E2E: Complete successful authentication"""
    password = "MyP@ssword123"
    
    # Step 1: Register user
    auth_manager.register_user(
        username="auth_user",
        password=password,
        email="auth@test.com"
    )
    
    # Step 2: Authenticate
    result = auth_manager.authenticate(
        username="auth_user",
        password=password
    )
    
    # Step 3: Verify authentication success
    assert result["success"] is True
    assert "session_token" in result
    assert result["username"] == "auth_user"
    assert result["role"] == "user"
    
    # Step 4: Verify session created
    token = result["session_token"]
    session = auth_manager.verify_session(token)
    assert session is not None
    assert session["username"] == "auth_user"


def test_e2e_failed_authentication_flow(auth_manager):
    """E2E: Failed authentication with wrong password"""
    # Register user
    auth_manager.register_user(
        username="wrong_pass_user",
        password="CorrectP@sW9D!",
        email="wrong@test.com"
    )
    
    # Attempt authentication with wrong password
    result = auth_manager.authenticate(
        username="wrong_pass_user",
        password="WrongP@ss456"
    )
    
    assert result["success"] is False
    assert "error" in result
    assert "Invalid credentials" in result["error"]


def test_e2e_account_lockout_flow(auth_manager):
    """E2E: Account lockout after multiple failed attempts"""
    password = "RealP@sW9D!"
    
    # Register user
    auth_manager.register_user(
        username="lockout_user",
        password=password,
        email="lockout@test.com"
    )
    
    # Make 5 failed login attempts
    for i in range(5):
        result = auth_manager.authenticate(
            username="lockout_user",
            password=f"WrongP@ss{i}"
        )
        assert result["success"] is False
    
    # 6th attempt should be locked
    result = auth_manager.authenticate(
        username="lockout_user",
        password=password  # Even with correct password
    )
    
    assert result["success"] is False
    assert "locked" in result["error"].lower()


# ==================== MFA Flow ====================

def test_e2e_mfa_setup_and_authentication(auth_manager):
    """E2E: Complete MFA setup and authentication"""
    password = "MFAP@sW9D!"
    
    # Step 1: Register user
    auth_manager.register_user(
        username="mfa_user",
        password=password,
        email="mfa@test.com"
    )
    
    # Step 2: Enable MFA (returns URI)
    uri = auth_manager.enable_mfa("mfa_user")
    assert uri is not None
    assert auth_manager.users["mfa_user"]["mfa_enabled"] is True
    
    # Step 3: Get secret from user data and generate TOTP code
    secret = auth_manager.users["mfa_user"]["mfa_secret"]
    totp = pyotp.TOTP(secret)
    current_code = totp.now()
    
    # Step 4: Authenticate with MFA
    result = auth_manager.authenticate(
        username="mfa_user",
        password=password,
        mfa_code=current_code
    )
    
    assert result["success"] is True
    assert "session_token" in result


def test_e2e_mfa_required_but_not_provided(auth_manager):
    """E2E: MFA required but code not provided"""
    password = "MFAP@ss456"
    
    # Register and enable MFA
    auth_manager.register_user(
        username="mfa_required",
        password=password,
        email="mfarequired@test.com"
    )
    auth_manager.enable_mfa("mfa_required")
    
    # Attempt authentication without MFA code
    result = auth_manager.authenticate(
        username="mfa_required",
        password=password
    )
    
    assert result["success"] is False
    assert result.get("mfa_required") is True
    assert "MFA code required" in result["error"]


def test_e2e_mfa_invalid_code(auth_manager):
    """E2E: MFA authentication with invalid code"""
    password = "MFAP@ss789"
    
    # Register and enable MFA
    auth_manager.register_user(
        username="mfa_invalid",
        password=password,
        email="mfainvalid@test.com"
    )
    auth_manager.enable_mfa("mfa_invalid")
    
    # Attempt with wrong MFA code
    result = auth_manager.authenticate(
        username="mfa_invalid",
        password=password,
        mfa_code="000000"  # Invalid code
    )
    
    assert result["success"] is False
    assert "Invalid MFA code" in result["error"]


# ==================== Session Management Flow ====================

def test_e2e_session_lifecycle(auth_manager):
    """E2E: Complete session lifecycle (create, verify, revoke)"""
    password = "SessionP@sW9D!"
    
    # Step 1: Register and authenticate
    auth_manager.register_user(
        username="session_user",
        password=password,
        email="session@test.com"
    )
    
    result = auth_manager.authenticate(
        username="session_user",
        password=password
    )
    token = result["session_token"]
    
    # Step 2: Verify session is valid
    session = auth_manager.verify_session(token)
    assert session is not None
    assert session["username"] == "session_user"
    
    # Step 3: Revoke session
    auth_manager.revoke_session(token)
    
    # Step 4: Verify session is invalid
    session = auth_manager.verify_session(token)
    assert session is None


# ==================== Data Export Flow ====================

def test_e2e_user_data_export_flow(auth_manager, temp_dir):
    """E2E: User data export process"""
    password = "ExportP@sW9D!"
    
    # Step 1: Register user with data
    auth_manager.register_user(
        username="export_user",
        password=password,
        email="export@test.com"
    )
    
    # Step 2: Collect user data
    user = auth_manager.users["export_user"]
    user_data = {
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "created_at": user["created_at"]
    }
    
    # Step 3: Export to file
    export_file = Path(temp_dir) / "user_export.json"
    import json
    with open(export_file, 'w') as f:
        json.dump(user_data, f, indent=2)
    
    # Step 4: Verify export exists
    assert export_file.exists()
    
    # Read and verify
    with open(export_file, 'r') as f:
        exported = json.load(f)
    
    assert exported["username"] == "export_user"
    assert exported["email"] == "export@test.com"


def test_e2e_account_deletion_flow(auth_manager):
    """E2E: Account deletion process"""
    password = "DeleteP@sW9D!"
    
    # Step 1: Register user
    auth_manager.register_user(
        username="delete_user",
        password=password,
        email="delete@test.com"
    )
    
    # Step 2: Verify user exists
    assert "delete_user" in auth_manager.users
    
    # Step 3: Delete account
    del auth_manager.users["delete_user"]
    
    # Step 4: Verify user deleted
    assert "delete_user" not in auth_manager.users
    
    # Step 5: Cannot authenticate deleted user
    result = auth_manager.authenticate("delete_user", password)
    assert result["success"] is False


# ==================== Rate Limiting Flow ====================

def test_e2e_rate_limiting_flow():
    """E2E: Rate limiting on authentication attempts"""
    limiter = RateLimiter()
    
    # Allow first 5 attempts
    for i in range(5):
        allowed = limiter.is_allowed("rate_user", max_requests=5, window_seconds=60)
        assert allowed is True
    
    # 6th attempt should be blocked
    blocked = limiter.is_allowed("rate_user", max_requests=5, window_seconds=60)
    assert blocked is False
    
    # Reset and verify
    limiter.reset("rate_user")
    allowed = limiter.is_allowed("rate_user", max_requests=5, window_seconds=60)
    assert allowed is True


# ==================== Audit Logging Flow ====================

def test_e2e_authentication_audit_trail(auth_manager, temp_dir):
    """E2E: Complete authentication with audit trail"""
    logger = AuditLogger(log_dir=temp_dir)
    password = "AuditP@sW9D!"
    
    # Step 1: Register user
    auth_manager.register_user(
        username="audit_user",
        password=password,
        email="audit@test.com"
    )
    logger.log_event(
        event_type="user_registration",
        user="audit_user",
        action="register",
        resource="user_account"
    )
    
    # Step 2: Failed login attempt
    auth_manager.authenticate("audit_user", "WrongP@ss")
    logger.log_auth_attempt("audit_user", success=False, ip="192.168.1.1")
    
    # Step 3: Successful login
    result = auth_manager.authenticate("audit_user", password)
    logger.log_auth_attempt("audit_user", success=True, ip="192.168.1.1")
    
    # Step 4: Verify audit log exists
    assert logger.log_file.exists()
    log_content = logger.log_file.read_text()
    assert "audit_user" in log_content
    assert "user_registration" in log_content
    assert "authentication" in log_content


# ==================== Complete Multi-Step Flow ====================

def test_e2e_complete_user_journey(auth_manager, temp_dir):
    """E2E: Complete user journey from registration to deletion"""
    logger = AuditLogger(log_dir=temp_dir)
    password = "JourneyP@sW9D!"
    
    # Step 1: Password validation
    is_valid, errors = PasswordValidator.validate(password)
    assert is_valid
    
    # Step 2: Register
    auth_manager.register_user(
        username="journey_user",
        password=password,
        email="journey@test.com"
    )
    logger.log_event("user_registration", "journey_user", "register", "account")
    
    # Step 3: First login
    result1 = auth_manager.authenticate("journey_user", password)
    assert result1["success"] is True
    token1 = result1["session_token"]
    logger.log_auth_attempt("journey_user", success=True)
    
    # Step 4: Enable MFA
    uri = auth_manager.enable_mfa("journey_user")
    secret = auth_manager.users["journey_user"]["mfa_secret"]
    logger.log_event("mfa_enabled", "journey_user", "enable_mfa", "security")
    
    # Step 5: Login with MFA
    totp = pyotp.TOTP(secret)
    result2 = auth_manager.authenticate(
        "journey_user",
        password,
        mfa_code=totp.now()
    )
    assert result2["success"] is True
    token2 = result2["session_token"]
    
    # Step 6: Verify session
    session = auth_manager.verify_session(token2)
    assert session["username"] == "journey_user"
    
    # Step 7: Data export
    import json
    user = auth_manager.users["journey_user"]
    export_file = Path(temp_dir) / "journey_user_export.json"
    with open(export_file, 'w') as f:
        json.dump({
            "username": user["username"],
            "email": user["email"],
            "mfa_enabled": user["mfa_enabled"]
        }, f)
    assert export_file.exists()
    
    # Step 8: Revoke session
    auth_manager.revoke_session(token2)
    
    # Step 9: Account deletion
    del auth_manager.users["journey_user"]
    assert "journey_user" not in auth_manager.users
    
    # Step 10: Verify audit trail
    log_content = logger.log_file.read_text()
    assert "journey_user" in log_content
    assert "user_registration" in log_content
    assert "mfa_enabled" in log_content

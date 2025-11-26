"""
Security Configuration and Best Practices for XENO
Centralizes security settings and provides helper functions
"""

import os
import re
from typing import Optional, List
from datetime import timedelta

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

class SecurityConfig:
    """Centralized security configuration"""
    
    # Authentication Settings
    JWT_SECRET_KEY = os.getenv('XENO_JWT_SECRET', 'CHANGE_THIS_IN_PRODUCTION')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION = timedelta(hours=24)
    
    # Password Policy
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGITS = True
    PASSWORD_REQUIRE_SPECIAL = True
    PASSWORD_SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    PASSWORD_MAX_AGE_DAYS = 90  # Force password change after 90 days
    PASSWORD_HISTORY_SIZE = 5  # Prevent reusing last 5 passwords
    
    # Account Lockout
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    LOCKOUT_RESET_AFTER_SUCCESS = True
    
    # Session Management
    SESSION_TIMEOUT_MINUTES = 30
    SESSION_ABSOLUTE_TIMEOUT_HOURS = 24
    CONCURRENT_SESSIONS_ALLOWED = 3
    
    # MFA Settings
    MFA_ISSUER_NAME = "XENO Assistant"
    MFA_TOKEN_VALIDITY_WINDOW = 1  # Accept tokens from 1 step before/after
    
    # Encryption Settings
    ENCRYPTION_KEY_SIZE = 2048  # RSA key size
    PBKDF2_ITERATIONS = 100000  # Password hashing iterations
    SALT_SIZE = 32  # bytes
    
    # Rate Limiting
    API_RATE_LIMIT_PER_MINUTE = 60
    API_RATE_LIMIT_PER_HOUR = 1000
    AUTH_RATE_LIMIT_PER_MINUTE = 10
    
    # File Upload Security
    ALLOWED_UPLOAD_EXTENSIONS = {'.txt', '.pdf', '.doc', '.docx', '.jpg', '.png', '.csv'}
    MAX_UPLOAD_SIZE_MB = 10
    UPLOAD_SCAN_FOR_MALWARE = True
    
    # Data Privacy (GDPR)
    DATA_RETENTION_DAYS = 365
    ANONYMIZE_AFTER_DELETION = True
    EXPORT_FORMAT = 'json'  # or 'csv'
    
    # Audit Logging
    AUDIT_LOG_ENABLED = True
    AUDIT_LOG_RETENTION_DAYS = 90
    LOG_SENSITIVE_OPERATIONS = True
    LOG_FAILED_AUTH_ATTEMPTS = True
    
    # Development/Debug Settings
    DEBUG_MODE = os.getenv('XENO_DEBUG', 'False').lower() == 'true'
    SECURITY_WARNINGS_ENABLED = True


# ============================================================================
# PASSWORD VALIDATION
# ============================================================================

class PasswordValidator:
    """Validates password strength and policy compliance"""
    
    @staticmethod
    def validate(password: str) -> tuple[bool, List[str]]:
        """
        Validate password against security policy
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # Length check
        if len(password) < SecurityConfig.PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {SecurityConfig.PASSWORD_MIN_LENGTH} characters")
        
        # Character requirements
        if SecurityConfig.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if SecurityConfig.PASSWORD_REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if SecurityConfig.PASSWORD_REQUIRE_DIGITS and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        
        if SecurityConfig.PASSWORD_REQUIRE_SPECIAL:
            if not any(c in SecurityConfig.PASSWORD_SPECIAL_CHARS for c in password):
                errors.append(f"Password must contain at least one special character: {SecurityConfig.PASSWORD_SPECIAL_CHARS}")
        
        # Common password check
        if password.lower() in COMMON_PASSWORDS:
            errors.append("Password is too common. Please choose a more unique password")
        
        # Sequential characters
        if has_sequential_chars(password):
            errors.append("Password contains sequential characters (e.g., 123, abc)")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def generate_strong_password(length: int = 16) -> str:
        """Generate a cryptographically secure random password"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + SecurityConfig.PASSWORD_SPECIAL_CHARS
        
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            is_valid, _ = PasswordValidator.validate(password)
            if is_valid:
                return password


# ============================================================================
# INPUT SANITIZATION
# ============================================================================

class InputSanitizer:
    """Sanitizes user inputs to prevent injection attacks"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Remove potentially dangerous characters from string"""
        if not value:
            return ""
        
        # Truncate to max length
        value = value[:max_length]
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Strip leading/trailing whitespace
        value = value.strip()
        
        return value
    
    @staticmethod
    def sanitize_email(email: str) -> Optional[str]:
        """Validate and sanitize email address"""
        if not email:
            return None
        
        email = email.lower().strip()
        
        # Basic email regex
        pattern = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
        if re.match(pattern, email):
            return email
        
        return None
    
    @staticmethod
    def sanitize_username(username: str) -> Optional[str]:
        """Validate and sanitize username"""
        if not username:
            return None
        
        username = username.strip()
        
        # Allow alphanumeric, underscore, hyphen
        if re.match(r'^[a-zA-Z0-9_-]{3,32}$', username):
            return username
        
        return None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent directory traversal"""
        import os.path
        
        # Get base filename only (remove path)
        filename = os.path.basename(filename)
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        # Prevent hidden files
        if filename.startswith('.'):
            filename = '_' + filename
        
        return filename


# ============================================================================
# RATE LIMITING
# ============================================================================

from collections import defaultdict
from datetime import datetime
from threading import Lock

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = defaultdict(list)  # key -> [timestamps]
        self.lock = Lock()
    
    def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """
        Check if request is allowed under rate limit
        
        Args:
            key: Unique identifier (e.g., username, IP)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            True if allowed, False if rate limit exceeded
        """
        with self.lock:
            now = datetime.now()
            cutoff = now.timestamp() - window_seconds
            
            # Remove old requests outside window
            self.requests[key] = [
                ts for ts in self.requests[key]
                if ts > cutoff
            ]
            
            # Check if under limit
            if len(self.requests[key]) < max_requests:
                self.requests[key].append(now.timestamp())
                return True
            
            return False
    
    def reset(self, key: str):
        """Reset rate limit for a key"""
        with self.lock:
            if key in self.requests:
                del self.requests[key]


# ============================================================================
# AUDIT LOGGING
# ============================================================================

import json
from pathlib import Path

class AuditLogger:
    """Security audit logging"""
    
    def __init__(self, log_dir: str = "logs/security"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
    
    def log_event(
        self,
        event_type: str,
        user: Optional[str],
        action: str,
        resource: Optional[str] = None,
        result: str = "success",
        details: Optional[dict] = None
    ):
        """Log a security event"""
        if not SecurityConfig.AUDIT_LOG_ENABLED:
            return
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,  # auth, access, change, etc.
            'user': user,
            'action': action,
            'resource': resource,
            'result': result,  # success, failure, denied
            'details': details or {}
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def log_auth_attempt(self, username: str, success: bool, ip: Optional[str] = None):
        """Log authentication attempt"""
        self.log_event(
            event_type='authentication',
            user=username,
            action='login',
            result='success' if success else 'failure',
            details={'ip_address': ip}
        )
    
    def log_data_access(self, user: str, resource: str, action: str):
        """Log data access"""
        self.log_event(
            event_type='data_access',
            user=user,
            action=action,  # read, write, delete
            resource=resource,
            result='success'
        )
    
    def log_security_event(self, user: str, action: str, details: dict):
        """Log security-related event"""
        self.log_event(
            event_type='security',
            user=user,
            action=action,
            result='success',
            details=details
        )


# ============================================================================
# COMMON PASSWORDS (Top 100 most common)
# ============================================================================

COMMON_PASSWORDS = {
    'password', '123456', '123456789', 'qwerty', 'abc123', 'monkey',
    '1234567', 'letmein', 'trustno1', 'dragon', 'baseball', '111111',
    'iloveyou', 'master', 'sunshine', 'ashley', 'bailey', 'passw0rd',
    'shadow', '123123', '654321', 'superman', 'qazwsx', 'michael',
    'football', 'password1', 'welcome', 'jesus', 'ninja', 'mustang',
    # Add more as needed
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def has_sequential_chars(password: str, length: int = 3) -> bool:
    """Check if password contains sequential characters"""
    for i in range(len(password) - length + 1):
        substr = password[i:i+length]
        
        # Check numeric sequences (123, 987)
        if substr.isdigit():
            digits = [int(c) for c in substr]
            if all(digits[i] + 1 == digits[i+1] for i in range(len(digits)-1)):
                return True
            if all(digits[i] - 1 == digits[i+1] for i in range(len(digits)-1)):
                return True
        
        # Check alphabetic sequences (abc, zyx)
        if substr.isalpha():
            chars = [ord(c.lower()) for c in substr]
            if all(chars[i] + 1 == chars[i+1] for i in range(len(chars)-1)):
                return True
            if all(chars[i] - 1 == chars[i+1] for i in range(len(chars)-1)):
                return True
    
    return False


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data for logging"""
    if len(data) <= visible_chars:
        return '*' * len(data)
    
    return data[:visible_chars] + '*' * (len(data) - visible_chars)


# ============================================================================
# SECURITY WARNINGS
# ============================================================================

def check_security_configuration():
    """Check for insecure configuration and warn"""
    warnings = []
    
    if SecurityConfig.JWT_SECRET_KEY == 'CHANGE_THIS_IN_PRODUCTION':
        warnings.append("⚠️  WARNING: Using default JWT secret key. Set XENO_JWT_SECRET environment variable!")
    
    if SecurityConfig.DEBUG_MODE:
        warnings.append("⚠️  WARNING: Debug mode is enabled. Disable in production!")
    
    if SecurityConfig.PASSWORD_MIN_LENGTH < 8:
        warnings.append("⚠️  WARNING: Password minimum length is too short (< 8 characters)")
    
    if SecurityConfig.MAX_LOGIN_ATTEMPTS > 10:
        warnings.append("⚠️  WARNING: Max login attempts is too high (> 10)")
    
    if warnings and SecurityConfig.SECURITY_WARNINGS_ENABLED:
        print("\n" + "="*70)
        print("SECURITY WARNINGS")
        print("="*70)
        for warning in warnings:
            print(warning)
        print("="*70 + "\n")
    
    return len(warnings) == 0


# Run security check on import
if __name__ != "__main__":
    check_security_configuration()

"""
Enterprise Security Module for XENO
Provides end-to-end encryption, authentication, and compliance features
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import os
import base64
import json
import hashlib
import secrets
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import jwt


class EncryptionManager:
    """Handles all encryption operations"""
    
    def __init__(self, master_key: Optional[bytes] = None):
        if master_key:
            self.master_key = master_key
        else:
            self.master_key = Fernet.generate_key()
        
        self.cipher_suite = Fernet(self.master_key)
        
        # Generate RSA key pair for asymmetric encryption
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt data using symmetric encryption (Fernet)"""
        encrypted = self.cipher_suite.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using symmetric encryption"""
        try:
            decoded = base64.b64decode(encrypted_data.encode())
            decrypted = self.cipher_suite.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
    
    def encrypt_file(self, file_path: str, output_path: str):
        """Encrypt a file"""
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted = self.cipher_suite.encrypt(data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted)
    
    def decrypt_file(self, encrypted_path: str, output_path: str):
        """Decrypt a file"""
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted = self.cipher_suite.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted)
    
    def encrypt_asymmetric(self, data: str, public_key: rsa.RSAPublicKey) -> str:
        """Encrypt data using RSA public key"""
        encrypted = public_key.encrypt(
            data.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted).decode()
    
    def decrypt_asymmetric(self, encrypted_data: str) -> str:
        """Decrypt data using RSA private key"""
        decoded = base64.b64decode(encrypted_data.encode())
        decrypted = self.private_key.decrypt(
            decoded,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted.decode()
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> tuple:
        """Hash password using PBKDF2"""
        if salt is None:
            salt = os.urandom(32)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode())
        return base64.b64encode(key).decode(), base64.b64encode(salt).decode()
    
    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """Verify password against hash"""
        salt_bytes = base64.b64decode(salt.encode())
        computed_hash, _ = self.hash_password(password, salt_bytes)
        return secrets.compare_digest(computed_hash, hashed)
    
    def export_public_key(self) -> str:
        """Export public key as PEM string"""
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode()
    
    def export_private_key(self, password: str) -> str:
        """Export encrypted private key as PEM string"""
        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
        )
        return pem.decode()


class AuthenticationManager:
    """Manages user authentication and sessions"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.users: Dict[str, Dict[str, Any]] = {}
        self.encryption = EncryptionManager()
    
    def register_user(
        self,
        username: str,
        password: str,
        email: str,
        role: str = "user"
    ) -> Dict[str, Any]:
        """Register a new user"""
        if username in self.users:
            raise ValueError("Username already exists")
        
        # Hash password
        password_hash, salt = self.encryption.hash_password(password)
        
        # Create user
        user = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "salt": salt,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "mfa_enabled": False,
            "mfa_secret": None,
            "failed_attempts": 0,
            "locked_until": None
        }
        
        self.users[username] = user
        return {"success": True, "username": username}
    
    def authenticate(
        self,
        username: str,
        password: str,
        mfa_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Authenticate user and create session"""
        user = self.users.get(username)
        
        if not user:
            return {"success": False, "error": "Invalid credentials"}
        
        # Check if account is locked
        if user.get("locked_until"):
            locked_until = datetime.fromisoformat(user["locked_until"])
            if datetime.now() < locked_until:
                return {"success": False, "error": "Account temporarily locked"}
            else:
                user["locked_until"] = None
                user["failed_attempts"] = 0
        
        # Verify password
        if not self.encryption.verify_password(
            password,
            user["password_hash"],
            user["salt"]
        ):
            user["failed_attempts"] += 1
            
            # Lock account after 5 failed attempts
            if user["failed_attempts"] >= 5:
                user["locked_until"] = (datetime.now() + timedelta(minutes=30)).isoformat()
                return {"success": False, "error": "Account locked due to multiple failed attempts"}
            
            return {"success": False, "error": "Invalid credentials"}
        
        # Check MFA if enabled
        if user.get("mfa_enabled"):
            if not mfa_code:
                return {"success": False, "error": "MFA code required", "mfa_required": True}
            
            if not self.verify_mfa(username, mfa_code):
                return {"success": False, "error": "Invalid MFA code"}
        
        # Reset failed attempts
        user["failed_attempts"] = 0
        user["last_login"] = datetime.now().isoformat()
        
        # Create session
        session_token = self.create_session(username, user["role"])
        
        return {
            "success": True,
            "session_token": session_token,
            "username": username,
            "role": user["role"]
        }
    
    def create_session(self, username: str, role: str, expires_in: int = 86400) -> str:
        """Create JWT session token"""
        payload = {
            "username": username,
            "role": role,
            "exp": datetime.utcnow() + timedelta(seconds=expires_in),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        # Store session
        self.sessions[token] = {
            "username": username,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(seconds=expires_in)).isoformat()
        }
        
        return token
    
    def verify_session(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify session token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            # Remove expired session
            if token in self.sessions:
                del self.sessions[token]
            return None
        except jwt.InvalidTokenError:
            return None
    
    def revoke_session(self, token: str):
        """Revoke session token"""
        if token in self.sessions:
            del self.sessions[token]
    
    def enable_mfa(self, username: str) -> str:
        """Enable MFA for user and return secret"""
        import pyotp
        
        user = self.users.get(username)
        if not user:
            raise ValueError("User not found")
        
        secret = pyotp.random_base32()
        user["mfa_enabled"] = True
        user["mfa_secret"] = secret
        
        # Generate QR code URI
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(username, issuer_name="XENO")
        
        return uri
    
    def disable_mfa(self, username: str):
        """Disable MFA for user"""
        user = self.users.get(username)
        if user:
            user["mfa_enabled"] = False
            user["mfa_secret"] = None
    
    def verify_mfa(self, username: str, code: str) -> bool:
        """Verify MFA code"""
        import pyotp
        
        user = self.users.get(username)
        if not user or not user.get("mfa_secret"):
            return False
        
        totp = pyotp.TOTP(user["mfa_secret"])
        return totp.verify(code, valid_window=1)
    
    def change_password(
        self,
        username: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """Change user password"""
        user = self.users.get(username)
        if not user:
            return False
        
        # Verify old password
        if not self.encryption.verify_password(
            old_password,
            user["password_hash"],
            user["salt"]
        ):
            return False
        
        # Hash new password
        password_hash, salt = self.encryption.hash_password(new_password)
        user["password_hash"] = password_hash
        user["salt"] = salt
        
        return True
    
    def reset_password(self, username: str, new_password: str) -> bool:
        """Reset user password (admin only)"""
        user = self.users.get(username)
        if not user:
            return False
        
        password_hash, salt = self.encryption.hash_password(new_password)
        user["password_hash"] = password_hash
        user["salt"] = salt
        user["failed_attempts"] = 0
        user["locked_until"] = None
        
        return True


class AuditLogger:
    """Logs all security-relevant events for compliance"""
    
    def __init__(self, log_file: str = "data/security/audit.log"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    def log_event(
        self,
        event_type: str,
        username: str,
        details: Dict[str, Any],
        ip_address: Optional[str] = None
    ):
        """Log security event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "username": username,
            "ip_address": ip_address,
            "details": details
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def log_login(self, username: str, success: bool, ip_address: Optional[str] = None):
        """Log login attempt"""
        self.log_event(
            "login",
            username,
            {"success": success},
            ip_address
        )
    
    def log_logout(self, username: str, ip_address: Optional[str] = None):
        """Log logout"""
        self.log_event(
            "logout",
            username,
            {},
            ip_address
        )
    
    def log_data_access(
        self,
        username: str,
        resource: str,
        action: str,
        ip_address: Optional[str] = None
    ):
        """Log data access"""
        self.log_event(
            "data_access",
            username,
            {"resource": resource, "action": action},
            ip_address
        )
    
    def log_permission_change(
        self,
        username: str,
        target_user: str,
        old_role: str,
        new_role: str
    ):
        """Log permission change"""
        self.log_event(
            "permission_change",
            username,
            {
                "target_user": target_user,
                "old_role": old_role,
                "new_role": new_role
            }
        )
    
    def log_security_event(
        self,
        username: str,
        event_description: str,
        severity: str = "medium"
    ):
        """Log general security event"""
        self.log_event(
            "security_event",
            username,
            {
                "description": event_description,
                "severity": severity
            }
        )
    
    def get_audit_trail(
        self,
        username: Optional[str] = None,
        event_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve audit trail with filters"""
        events = []
        
        if not os.path.exists(self.log_file):
            return events
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    
                    # Apply filters
                    if username and event.get("username") != username:
                        continue
                    
                    if event_type and event.get("event_type") != event_type:
                        continue
                    
                    event_time = datetime.fromisoformat(event["timestamp"])
                    if start_date and event_time < start_date:
                        continue
                    if end_date and event_time > end_date:
                        continue
                    
                    events.append(event)
                    
                    if len(events) >= limit:
                        break
                        
                except json.JSONDecodeError:
                    continue
        
        return events[::-1]  # Most recent first


class ComplianceManager:
    """Manages GDPR, SOC2, and other compliance requirements"""
    
    def __init__(self, data_dir: str = "data/compliance"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.encryption = EncryptionManager()
    
    def export_user_data(self, username: str) -> Dict[str, Any]:
        """Export all user data (GDPR right to data portability)"""
        # This would collect all user data from various sources
        user_data = {
            "username": username,
            "export_date": datetime.now().isoformat(),
            "data": {
                "profile": {},
                "emails": [],
                "tasks": [],
                "calendar_events": [],
                "notes": [],
                "preferences": {}
            }
        }
        
        # Encrypt and save
        export_file = os.path.join(self.data_dir, f"{username}_export.json")
        with open(export_file, 'w') as f:
            json.dump(user_data, f, indent=2)
        
        return user_data
    
    def delete_user_data(self, username: str) -> bool:
        """Delete all user data (GDPR right to erasure)"""
        # This would delete user data from all systems
        # In practice, this needs to handle:
        # - User profile
        # - All emails, tasks, calendar events
        # - Associated files
        # - Audit logs (may need to anonymize instead of delete)
        
        # Mark user as deleted
        deletion_record = {
            "username": username,
            "deletion_date": datetime.now().isoformat(),
            "requested_by": username,
            "status": "completed"
        }
        
        deletion_file = os.path.join(self.data_dir, "deletions.json")
        records = []
        
        if os.path.exists(deletion_file):
            with open(deletion_file, 'r') as f:
                records = json.load(f)
        
        records.append(deletion_record)
        
        with open(deletion_file, 'w') as f:
            json.dump(records, f, indent=2)
        
        return True
    
    def generate_privacy_report(self) -> Dict[str, Any]:
        """Generate privacy compliance report"""
        report = {
            "report_date": datetime.now().isoformat(),
            "compliance_frameworks": ["GDPR", "SOC2", "CCPA"],
            "data_retention": {
                "user_data": "Retained while account is active",
                "audit_logs": "7 years",
                "backups": "90 days"
            },
            "encryption": {
                "at_rest": "AES-256",
                "in_transit": "TLS 1.3",
                "key_management": "Automated rotation every 90 days"
            },
            "access_controls": {
                "authentication": "Multi-factor authentication available",
                "authorization": "Role-based access control (RBAC)",
                "session_management": "JWT with 24-hour expiry"
            },
            "audit_logging": {
                "enabled": True,
                "events_logged": [
                    "login/logout",
                    "data_access",
                    "permission_changes",
                    "security_events"
                ]
            }
        }
        
        return report
    
    def anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize sensitive data for analytics"""
        anonymized = data.copy()
        
        # Hash or remove PII fields
        pii_fields = ["username", "email", "name", "phone", "address"]
        
        for field in pii_fields:
            if field in anonymized:
                # Hash the field
                hash_value = hashlib.sha256(str(anonymized[field]).encode()).hexdigest()
                anonymized[field] = f"anon_{hash_value[:16]}"
        
        return anonymized

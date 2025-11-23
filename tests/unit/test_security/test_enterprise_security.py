"""
Unit Tests for Enterprise Security Module
Tests encryption, authentication, and security features
"""
import pytest
from src.security.enterprise_security import EncryptionManager, AuthenticationManager


class TestEncryptionManager:
    """Test suite for EncryptionManager class"""
    
    @pytest.fixture
    def encryption(self):
        """Fixture to create a fresh EncryptionManager instance"""
        return EncryptionManager()
    
    def test_initialization(self, encryption):
        """Test that encryption manager initializes correctly"""
        assert encryption is not None
        assert hasattr(encryption, 'encrypt_data')
        assert hasattr(encryption, 'decrypt_data')
    
    def test_encrypt_decrypt_data(self, encryption):
        """Test data encryption and decryption"""
        original_data = "sensitive_information_12345"
        
        # Encrypt data
        encrypted = encryption.encrypt_data(original_data)
        assert encrypted != original_data
        assert encrypted is not None
        
        # Decrypt data
        decrypted = encryption.decrypt_data(encrypted)
        assert decrypted == original_data
    
    def test_encrypt_empty_string(self, encryption):
        """Test encrypting empty string"""
        encrypted = encryption.encrypt_data("")
        assert encrypted is not None
        
        decrypted = encryption.decrypt_data(encrypted)
        assert decrypted == ""
    
    def test_encrypt_large_data(self, encryption):
        """Test encrypting large data"""
        large_data = "A" * 10000  # 10KB of data
        
        encrypted = encryption.encrypt_data(large_data)
        decrypted = encryption.decrypt_data(encrypted)
        
        assert decrypted == large_data
    
    def test_hash_password(self, encryption):
        """Test password hashing"""
        password = "SecurePassword123!"
        
        hashed, salt = encryption.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert salt is not None
    
    def test_verify_password(self, encryption):
        """Test password verification"""
        password = "MyPassword456"
        
        hashed, salt = encryption.hash_password(password)
        
        # Correct password should verify
        assert encryption.verify_password(password, hashed, salt) is True
        
        # Incorrect password should fail
        assert encryption.verify_password("WrongPassword", hashed, salt) is False
    
    def test_password_hash_uniqueness(self, encryption):
        """Test that same password generates different hashes (salt)"""
        password = "TestPassword789"
        
        hash1, salt1 = encryption.hash_password(password)
        hash2, salt2 = encryption.hash_password(password)
        
        # Hashes should be different due to different salt
        assert hash1 != hash2
        assert salt1 != salt2
        
        # But both should verify correctly
        assert encryption.verify_password(password, hash1, salt1) is True
        assert encryption.verify_password(password, hash2, salt2) is True


class TestAuthenticationManager:
    """Test suite for AuthenticationManager class"""
    
    @pytest.fixture
    def auth(self):
        """Fixture to create a fresh AuthenticationManager instance"""
        return AuthenticationManager(secret_key="test_secret_key_12345")
    
    def test_initialization(self, auth):
        """Test that authentication manager initializes correctly"""
        assert auth is not None
        assert hasattr(auth, 'register_user')
        assert hasattr(auth, 'authenticate')
    
    def test_register_user(self, auth):
        """Test user registration"""
        result = auth.register_user(
            username="testuser",
            password="TestPass123!",
            email="test@example.com"
        )
        
        assert result['success'] is True
        assert result['username'] == "testuser"
    
    def test_register_duplicate_user(self, auth):
        """Test that duplicate usernames are rejected"""
        auth.register_user("alice", "Pass123!", "alice@example.com")
        
        with pytest.raises(ValueError, match="already exists"):
            auth.register_user("alice", "Pass456!", "alice2@example.com")
    
    def test_authenticate_user(self, auth):
        """Test user authentication"""
        username = "bob"
        password = "SecurePass456!"
        
        # Register user
        auth.register_user(username, password, "bob@example.com")
        
        # Authenticate with correct password
        result = auth.authenticate(username, password)
        assert result['success'] is True
    
    def test_authenticate_wrong_password(self, auth):
        """Test authentication with wrong password"""
        username = "charlie"
        password = "CorrectPass789!"
        
        auth.register_user(username, password, "charlie@example.com")
        
        # Authenticate with wrong password
        result = auth.authenticate(username, "WrongPassword")
        assert result['success'] is False


@pytest.mark.integration
def test_full_authentication_flow():
    """Integration test: Complete authentication workflow"""
    auth = AuthenticationManager(secret_key="integration_test_secret")
    
    # Step 1: User registration
    username = "alice"
    password = "SecurePass123!"
    email = "alice@example.com"
    
    # Register user
    result = auth.register_user(username, password, email)
    assert result['success'] is True
    
    # Step 2: User login
    # Authenticate with correct credentials
    auth_result = auth.authenticate(username, password)
    assert auth_result['success'] is True
    
    # Step 3: Test encryption
    encryption = EncryptionManager()
    
    # Encrypt sensitive data
    sensitive_data = "User's private information"
    encrypted = encryption.encrypt_data(sensitive_data)
    
    # Decrypt when needed
    decrypted = encryption.decrypt_data(encrypted)
    assert decrypted == sensitive_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Single Sign-On (SSO) Integration for XENO
Supports OAuth2, SAML, and OIDC protocols
"""

import aiohttp
import secrets
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs, urlparse
import base64
import hashlib


class SSOProvider:
    """Base class for SSO providers"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state_store: Dict[str, Any] = {}
    
    async def get_authorization_url(self) -> Dict[str, str]:
        """Get authorization URL for OAuth flow"""
        raise NotImplementedError
    
    async def exchange_code(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        raise NotImplementedError
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from provider"""
        raise NotImplementedError
    
    def generate_state(self) -> str:
        """Generate random state for CSRF protection"""
        state = secrets.token_urlsafe(32)
        self.state_store[state] = {
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=10)).isoformat()
        }
        return state
    
    def verify_state(self, state: str) -> bool:
        """Verify state token"""
        if state not in self.state_store:
            return False
        
        state_data = self.state_store[state]
        expires_at = datetime.fromisoformat(state_data["expires_at"])
        
        if datetime.now() > expires_at:
            del self.state_store[state]
            return False
        
        del self.state_store[state]
        return True


class GoogleSSOProvider(SSOProvider):
    """Google OAuth2 SSO provider"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        super().__init__(client_id, client_secret, redirect_uri)
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        self.scopes = ["openid", "email", "profile"]
    
    async def get_authorization_url(self) -> Dict[str, str]:
        """Get Google OAuth authorization URL"""
        state = self.generate_state()
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        
        url = f"{self.auth_url}?{urlencode(params)}"
        
        return {
            "url": url,
            "state": state
        }
    
    async def exchange_code(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange code for access token"""
        if not self.verify_state(state):
            raise ValueError("Invalid state token")
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.token_url, data=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Token exchange failed: {await response.text()}")
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from Google"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.userinfo_url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"User info fetch failed: {await response.text()}")


class MicrosoftSSOProvider(SSOProvider):
    """Microsoft Azure AD OAuth2 SSO provider"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, tenant: str = "common"):
        super().__init__(client_id, client_secret, redirect_uri)
        self.tenant = tenant
        self.auth_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
        self.token_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
        self.userinfo_url = "https://graph.microsoft.com/v1.0/me"
        self.scopes = ["openid", "email", "profile", "User.Read"]
    
    async def get_authorization_url(self) -> Dict[str, str]:
        """Get Microsoft OAuth authorization URL"""
        state = self.generate_state()
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
            "response_mode": "query"
        }
        
        url = f"{self.auth_url}?{urlencode(params)}"
        
        return {
            "url": url,
            "state": state
        }
    
    async def exchange_code(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange code for access token"""
        if not self.verify_state(state):
            raise ValueError("Invalid state token")
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.token_url, data=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Token exchange failed: {await response.text()}")
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from Microsoft Graph"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.userinfo_url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"User info fetch failed: {await response.text()}")


class OktaSSOProvider(SSOProvider):
    """Okta OIDC SSO provider"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, okta_domain: str):
        super().__init__(client_id, client_secret, redirect_uri)
        self.okta_domain = okta_domain
        self.auth_url = f"https://{okta_domain}/oauth2/v1/authorize"
        self.token_url = f"https://{okta_domain}/oauth2/v1/token"
        self.userinfo_url = f"https://{okta_domain}/oauth2/v1/userinfo"
        self.scopes = ["openid", "email", "profile"]
    
    async def get_authorization_url(self) -> Dict[str, str]:
        """Get Okta authorization URL"""
        state = self.generate_state()
        nonce = secrets.token_urlsafe(32)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
            "nonce": nonce
        }
        
        url = f"{self.auth_url}?{urlencode(params)}"
        
        return {
            "url": url,
            "state": state,
            "nonce": nonce
        }
    
    async def exchange_code(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange code for access token"""
        if not self.verify_state(state):
            raise ValueError("Invalid state token")
        
        auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}
        
        data = {
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.token_url, data=data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Token exchange failed: {await response.text()}")
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from Okta"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.userinfo_url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"User info fetch failed: {await response.text()}")


class SSOManager:
    """Manages SSO providers and authentication flow"""
    
    def __init__(self):
        self.providers: Dict[str, SSOProvider] = {}
    
    def register_provider(self, name: str, provider: SSOProvider):
        """Register SSO provider"""
        self.providers[name] = provider
    
    def get_provider(self, name: str) -> Optional[SSOProvider]:
        """Get SSO provider by name"""
        return self.providers.get(name)
    
    async def initiate_login(self, provider_name: str) -> Dict[str, str]:
        """Initiate SSO login flow"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider {provider_name} not found")
        
        return await provider.get_authorization_url()
    
    async def handle_callback(
        self,
        provider_name: str,
        code: str,
        state: str
    ) -> Dict[str, Any]:
        """Handle SSO callback"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider {provider_name} not found")
        
        # Exchange code for token
        token_data = await provider.exchange_code(code, state)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise ValueError("No access token in response")
        
        # Get user info
        user_info = await provider.get_user_info(access_token)
        
        return {
            "provider": provider_name,
            "access_token": access_token,
            "refresh_token": token_data.get("refresh_token"),
            "expires_in": token_data.get("expires_in"),
            "user_info": user_info
        }


class RBACManager:
    """Role-Based Access Control manager"""
    
    def __init__(self):
        # Define roles and their permissions
        self.roles: Dict[str, Dict[str, Any]] = {
            "admin": {
                "description": "Full system access",
                "permissions": [
                    "user.create",
                    "user.read",
                    "user.update",
                    "user.delete",
                    "role.assign",
                    "settings.modify",
                    "data.export",
                    "audit.view",
                    "integration.manage"
                ]
            },
            "manager": {
                "description": "Team management access",
                "permissions": [
                    "user.read",
                    "user.update",
                    "data.export",
                    "team.manage",
                    "workflow.create",
                    "workflow.delete"
                ]
            },
            "user": {
                "description": "Standard user access",
                "permissions": [
                    "profile.read",
                    "profile.update",
                    "email.send",
                    "task.create",
                    "calendar.manage",
                    "workflow.create"
                ]
            },
            "viewer": {
                "description": "Read-only access",
                "permissions": [
                    "profile.read",
                    "data.read"
                ]
            }
        }
        
        # User role assignments
        self.user_roles: Dict[str, str] = {}
    
    def assign_role(self, username: str, role: str) -> bool:
        """Assign role to user"""
        if role not in self.roles:
            return False
        
        self.user_roles[username] = role
        return True
    
    def get_user_role(self, username: str) -> Optional[str]:
        """Get user's role"""
        return self.user_roles.get(username)
    
    def get_user_permissions(self, username: str) -> List[str]:
        """Get user's permissions"""
        role = self.get_user_role(username)
        if not role or role not in self.roles:
            return []
        
        return self.roles[role]["permissions"]
    
    def has_permission(self, username: str, permission: str) -> bool:
        """Check if user has specific permission"""
        permissions = self.get_user_permissions(username)
        
        # Check exact permission
        if permission in permissions:
            return True
        
        # Check wildcard permission (e.g., "user.*" grants "user.read")
        permission_parts = permission.split(".")
        if len(permission_parts) == 2:
            wildcard = f"{permission_parts[0]}.*"
            if wildcard in permissions:
                return True
        
        return False
    
    def create_custom_role(
        self,
        role_name: str,
        description: str,
        permissions: List[str]
    ) -> bool:
        """Create custom role"""
        if role_name in self.roles:
            return False
        
        self.roles[role_name] = {
            "description": description,
            "permissions": permissions,
            "custom": True
        }
        
        return True
    
    def update_role_permissions(
        self,
        role_name: str,
        permissions: List[str]
    ) -> bool:
        """Update role permissions"""
        if role_name not in self.roles:
            return False
        
        # Don't allow modifying built-in roles
        if not self.roles[role_name].get("custom", False):
            return False
        
        self.roles[role_name]["permissions"] = permissions
        return True
    
    def delete_custom_role(self, role_name: str) -> bool:
        """Delete custom role"""
        if role_name not in self.roles:
            return False
        
        # Don't allow deleting built-in roles
        if not self.roles[role_name].get("custom", False):
            return False
        
        # Remove role from users
        for username in list(self.user_roles.keys()):
            if self.user_roles[username] == role_name:
                del self.user_roles[username]
        
        del self.roles[role_name]
        return True
    
    def list_roles(self) -> List[Dict[str, Any]]:
        """List all roles"""
        return [
            {
                "name": name,
                "description": role["description"],
                "permissions": role["permissions"],
                "custom": role.get("custom", False)
            }
            for name, role in self.roles.items()
        ]

"""
OAuth2 authentication helper for XENO AI Assistant.
Handles OAuth flows for Gmail, GitHub, and other services.
"""

import webbrowser
import http.server
import socketserver
import urllib.parse
from typing import Dict, Optional, Callable
import logging
import threading
import time

logger = logging.getLogger("XENO.OAuthHelper")


class OAuthHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callbacks."""
    
    auth_code = None
    auth_state = None
    
    def do_GET(self):
        """Handle GET request (OAuth callback)."""
        # Parse query parameters
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        # Extract authorization code
        if 'code' in params:
            OAuthHandler.auth_code = params['code'][0]
            OAuthHandler.auth_state = params.get('state', [None])[0]
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            success_html = """
            <html>
            <head><title>Authentication Successful</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>✅ Authentication Successful!</h1>
                <p>You can now close this window and return to XENO.</p>
                <script>setTimeout(() => window.close(), 3000);</script>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())
        else:
            # Send error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            error_html = """
            <html>
            <head><title>Authentication Failed</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>❌ Authentication Failed</h1>
                <p>Please try again.</p>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())
    
    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


class OAuthHelper:
    """Helper class for OAuth2 authentication flows."""
    
    def __init__(self, redirect_port: int = 8080):
        """
        Initialize OAuth helper.
        
        Args:
            redirect_port: Port for OAuth callback server
        """
        self.redirect_port = redirect_port
        self.redirect_uri = f"http://localhost:{redirect_port}/callback"
        self.server = None
        self.server_thread = None
        logger.info(f"OAuthHelper initialized with redirect URI: {self.redirect_uri}")
    
    def start_callback_server(self):
        """Start local HTTP server for OAuth callbacks."""
        try:
            self.server = socketserver.TCPServer(
                ("localhost", self.redirect_port),
                OAuthHandler
            )
            
            # Run server in background thread
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            logger.info(f"OAuth callback server started on port {self.redirect_port}")
            
        except Exception as e:
            logger.error(f"Failed to start callback server: {e}")
            raise
    
    def stop_callback_server(self):
        """Stop OAuth callback server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("OAuth callback server stopped")
    
    def authenticate_github(self, client_id: str, scopes: list = None) -> Optional[str]:
        """
        Authenticate with GitHub using OAuth.
        
        Args:
            client_id: GitHub OAuth app client ID
            scopes: List of permission scopes
            
        Returns:
            Authorization code if successful
        """
        try:
            if scopes is None:
                scopes = ['repo', 'user']
            
            # Build authorization URL
            scope_str = ' '.join(scopes)
            auth_url = (
                f"https://github.com/login/oauth/authorize"
                f"?client_id={client_id}"
                f"&redirect_uri={urllib.parse.quote(self.redirect_uri)}"
                f"&scope={urllib.parse.quote(scope_str)}"
                f"&state=github_auth"
            )
            
            # Reset auth code
            OAuthHandler.auth_code = None
            
            # Start callback server
            self.start_callback_server()
            
            # Open browser
            logger.info("Opening GitHub authorization page in browser...")
            webbrowser.open(auth_url)
            
            # Wait for callback
            timeout = 300  # 5 minutes
            start_time = time.time()
            
            while OAuthHandler.auth_code is None:
                if time.time() - start_time > timeout:
                    logger.error("OAuth timeout - no response received")
                    self.stop_callback_server()
                    return None
                time.sleep(0.5)
            
            auth_code = OAuthHandler.auth_code
            self.stop_callback_server()
            
            logger.info("GitHub authentication successful")
            return auth_code
            
        except Exception as e:
            logger.error(f"GitHub authentication failed: {e}")
            self.stop_callback_server()
            return None
    
    def authenticate_google(self, client_id: str, client_secret: str, 
                          scopes: list = None) -> Optional[Dict]:
        """
        Authenticate with Google using OAuth.
        
        Args:
            client_id: Google OAuth client ID
            client_secret: Google OAuth client secret
            scopes: List of permission scopes
            
        Returns:
            Credentials dictionary if successful
        """
        try:
            if scopes is None:
                scopes = [
                    'https://www.googleapis.com/auth/gmail.readonly',
                    'https://www.googleapis.com/auth/gmail.send',
                    'https://www.googleapis.com/auth/calendar'
                ]
            
            # Build authorization URL
            scope_str = ' '.join(scopes)
            auth_url = (
                f"https://accounts.google.com/o/oauth2/v2/auth"
                f"?client_id={client_id}"
                f"&redirect_uri={urllib.parse.quote(self.redirect_uri)}"
                f"&scope={urllib.parse.quote(scope_str)}"
                f"&response_type=code"
                f"&access_type=offline"
                f"&state=google_auth"
            )
            
            # Reset auth code
            OAuthHandler.auth_code = None
            
            # Start callback server
            self.start_callback_server()
            
            # Open browser
            logger.info("Opening Google authorization page in browser...")
            webbrowser.open(auth_url)
            
            # Wait for callback
            timeout = 300
            start_time = time.time()
            
            while OAuthHandler.auth_code is None:
                if time.time() - start_time > timeout:
                    logger.error("OAuth timeout - no response received")
                    self.stop_callback_server()
                    return None
                time.sleep(0.5)
            
            auth_code = OAuthHandler.auth_code
            self.stop_callback_server()
            
            logger.info("Google authentication successful")
            return {
                'code': auth_code,
                'client_id': client_id,
                'client_secret': client_secret
            }
            
        except Exception as e:
            logger.error(f"Google authentication failed: {e}")
            self.stop_callback_server()
            return None
    
    def open_github_token_page(self):
        """Open GitHub personal access token creation page."""
        try:
            url = "https://github.com/settings/tokens/new?description=XENO%20AI%20Assistant&scopes=repo,user,read:org"
            logger.info("Opening GitHub token creation page...")
            webbrowser.open(url)
            return True
        except Exception as e:
            logger.error(f"Failed to open GitHub token page: {e}")
            return False
    
    def open_google_app_password_page(self):
        """Open Google App Password creation page."""
        try:
            url = "https://myaccount.google.com/apppasswords"
            logger.info("Opening Google App Password page...")
            webbrowser.open(url)
            return True
        except Exception as e:
            logger.error(f"Failed to open Google App Password page: {e}")
            return False
    
    @staticmethod
    def get_github_token_instructions() -> str:
        """Get instructions for creating GitHub token."""
        return """
To create a GitHub Personal Access Token:

1. Click the button to open GitHub settings
2. Give your token a name (e.g., "XENO AI Assistant")
3. Select the following scopes:
   - repo (Full control of private repositories)
   - user (Update user data)
   - read:org (Read org data)
4. Click "Generate token"
5. Copy the token (you won't see it again!)
6. Paste it into XENO

Note: Treat this token like a password - never share it!
"""
    
    @staticmethod
    def get_google_app_password_instructions() -> str:
        """Get instructions for creating Google App Password."""
        return """
To create a Google App Password:

1. Click the button to open Google Account settings
2. You may need to verify it's you
3. Click "Create app password"
4. Give it a name (e.g., "XENO AI Assistant")
5. Click "Create"
6. Copy the 16-character password
7. Paste it into XENO

Note: This is different from your regular Google password!
App Passwords only work with 2-Step Verification enabled.
"""

"""
Voice Command Processor for XENO
Processes voice commands and triggers actions
"""
import re
from src.core.logger import setup_logger


class VoiceCommandProcessor:
    """Process voice commands and trigger actions"""
    
    def __init__(self, main_window):
        """
        Initialize command processor
        
        Args:
            main_window: Main window instance to control
        """
        self.logger = setup_logger("voice.commands")
        self.main_window = main_window
        
        # Command patterns
        self.commands = {
            # Navigation
            r'(open|show|go to) (gmail|email|inbox)': self._open_gmail,
            r'(open|show|go to) github': self._open_github,
            r'(open|show|go to) linkedin': self._open_linkedin,
            r'(open|show|go to) (chat|ai)': self._open_chat,
            r'(open|show|go to) dashboard': self._open_dashboard,
            r'(open|show|go to) settings': self._open_settings,
            
            # Email commands
            r'check (my )?email(s)?': self._check_emails,
            r'read (my )?email(s)?': self._check_emails,
            r'(any )?new email(s)?': self._check_emails,
            r'refresh email(s)?': self._refresh_emails,
            
            # GitHub commands
            r'(show|list) (my )?repositor(y|ies)': self._show_repos,
            r'(show|list) (my )?repo(s)?': self._show_repos,
            r'github stats': self._show_github_stats,
            
            # LinkedIn commands
            r'(show|open) (my )?profile': self._show_linkedin,
            r'linkedin profile': self._show_linkedin,
            
            # General commands
            r'what can you do': self._show_help,
            r'help': self._show_help,
            r'hello|hi|hey': self._greet,
            r'thank you|thanks': self._you_re_welcome,
            r'goodbye|bye|exit': self._goodbye,
        }
    
    def process_command(self, command_text):
        """
        Process a voice command
        
        Args:
            command_text: Command text to process
            
        Returns:
            Response text or None
        """
        command_text = command_text.lower().strip()
        self.logger.info(f"Processing command: {command_text}")
        
        # Try to match command patterns
        for pattern, handler in self.commands.items():
            if re.search(pattern, command_text):
                self.logger.info(f"Matched pattern: {pattern}")
                try:
                    response = handler(command_text)
                    return response
                except Exception as e:
                    self.logger.error(f"Error executing command: {e}")
                    return f"Sorry, I encountered an error: {str(e)}"
        
        # No match found - ask AI
        return self._ask_ai(command_text)
    
    # Navigation commands
    def _open_gmail(self, cmd):
        """Open Gmail page"""
        self.main_window._switch_page(2)  # Gmail is page 2
        return "Opening your Gmail inbox"
    
    def _open_github(self, cmd):
        """Open GitHub page"""
        self.main_window._switch_page(4)  # GitHub is page 4
        return "Opening your GitHub repositories"
    
    def _open_linkedin(self, cmd):
        """Open LinkedIn page"""
        self.main_window._switch_page(3)  # LinkedIn is page 3
        return "Opening your LinkedIn profile"
    
    def _open_chat(self, cmd):
        """Open chat page"""
        self.main_window._switch_page(0)  # Chat is page 0
        return "Opening AI chat"
    
    def _open_dashboard(self, cmd):
        """Open dashboard"""
        self.main_window._switch_page(1)  # Dashboard is page 1
        return "Opening dashboard"
    
    def _open_settings(self, cmd):
        """Open settings"""
        self.main_window._switch_page(5)  # Settings is page 5
        return "Opening settings"
    
    # Email commands
    def _check_emails(self, cmd):
        """Check emails"""
        self.main_window._switch_page(2)
        if self.main_window.email_handler:
            # Trigger refresh if logged in
            try:
                self.main_window._load_gmail_emails()
                return "Checking your emails now"
            except:
                return "Please login to Gmail first"
        else:
            return "Please login to Gmail to check your emails"
    
    def _refresh_emails(self, cmd):
        """Refresh email list"""
        if self.main_window.email_handler:
            self.main_window._load_gmail_emails()
            return "Refreshing your emails"
        else:
            return "Please login to Gmail first"
    
    # GitHub commands
    def _show_repos(self, cmd):
        """Show repositories"""
        self.main_window._switch_page(4)
        if self.main_window.github_manager:
            try:
                self.main_window._load_github_repos()
                return "Showing your repositories"
            except:
                return "Please login to GitHub first"
        else:
            return "Please login to GitHub to see your repositories"
    
    def _show_github_stats(self, cmd):
        """Show GitHub stats"""
        if self.main_window.github_manager:
            try:
                stats = self.main_window.github_manager.get_user_stats()
                return f"You have {stats.get('public_repos', 0)} public repositories, {stats.get('followers', 0)} followers, and {stats.get('following', 0)} following"
            except:
                return "Could not fetch GitHub stats"
        else:
            return "Please login to GitHub first"
    
    # LinkedIn commands
    def _show_linkedin(self, cmd):
        """Show LinkedIn profile"""
        self.main_window._switch_page(3)
        if self.main_window.linkedin_automation:
            return "Opening your LinkedIn profile"
        else:
            return "Please login to LinkedIn first"
    
    # General commands
    def _show_help(self, cmd):
        """Show available commands"""
        return ("I can help you with: checking emails, viewing GitHub repositories, "
                "managing LinkedIn, searching jobs, and chatting with AI. "
                "Try saying 'open Gmail' or 'check my emails'.")
    
    def _greet(self, cmd):
        """Greeting"""
        return "Hello! How can I assist you today?"
    
    def _you_re_welcome(self, cmd):
        """Response to thanks"""
        return "You're welcome! Anything else I can help with?"
    
    def _goodbye(self, cmd):
        """Goodbye"""
        return "Goodbye! Call me anytime you need assistance."
    
    def _ask_ai(self, cmd):
        """Ask AI assistant for unrecognized commands"""
        # Switch to chat page
        self.main_window._switch_page(0)
        
        # Send to AI chat
        if self.main_window.ai_chat:
            try:
                # Set the chat input
                self.main_window.chat_input.setText(cmd)
                # Trigger send
                self.main_window._send_message()
                return "Let me think about that"
            except:
                return "I didn't understand that command. Try asking in the chat."
        else:
            return "I didn't understand that command. Try 'help' for available commands."

"""
Enhanced Voice Command Handler with TTS Feedback
Handles advanced voice commands and provides spoken responses
"""
import re
from datetime import datetime, timedelta
from pathlib import Path
from core.logger import setup_logger
import pyttsx3


class VoiceCommandHandler:
    """Enhanced voice command handler with TTS feedback"""
    
    def __init__(self, main_window=None):
        """
        Initialize voice command handler
        
        Args:
            main_window: Reference to main window for UI actions
        """
        self.logger = setup_logger("voice.command_handler")
        self.main_window = main_window
        
        # Initialize text-to-speech
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 175)  # Speed
            self.tts_engine.setProperty('volume', 0.9)  # Volume
            
            # Set voice (try to use female voice if available)
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            self.tts_enabled = True
            self.logger.info("Text-to-speech initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS: {e}")
            self.tts_enabled = False
        
        # Command patterns
        self.command_patterns = {
            # Email commands
            'check_email': r'(check|read|show|get) (my )?email',
            'unread_email': r'(how many|check) unread',
            'send_email': r'send (an )?email to (.+)',
            'reply_email': r'reply to (.+)',
            
            # Calendar/Schedule commands
            'schedule_meeting': r'schedule (a )?meeting (.+)',
            'check_schedule': r"(what's|check|show) (my )?schedule",
            'add_reminder': r'remind me to (.+)',
            'upcoming_events': r"(what's|any) upcoming (events|meetings)",
            
            # LinkedIn/Job commands
            'search_jobs': r'(search|find|look for) jobs? (.+)',
            'check_applications': r'check (my )?applications?',
            'apply_job': r'apply (to|for) (.+)',
            
            # GitHub commands
            'check_repos': r'(check|show|list) (my )?repositories',
            'repo_status': r'(status|check) (of )?(.+) repo',
            'recent_commits': r'(show|check) recent commits',
            
            # AI commands
            'daily_briefing': r'(give|show|get) (me )?(my |a )?daily briefing',
            'ask_ai': r'(ask|tell me|what is|how to) (.+)',
            
            # Dashboard commands
            'open_dashboard': r'(open|show|go to) dashboard',
            'refresh': r'refresh',
            'add_goal': r'add goal (.+)',
            
            # System commands
            'time': r'what time is it',
            'date': r"what's (the )?date",
            'status': r'(system )?status',
            'help': r'help|what can you do',
        }
    
    def speak(self, text):
        """Speak text using TTS"""
        if self.tts_enabled:
            try:
                self.logger.info(f"Speaking: {text}")
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                self.logger.error(f"TTS error: {e}")
    
    def process_command(self, command):
        """
        Process voice command and execute appropriate action
        
        Args:
            command: Voice command text
            
        Returns:
            Response text
        """
        command = command.lower().strip()
        self.logger.info(f"Processing command: {command}")
        
        # Match command to pattern and execute
        for cmd_type, pattern in self.command_patterns.items():
            match = re.search(pattern, command)
            if match:
                self.logger.info(f"Matched command type: {cmd_type}")
                handler = getattr(self, f'_handle_{cmd_type}', None)
                if handler:
                    response = handler(match)
                    self.speak(response)
                    return response
        
        # No specific command matched, use AI
        return self._handle_ask_ai(command)
    
    def _handle_check_email(self, match):
        """Handle check email command"""
        if not self.main_window or not self.main_window.email_handler:
            return "Email is not configured."
        
        try:
            unread = self.main_window.email_handler.get_unread_count()
            if unread == 0:
                return "You have no unread emails."
            elif unread == 1:
                return "You have 1 unread email."
            else:
                return f"You have {unread} unread emails."
        except Exception as e:
            self.logger.error(f"Error checking email: {e}")
            return "I couldn't check your email."
    
    def _handle_unread_email(self, match):
        """Handle unread count command"""
        return self._handle_check_email(match)
    
    def _handle_send_email(self, match):
        """Handle send email command"""
        recipient = match.group(2)
        if self.main_window:
            # Open compose dialog
            self.main_window._show_compose_dialog(to=recipient)
            return f"Opening email compose dialog for {recipient}."
        return "I can't send emails right now."
    
    def _handle_schedule_meeting(self, match):
        """Handle schedule meeting command"""
        meeting_details = match.group(2)
        # Parse meeting details (future: integrate with calendar)
        return f"I'll help you schedule a meeting about {meeting_details}. Calendar integration coming soon!"
    
    def _handle_check_schedule(self, match):
        """Handle check schedule command"""
        # Future: integrate with Google Calendar
        current_time = datetime.now().strftime("%I:%M %p")
        return f"It's currently {current_time}. Calendar integration is coming soon to show your full schedule."
    
    def _handle_add_reminder(self, match):
        """Handle add reminder command"""
        reminder_text = match.group(1)
        # Future: integrate with reminder system
        if self.main_window:
            # Add as a goal for now
            try:
                self.main_window._add_goal_widget(f"Reminder: {reminder_text}", False)
                self.main_window._save_goals()
                return f"I've added a reminder to {reminder_text}."
            except:
                pass
        return f"I'll remind you to {reminder_text}."
    
    def _handle_upcoming_events(self, match):
        """Handle upcoming events command"""
        return "Calendar integration is coming soon. I'll be able to show your upcoming events then!"
    
    def _handle_search_jobs(self, match):
        """Handle search jobs command"""
        job_query = match.group(2)
        if self.main_window and hasattr(self.main_window, 'job_keywords_input'):
            self.main_window.job_keywords_input.setText(job_query)
            # Switch to jobs page
            self.main_window._switch_page(3)  # LinkedIn page
            return f"Searching for {job_query} jobs on LinkedIn."
        return f"I'll search for {job_query} jobs."
    
    def _handle_check_applications(self, match):
        """Handle check applications command"""
        if self.main_window:
            self.main_window._switch_page(3)  # LinkedIn page
            return "Opening your job applications."
        return "Checking your applications."
    
    def _handle_check_repos(self, match):
        """Handle check repositories command"""
        if self.main_window and self.main_window.github_manager:
            try:
                repos = self.main_window.github_manager.get_repositories()
                count = len(repos)
                self.main_window._switch_page(4)  # GitHub page
                return f"You have {count} repositories. Opening GitHub page."
            except:
                return "I couldn't access your GitHub repositories."
        return "GitHub is not configured."
    
    def _handle_recent_commits(self, match):
        """Handle recent commits command"""
        if self.main_window:
            self.main_window._switch_page(4)  # GitHub page
            return "Opening GitHub page to show recent activity."
        return "Checking recent commits."
    
    def _handle_daily_briefing(self, match):
        """Handle daily briefing command"""
        if self.main_window:
            # Switch to dashboard and generate briefing
            self.main_window._switch_page(1)  # Dashboard
            try:
                self.main_window._generate_daily_briefing()
                return "Generating your daily briefing on the dashboard."
            except:
                pass
        return "Preparing your daily briefing."
    
    def _handle_ask_ai(self, match):
        """Handle AI question command"""
        if isinstance(match, str):
            question = match
        else:
            question = match.group(2) if match.lastindex >= 2 else match.group(0)
        
        if self.main_window:
            # Use AI chat
            try:
                if hasattr(self.main_window, 'ai_chat_enhanced') and self.main_window.ai_chat_enhanced:
                    response = self.main_window.ai_chat_enhanced.send_message(question)
                elif hasattr(self.main_window, 'ai_chat') and self.main_window.ai_chat:
                    response = self.main_window.ai_chat.send_message(question)
                else:
                    return "AI is not configured."
                
                # Limit spoken response length
                if len(response) > 200:
                    return response[:200] + "... Check the chat window for the full response."
                return response
            except Exception as e:
                self.logger.error(f"AI error: {e}")
                return "I couldn't process that question."
        return "AI is not available."
    
    def _handle_open_dashboard(self, match):
        """Handle open dashboard command"""
        if self.main_window:
            self.main_window._switch_page(1)
            return "Opening dashboard."
        return "Dashboard opened."
    
    def _handle_refresh(self, match):
        """Handle refresh command"""
        if self.main_window and hasattr(self.main_window, '_refresh_dashboard'):
            self.main_window._refresh_dashboard()
            return "Refreshing dashboard."
        return "Refreshing."
    
    def _handle_add_goal(self, match):
        """Handle add goal command"""
        goal_text = match.group(1)
        if self.main_window:
            try:
                self.main_window._add_goal_widget(goal_text, False)
                self.main_window._save_goals()
                return f"Added goal: {goal_text}"
            except:
                pass
        return f"Goal added: {goal_text}"
    
    def _handle_time(self, match):
        """Handle time query"""
        current_time = datetime.now().strftime("%I:%M %p")
        return f"It's {current_time}."
    
    def _handle_date(self, match):
        """Handle date query"""
        current_date = datetime.now().strftime("%B %d, %Y")
        return f"Today is {current_date}."
    
    def _handle_status(self, match):
        """Handle system status query"""
        status_parts = ["XENO is online."]
        
        if self.main_window:
            if self.main_window.email_handler:
                status_parts.append("Email is connected.")
            if self.main_window.github_manager:
                status_parts.append("GitHub is connected.")
            if self.main_window.ai_chat or self.main_window.ai_chat_enhanced:
                status_parts.append("AI is ready.")
        
        return " ".join(status_parts)
    
    def _handle_help(self, match):
        """Handle help command"""
        return """I can help you with emails, schedule meetings, search for jobs, 
check GitHub, answer questions, and manage your dashboard. 
Try saying: check email, schedule meeting, search jobs, or ask me anything!"""

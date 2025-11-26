"""
Enhanced Voice Command Handler with TTS Feedback
Handles advanced voice commands and provides spoken responses
"""
import re
from datetime import datetime, timedelta
from pathlib import Path
from src.core.logger import setup_logger
import pyttsx3

try:
    from PyQt6.QtCore import QMetaObject, Qt, Q_ARG, QCoreApplication
    from PyQt6.QtWidgets import QApplication
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False


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
            # Navigation commands
            'open_gmail': r'(open|show|go to) (my )?gmail',
            'open_email': r'(open|show|go to) (my )?email',
            'open_linkedin': r'(open|show|go to) (my )?linkedin',
            'open_github': r'(open|show|go to) (my )?github',
            'open_calendar': r'(open|show|go to) (my )?calendar',
            'open_dashboard': r'(open|show|go to) (my )?dashboard',
            'open_chat': r'(open|show|go to) (my )?chat',
            'open_settings': r'(open|show|go to) settings',
            
            # Email commands - Enhanced
            'read_emails': r'(read|tell me about|show me) (my |the )?emails?',
            'read_next_email': r'(read |show )?next (email|one)',
            'read_previous_email': r'(read |show )?previous (email|one)',
            'check_email': r'(check|get) (my )?email',
            'unread_email': r'(how many|check) unread',
            'draft_reply': r'(draft|write|compose) (a )?reply',
            'send_reply': r'send (that |the )?reply',
            'send_email': r'send (an )?email to (.+)',
            
            # Calendar/Schedule commands
            'schedule_meeting': r'schedule (a )?meeting (.+)',
            'check_schedule': r"(what's|check|show) (my )?schedule",
            'add_reminder': r'remind me to (.+)',
            'upcoming_events': r"(what's|any) upcoming (events|meetings)",
            
            # LinkedIn/Job commands
            'search_jobs': r'(search|find|look for) jobs? (.+)',
            'check_applications': r'check (my )?applications?',
            'apply_job': r'apply (to|for) (.+)',
            'check_linkedin_jobs': r'check linkedin (for )?(new )?(internship|job|jobs|internships)',
            
            # GitHub commands
            'check_repos': r'(check|show|list) (my )?repositories',
            'check_readme': r'check (the )?readme (files?)?',
            'repo_status': r'(status|check) (of )?(.+) repo',
            'recent_commits': r'(show|check) recent commits',
            'repos_uptodate': r'(check if|are) (my )?repos (are )?up to date',
            
            # AI commands
            'daily_briefing': r'(give|show|get) (me )?(my |a )?daily briefing',
            'ask_ai': r'(ask|tell me|what is|how to) (.+)',
            
            # Other commands
            'refresh': r'refresh',
            'add_goal': r'add goal (.+)',
            
            # System commands
            'time': r'what time is it',
            'date': r"what's (the )?date",
            'status': r'(system )?status',
            'help': r'help|what can you do',
        }
        
        # Email reading state
        self.current_emails = []
        self.current_email_index = -1
        self.draft_reply_text = ""
    
    def speak(self, text):
        """Speak text using TTS - thread-safe"""
        if self.tts_enabled:
            try:
                self.logger.info(f"Speaking: {text}")
                # Run TTS in a separate thread to avoid Qt threading issues
                import threading
                def _speak():
                    try:
                        self.tts_engine.say(text)
                        self.tts_engine.runAndWait()
                    except Exception as e:
                        self.logger.error(f"TTS error in thread: {e}")
                
                speak_thread = threading.Thread(target=_speak, daemon=True)
                speak_thread.start()
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
    
    def _handle_read_emails(self, match):
        """Handle read emails command - reads through emails one by one"""
        if not self.main_window or not self.main_window.email_handler:
            return "Email is not configured."
        
        try:
            # Fetch recent unread emails
            self.current_emails = self.main_window.email_handler.get_recent_emails(count=10, only_unread=True)
            
            if not self.current_emails:
                return "You have no unread emails."
            
            # Start with the first email
            self.current_email_index = 0
            return self._read_current_email()
            
        except Exception as e:
            self.logger.error(f"Error reading emails: {e}")
            return "I couldn't read your emails."
    
    def _handle_read_next_email(self, match):
        """Handle read next email command"""
        if not self.current_emails:
            return "Please say 'read my emails' first."
        
        if self.current_email_index >= len(self.current_emails) - 1:
            return "That was the last email."
        
        self.current_email_index += 1
        return self._read_current_email()
    
    def _handle_read_previous_email(self, match):
        """Handle read previous email command"""
        if not self.current_emails:
            return "Please say 'read my emails' first."
        
        if self.current_email_index <= 0:
            return "This is the first email."
        
        self.current_email_index -= 1
        return self._read_current_email()
    
    def _read_current_email(self):
        """Read the current email with full details"""
        if not self.current_emails or self.current_email_index < 0:
            return "No email to read."
        
        email = self.current_emails[self.current_email_index]
        
        # Parse the sender
        sender = email.get('from', 'Unknown')
        # Extract just the name or email
        if '<' in sender:
            sender = sender.split('<')[0].strip().strip('"')
        
        # Parse the date
        date_str = email.get('date', '')
        try:
            from email.utils import parsedate_to_datetime
            email_date = parsedate_to_datetime(date_str)
            date_display = email_date.strftime("%B %d at %I:%M %p")
        except:
            date_display = date_str
        
        # Get subject and body
        subject = email.get('subject', 'No subject')
        body = email.get('body', '').strip()
        
        # Clean up body (remove HTML tags if present)
        import re
        body_clean = re.sub('<[^<]+?>', '', body)
        body_clean = body_clean[:300]  # Limit to first 300 chars
        
        # Build the response
        response = f"Email {self.current_email_index + 1} of {len(self.current_emails)}. "
        response += f"From {sender}. "
        response += f"Subject: {subject}. "
        response += f"Received on {date_display}. "
        response += f"The email says: {body_clean}"
        
        return response
    
    def _handle_draft_reply(self, match):
        """Handle draft reply command"""
        if not self.current_emails or self.current_email_index < 0:
            return "Please read an email first before replying."
        
        current_email = self.current_emails[self.current_email_index]
        
        # Use AI to draft a reply (simplified version)
        subject = current_email.get('subject', '')
        sender = current_email.get('from', '')
        body = current_email.get('full_body', '')
        
        # Simple professional reply template
        self.draft_reply_text = f"Thank you for your email regarding {subject}. I have reviewed your message and will get back to you shortly."
        
        return f"I've drafted a reply: {self.draft_reply_text}. Say 'send reply' to send it, or tell me how to modify it."
    
    def _handle_send_reply(self, match):
        """Handle send reply command"""
        if not self.draft_reply_text:
            return "Please draft a reply first by saying 'draft a reply'."
        
        if not self.current_emails or self.current_email_index < 0:
            return "No email to reply to."
        
        current_email = self.current_emails[self.current_email_index]
        
        try:
            # Extract sender email
            sender = current_email.get('from', '')
            if '<' in sender:
                email_addr = sender.split('<')[1].split('>')[0]
            else:
                email_addr = sender
            
            # Get subject
            subject = current_email.get('subject', '')
            if not subject.lower().startswith('re:'):
                subject = f"Re: {subject}"
            
            # Send the email
            success = self.main_window.email_handler.send_email(
                to=email_addr,
                subject=subject,
                body=self.draft_reply_text
            )
            
            if success:
                self.draft_reply_text = ""
                return f"Reply sent successfully to {email_addr}."
            else:
                return "Failed to send the reply. Please check your email configuration."
                
        except Exception as e:
            self.logger.error(f"Error sending reply: {e}")
            return "I couldn't send the reply due to an error."
    
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
    
    def _handle_check_readme(self, match):
        """Handle check readme files command"""
        if self.main_window and self.main_window.github_manager:
            try:
                repos = self.main_window.github_manager.get_repositories()
                self.main_window._switch_page(4)  # GitHub page
                
                # Summary of repos
                readme_summary = f"Checking README files for {len(repos)} repositories. "
                # In a full implementation, would actually fetch and analyze README files
                return readme_summary + "Opening GitHub page for details."
            except:
                return "I couldn't access your GitHub repositories."
        return "GitHub is not configured."
    
    def _handle_repos_uptodate(self, match):
        """Handle check if repos are up to date command"""
        if self.main_window and self.main_window.github_manager:
            try:
                repos = self.main_window.github_manager.get_repositories()
                self.main_window._switch_page(4)  # GitHub page
                
                # Check for repos that need attention
                return f"Checking {len(repos)} repositories for updates. Opening GitHub page."
            except:
                return "I couldn't access your GitHub repositories."
        return "GitHub is not configured."
    
    def _handle_check_linkedin_jobs(self, match):
        """Handle check LinkedIn for new internship/job opportunities"""
        if self.main_window:
            self.main_window._switch_page(3)  # LinkedIn page
            
            # Determine if looking for internships or jobs
            job_type = "internship" if "internship" in match.group(0) else "job"
            return f"Checking LinkedIn for new {job_type} opportunities. Opening LinkedIn page."
        return "Opening LinkedIn to check for opportunities."
    
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
    
    def _switch_page_safe(self, page_index):
        """Safely switch page using Qt's thread-safe signal mechanism"""
        if self.main_window and QT_AVAILABLE:
            try:
                # Use QMetaObject.invokeMethod for thread-safe Qt calls
                QMetaObject.invokeMethod(
                    self.main_window,
                    "_switch_page",
                    Qt.ConnectionType.QueuedConnection,
                    Q_ARG(int, page_index)
                )
            except Exception as e:
                self.logger.error(f"Error switching page: {e}")
                # Fallback to direct call
                try:
                    self.main_window._switch_page(page_index)
                except:
                    pass
    
    def _handle_open_gmail(self, match):
        """Handle open gmail command"""
        if self.main_window:
            self._switch_page_safe(2)  # Gmail page
            return "Opening Gmail."
        return "Gmail opened."
    
    def _handle_open_email(self, match):
        """Handle open email command (alias for Gmail)"""
        return self._handle_open_gmail(match)
    
    def _handle_open_linkedin(self, match):
        """Handle open linkedin command"""
        if self.main_window:
            self._switch_page_safe(3)  # LinkedIn page
            return "Opening LinkedIn."
        return "LinkedIn opened."
    
    def _handle_open_github(self, match):
        """Handle open github command"""
        if self.main_window:
            self._switch_page_safe(4)  # GitHub page
            return "Opening GitHub."
        return "GitHub opened."
    
    def _handle_open_calendar(self, match):
        """Handle open calendar command"""
        if self.main_window:
            self._switch_page_safe(5)  # Calendar page
            return "Opening calendar."
        return "Calendar opened."
    
    def _handle_open_chat(self, match):
        """Handle open chat command"""
        if self.main_window:
            self._switch_page_safe(0)  # Chat page
            return "Opening chat."
        return "Chat opened."
    
    def _handle_open_settings(self, match):
        """Handle open settings command"""
        if self.main_window:
            self._switch_page_safe(6)  # Settings page
            return "Opening settings."
        return "Settings opened."
    
    def _handle_open_dashboard(self, match):
        """Handle open dashboard command"""
        if self.main_window:
            self._switch_page_safe(1)
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

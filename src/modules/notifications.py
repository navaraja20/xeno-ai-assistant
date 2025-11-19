"""
Notification system for XENO
Handles desktop notifications for emails, GitHub, LinkedIn, and other events
"""
import logging
from datetime import datetime
from typing import Optional, Callable
import threading
import time
from plyer import notification

logger = logging.getLogger("XENO.Notifications")


class NotificationManager:
    """Manages desktop notifications and alerts"""
    
    def __init__(self, app_name: str = "XENO"):
        """
        Initialize notification manager
        
        Args:
            app_name: Application name for notifications
        """
        self.app_name = app_name
        self.enabled = True
        self.notification_history = []
        self.max_history = 100
        logger.info("NotificationManager initialized")
    
    def notify(
        self,
        title: str,
        message: str,
        urgency: str = "normal",
        timeout: int = 10,
        callback: Optional[Callable] = None
    ):
        """
        Send a desktop notification
        
        Args:
            title: Notification title
            message: Notification message
            urgency: Urgency level ('low', 'normal', 'critical')
            timeout: Notification display time in seconds
            callback: Optional callback when notification is clicked
        """
        if not self.enabled:
            return
        
        try:
            notification.notify(
                title=f"{self.app_name} - {title}",
                message=message,
                app_name=self.app_name,
                timeout=timeout
            )
            
            # Store in history
            self._add_to_history(title, message, urgency)
            
            logger.info(f"Notification sent: {title}")
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    def notify_email(self, sender: str, subject: str, preview: str):
        """
        Send email notification
        
        Args:
            sender: Email sender
            subject: Email subject
            preview: Email preview text
        """
        self.notify(
            title=f"New Email from {sender}",
            message=f"{subject}\n{preview[:100]}...",
            urgency="normal",
            timeout=15
        )
    
    def notify_github(self, repo: str, event_type: str, details: str):
        """
        Send GitHub notification
        
        Args:
            repo: Repository name
            event_type: Type of event (PR, Issue, Star, etc.)
            details: Event details
        """
        self.notify(
            title=f"GitHub - {event_type}",
            message=f"{repo}\n{details}",
            urgency="normal",
            timeout=10
        )
    
    def notify_linkedin(self, event_type: str, details: str):
        """
        Send LinkedIn notification
        
        Args:
            event_type: Type of event (Message, Connection, Job, etc.)
            details: Event details
        """
        self.notify(
            title=f"LinkedIn - {event_type}",
            message=details,
            urgency="normal",
            timeout=10
        )
    
    def notify_urgent(self, title: str, message: str):
        """
        Send urgent notification with high priority
        
        Args:
            title: Notification title
            message: Notification message
        """
        self.notify(
            title=title,
            message=message,
            urgency="critical",
            timeout=0  # Stay until dismissed
        )
    
    def _add_to_history(self, title: str, message: str, urgency: str):
        """Add notification to history"""
        self.notification_history.append({
            'title': title,
            'message': message,
            'urgency': urgency,
            'timestamp': datetime.now()
        })
        
        # Trim history if too large
        if len(self.notification_history) > self.max_history:
            self.notification_history = self.notification_history[-self.max_history:]
    
    def get_history(self, limit: int = 20):
        """Get notification history"""
        return self.notification_history[-limit:]
    
    def clear_history(self):
        """Clear notification history"""
        self.notification_history = []
        logger.info("Notification history cleared")
    
    def enable(self):
        """Enable notifications"""
        self.enabled = True
        logger.info("Notifications enabled")
    
    def disable(self):
        """Disable notifications"""
        self.enabled = False
        logger.info("Notifications disabled")


class BackgroundMonitor:
    """Background monitoring service for proactive notifications"""
    
    def __init__(self, notification_manager: NotificationManager):
        """
        Initialize background monitor
        
        Args:
            notification_manager: NotificationManager instance
        """
        self.notification_manager = notification_manager
        self.email_handler = None
        self.github_manager = None
        self.linkedin_automation = None
        
        self.is_running = False
        self.monitor_thread = None
        
        # Tracking state
        self.last_email_count = 0
        self.last_github_notifications = 0
        self.seen_email_ids = set()
        
        # Monitor intervals (seconds)
        self.email_interval = 60  # Check every 1 minute
        self.github_interval = 300  # Check every 5 minutes
        self.linkedin_interval = 600  # Check every 10 minutes
        
        logger.info("BackgroundMonitor initialized")
    
    def set_email_handler(self, handler):
        """Set email handler for monitoring"""
        self.email_handler = handler
        logger.info("Email handler connected to monitor")
    
    def set_github_manager(self, manager):
        """Set GitHub manager for monitoring"""
        self.github_manager = manager
        logger.info("GitHub manager connected to monitor")
    
    def set_linkedin_automation(self, automation):
        """Set LinkedIn automation for monitoring"""
        self.linkedin_automation = automation
        logger.info("LinkedIn automation connected to monitor")
    
    def start(self):
        """Start background monitoring"""
        if self.is_running:
            logger.warning("Monitor already running")
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Background monitoring started")
    
    def stop(self):
        """Stop background monitoring"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Background monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        last_email_check = 0
        last_github_check = 0
        last_linkedin_check = 0
        
        while self.is_running:
            current_time = time.time()
            
            # Check emails
            if current_time - last_email_check >= self.email_interval:
                self._check_emails()
                last_email_check = current_time
            
            # Check GitHub
            if current_time - last_github_check >= self.github_interval:
                self._check_github()
                last_github_check = current_time
            
            # Check LinkedIn
            if current_time - last_linkedin_check >= self.linkedin_interval:
                self._check_linkedin()
                last_linkedin_check = current_time
            
            # Sleep for a short interval
            time.sleep(10)
    
    def _check_emails(self):
        """Check for new emails"""
        if not self.email_handler:
            return
        
        try:
            # Get recent unread emails
            emails = self.email_handler.get_recent_emails(count=5, only_unread=True)
            
            for email in emails:
                email_id = email.get('id')
                
                # Skip if already seen
                if email_id in self.seen_email_ids:
                    continue
                
                # Mark as seen
                self.seen_email_ids.add(email_id)
                
                # Send notification
                sender = email.get('from', 'Unknown')
                subject = email.get('subject', '(No Subject)')
                preview = email.get('body', '')[:100]
                
                # Check if urgent (basic detection)
                is_urgent = any(word in subject.lower() for word in ['urgent', 'important', 'asap', 'critical'])
                
                if is_urgent:
                    self.notification_manager.notify_urgent(
                        f"URGENT Email from {sender}",
                        f"{subject}\n{preview}"
                    )
                else:
                    self.notification_manager.notify_email(sender, subject, preview)
            
            # Trim seen_email_ids if too large
            if len(self.seen_email_ids) > 1000:
                self.seen_email_ids = set(list(self.seen_email_ids)[-500:])
                
        except Exception as e:
            logger.error(f"Error checking emails: {e}")
    
    def _check_github(self):
        """Check for GitHub notifications"""
        if not self.github_manager:
            return
        
        try:
            # Get notifications (if API supports it)
            # This is a placeholder - GitHub API has notification endpoints
            logger.debug("Checking GitHub notifications...")
            
        except Exception as e:
            logger.error(f"Error checking GitHub: {e}")
    
    def _check_linkedin(self):
        """Check for LinkedIn notifications"""
        if not self.linkedin_automation:
            return
        
        try:
            # Check for new messages/connections
            logger.debug("Checking LinkedIn notifications...")
            
        except Exception as e:
            logger.error(f"Error checking LinkedIn: {e}")

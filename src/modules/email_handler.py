"""
Email automation module for XENO AI Assistant.
Handles email reading, sending, auto-replies, and filtering.
"""

import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from typing import List, Dict, Optional
import logging
from datetime import datetime
import re

logger = logging.getLogger("XENO.EmailHandler")


class EmailHandler:
    """Handles all email automation tasks."""
    
    def __init__(self, email_address: str, password: str):
        """
        Initialize email handler.
        
        Args:
            email_address: User's email address
            password: App password (not regular password - use Gmail App Passwords)
        """
        self.email_address = email_address
        self.password = password
        self.imap_server = self._get_imap_server(email_address)
        self.smtp_server = self._get_smtp_server(email_address)
        self.imap = None
        self.smtp = None
        logger.info(f"EmailHandler initialized for {email_address}")
    
    def _get_imap_server(self, email_address: str) -> tuple:
        """Get IMAP server settings based on email provider."""
        domain = email_address.split('@')[1].lower()
        
        servers = {
            'gmail.com': ('imap.gmail.com', 993),
            'outlook.com': ('outlook.office365.com', 993),
            'hotmail.com': ('outlook.office365.com', 993),
            'yahoo.com': ('imap.mail.yahoo.com', 993),
        }
        
        return servers.get(domain, ('imap.gmail.com', 993))
    
    def _get_smtp_server(self, email_address: str) -> tuple:
        """Get SMTP server settings based on email provider."""
        domain = email_address.split('@')[1].lower()
        
        servers = {
            'gmail.com': ('smtp.gmail.com', 587),
            'outlook.com': ('smtp.office365.com', 587),
            'hotmail.com': ('smtp.office365.com', 587),
            'yahoo.com': ('smtp.mail.yahoo.com', 587),
        }
        
        return servers.get(domain, ('smtp.gmail.com', 587))
    
    def connect(self) -> bool:
        """Connect to email servers."""
        try:
            # Connect to IMAP
            server, port = self.imap_server
            self.imap = imaplib.IMAP4_SSL(server, port)
            self.imap.login(self.email_address, self.password)
            logger.info("Successfully connected to IMAP server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to email: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from email servers."""
        try:
            if self.imap:
                self.imap.logout()
            if self.smtp:
                self.smtp.quit()
            logger.info("Disconnected from email servers")
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
    
    def get_unread_count(self) -> int:
        """Get count of unread emails."""
        try:
            if not self.imap:
                self.connect()
            
            self.imap.select('INBOX')
            status, messages = self.imap.search(None, 'UNSEEN')
            
            if status == 'OK':
                email_ids = messages[0].split()
                count = len(email_ids)
                logger.info(f"Found {count} unread emails")
                return count
            return 0
        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            return 0
    
    def get_recent_emails(self, count: int = 10, only_unread: bool = False) -> List[Dict]:
        """
        Get recent emails.
        
        Args:
            count: Number of emails to retrieve
            only_unread: If True, only get unread emails
            
        Returns:
            List of email dictionaries with subject, from, date, body
        """
        try:
            if not self.imap:
                self.connect()
            
            self.imap.select('INBOX')
            
            # Search for emails
            search_criteria = 'UNSEEN' if only_unread else 'ALL'
            status, messages = self.imap.search(None, search_criteria)
            
            if status != 'OK':
                return []
            
            email_ids = messages[0].split()
            email_ids = email_ids[-count:]  # Get latest N emails
            
            emails = []
            for email_id in reversed(email_ids):  # Newest first
                email_data = self._fetch_email(email_id)
                if email_data:
                    emails.append(email_data)
            
            logger.info(f"Retrieved {len(emails)} emails")
            return emails
            
        except Exception as e:
            logger.error(f"Error getting recent emails: {e}")
            return []
    
    def _fetch_email(self, email_id: bytes) -> Optional[Dict]:
        """Fetch and parse a single email."""
        try:
            status, msg_data = self.imap.fetch(email_id, '(RFC822)')
            
            if status != 'OK':
                return None
            
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Decode subject
            subject, encoding = decode_header(email_message["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else 'utf-8')
            
            # Get sender
            from_header = email_message.get("From")
            
            # Get date
            date_str = email_message.get("Date")
            
            # Get body
            body = self._get_email_body(email_message)
            
            return {
                'id': email_id.decode(),
                'subject': subject,
                'from': from_header,
                'date': date_str,
                'body': body[:500],  # First 500 chars
                'full_body': body
            }
            
        except Exception as e:
            logger.error(f"Error fetching email {email_id}: {e}")
            return None
    
    def _get_email_body(self, email_message) -> str:
        """Extract email body from message."""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except:
                        pass
        else:
            try:
                body = email_message.get_payload(decode=True).decode()
            except:
                body = str(email_message.get_payload())
        
        return body.strip()
    
    def send_email(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            html: If True, send as HTML email
            
        Returns:
            True if sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to
            msg['Subject'] = subject
            
            # Add body
            msg_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, msg_type))
            
            # Connect to SMTP
            server, port = self.smtp_server
            self.smtp = smtplib.SMTP(server, port)
            self.smtp.starttls()
            self.smtp.login(self.email_address, self.password)
            
            # Send email
            self.smtp.send_message(msg)
            self.smtp.quit()
            
            logger.info(f"Email sent successfully to {to}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def auto_reply(self, email_id: str, reply_message: str) -> bool:
        """
        Send an auto-reply to an email.
        
        Args:
            email_id: ID of the email to reply to
            reply_message: Message to send
            
        Returns:
            True if reply sent successfully
        """
        try:
            # Fetch the original email
            status, msg_data = self.imap.fetch(email_id.encode(), '(RFC822)')
            
            if status != 'OK':
                return False
            
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Get original sender
            from_header = email_message.get("From")
            # Extract email address from "Name <email@domain.com>" format
            email_match = re.search(r'<(.+?)>', from_header)
            recipient = email_match.group(1) if email_match else from_header
            
            # Get original subject
            subject, encoding = decode_header(email_message["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else 'utf-8')
            
            # Add "Re: " if not already there
            if not subject.startswith("Re: "):
                subject = f"Re: {subject}"
            
            # Send reply
            return self.send_email(recipient, subject, reply_message)
            
        except Exception as e:
            logger.error(f"Failed to send auto-reply: {e}")
            return False
    
    def mark_as_read(self, email_id: str) -> bool:
        """Mark an email as read."""
        try:
            self.imap.store(email_id.encode(), '+FLAGS', '\\Seen')
            logger.info(f"Marked email {email_id} as read")
            return True
        except Exception as e:
            logger.error(f"Failed to mark email as read: {e}")
            return False
    
    def search_emails(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Search emails by subject or sender.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of matching emails
        """
        try:
            if not self.imap:
                self.connect()
            
            self.imap.select('INBOX')
            
            # Search by subject
            status, messages = self.imap.search(None, f'SUBJECT "{query}"')
            
            if status != 'OK':
                return []
            
            email_ids = messages[0].split()
            email_ids = email_ids[-max_results:]
            
            emails = []
            for email_id in reversed(email_ids):
                email_data = self._fetch_email(email_id)
                if email_data:
                    emails.append(email_data)
            
            logger.info(f"Found {len(emails)} emails matching '{query}'")
            return emails
            
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []

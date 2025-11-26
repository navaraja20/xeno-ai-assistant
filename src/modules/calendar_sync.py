"""
Calendar sync module for XENO AI Assistant.
Handles Google Calendar integration for event management.
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
import os
import pickle

logger = logging.getLogger("XENO.CalendarSync")

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']


class CalendarSync:
    """Handles Google Calendar synchronization and event management."""
    
    def __init__(self, credentials_path: str = None):
        """
        Initialize calendar sync.
        
        Args:
            credentials_path: Path to store credentials (default: ~/.XENO/)
        """
        if credentials_path is None:
            credentials_path = os.path.expanduser('~/.XENO/')
        
        self.credentials_path = credentials_path
        self.token_file = os.path.join(credentials_path, 'calendar_token.pickle')
        self.credentials_file = os.path.join(credentials_path, 'calendar_credentials.json')
        self.service = None
        self.creds = None
        
        # Create credentials directory if it doesn't exist
        os.makedirs(credentials_path, exist_ok=True)
        
        logger.info("CalendarSync initialized")
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API.
        
        Returns:
            True if authentication successful
        """
        try:
            # Load existing credentials
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # If no valid credentials, let user log in
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    # Check if credentials file exists
                    if not os.path.exists(self.credentials_file):
                        logger.error(f"Credentials file not found: {self.credentials_file}")
                        logger.info("Please download OAuth credentials from Google Cloud Console")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.creds, token)
            
            # Build service
            self.service = build('calendar', 'v3', credentials=self.creds)
            logger.info("Successfully authenticated with Google Calendar")
            return True
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Calendar: {e}")
            return False
    
    def get_upcoming_events(self, max_results: int = 10, days_ahead: int = 7) -> List[Dict]:
        """
        Get upcoming calendar events.
        
        Args:
            max_results: Maximum number of events to return
            days_ahead: Number of days to look ahead
            
        Returns:
            List of event dictionaries
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return []
            
            # Get current time and time range
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            # Call Calendar API
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            result = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                result.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'description': event.get('description', ''),
                    'start': start,
                    'end': end,
                    'location': event.get('location', ''),
                    'attendees': [a.get('email') for a in event.get('attendees', [])]
                })
            
            logger.info(f"Retrieved {len(result)} upcoming events")
            return result
            
        except HttpError as e:
            logger.error(f"HTTP error getting events: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            return []
    
    def create_event(self, summary: str, start_time: datetime, end_time: datetime,
                    description: str = '', location: str = '', 
                    attendees: List[str] = None) -> Optional[str]:
        """
        Create a new calendar event.
        
        Args:
            summary: Event title
            start_time: Start datetime
            end_time: End datetime
            description: Event description
            location: Event location
            attendees: List of attendee email addresses
            
        Returns:
            Event ID if successful, None otherwise
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return None
            
            # Build event object
            event = {
                'summary': summary,
                'description': description,
                'location': location,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            # Add attendees if provided
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            # Create event
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            logger.info(f"Created event: {summary}")
            return created_event['id']
            
        except HttpError as e:
            logger.error(f"HTTP error creating event: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return None
    
    def update_event(self, event_id: str, **kwargs) -> bool:
        """
        Update an existing event.
        
        Args:
            event_id: Event ID to update
            **kwargs: Fields to update (summary, description, start, end, etc.)
            
        Returns:
            True if successful
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            # Get existing event
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Update fields
            if 'summary' in kwargs:
                event['summary'] = kwargs['summary']
            if 'description' in kwargs:
                event['description'] = kwargs['description']
            if 'location' in kwargs:
                event['location'] = kwargs['location']
            if 'start_time' in kwargs:
                event['start'] = {
                    'dateTime': kwargs['start_time'].isoformat(),
                    'timeZone': 'UTC'
                }
            if 'end_time' in kwargs:
                event['end'] = {
                    'dateTime': kwargs['end_time'].isoformat(),
                    'timeZone': 'UTC'
                }
            
            # Update event
            self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"Updated event: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"HTTP error updating event: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete an event.
        
        Args:
            event_id: Event ID to delete
            
        Returns:
            True if successful
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            logger.info(f"Deleted event: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"HTTP error deleting event: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            return False
    
    def search_events(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for events by text query.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of matching events
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return []
            
            # Search events
            events_result = self.service.events().list(
                calendarId='primary',
                q=query,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            result = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                
                result.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'description': event.get('description', ''),
                    'start': start,
                    'location': event.get('location', '')
                })
            
            logger.info(f"Found {len(result)} events matching '{query}'")
            return result
            
        except HttpError as e:
            logger.error(f"HTTP error searching events: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            return []
    
    def get_todays_events(self) -> List[Dict]:
        """
        Get today's events.
        
        Returns:
            List of today's events
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return []
            
            # Get today's date range
            now = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=1)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            result = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                
                result.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'description': event.get('description', ''),
                    'start': start,
                    'location': event.get('location', '')
                })
            
            logger.info(f"Retrieved {len(result)} events for today")
            return result
            
        except HttpError as e:
            logger.error(f"HTTP error getting today's events: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting today's events: {e}")
            return []
    
    def create_reminder(self, title: str, reminder_time: datetime, 
                       description: str = '') -> Optional[str]:
        """
        Create a reminder (1-hour event).
        
        Args:
            title: Reminder title
            reminder_time: When to be reminded
            description: Reminder description
            
        Returns:
            Event ID if successful
        """
        end_time = reminder_time + timedelta(hours=1)
        return self.create_event(
            summary=f"⏰ {title}",
            start_time=reminder_time,
            end_time=end_time,
            description=description
        )

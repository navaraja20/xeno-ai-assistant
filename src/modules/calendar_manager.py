"""
Google Calendar Integration Module
Handles calendar sync, event management, and reminders
"""
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os.path
import pickle
from pathlib import Path
from typing import List, Dict, Optional
from core.logger import setup_logger


class CalendarManager:
    """Google Calendar integration manager"""
    
    # Google Calendar API scopes
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        """Initialize calendar manager"""
        self.logger = setup_logger("calendar.manager")
        self.service = None
        self.credentials = None
        self.token_file = Path(__file__).parent.parent.parent / "data" / "calendar_token.pickle"
        self.credentials_file = Path(__file__).parent.parent.parent / "data" / "calendar_credentials.json"
        
    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API
        
        Returns:
            True if authenticated successfully
        """
        try:
            # Check if token file exists
            if self.token_file.exists():
                with open(self.token_file, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # If credentials don't exist or are invalid, get new ones
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    if not self.credentials_file.exists():
                        self.logger.error("Calendar credentials file not found. Please download from Google Cloud Console.")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_file), self.SCOPES)
                    self.credentials = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # Build service
            self.service = build('calendar', 'v3', credentials=self.credentials)
            self.logger.info("Successfully authenticated with Google Calendar")
            return True
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False
    
    def get_upcoming_events(self, max_results: int = 10, days_ahead: int = 7) -> List[Dict]:
        """
        Get upcoming calendar events
        
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
            
            # Calculate time range
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Format events
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'description': event.get('description', ''),
                    'start': self._parse_datetime(start),
                    'end': self._parse_datetime(end),
                    'location': event.get('location', ''),
                    'attendees': event.get('attendees', []),
                    'hangout_link': event.get('hangoutLink', ''),
                    'html_link': event.get('htmlLink', '')
                })
            
            self.logger.info(f"Retrieved {len(formatted_events)} upcoming events")
            return formatted_events
            
        except Exception as e:
            self.logger.error(f"Error getting events: {e}")
            return []
    
    def get_todays_events(self) -> List[Dict]:
        """Get today's events"""
        try:
            if not self.service:
                if not self.authenticate():
                    return []
            
            # Get today's date range
            now = datetime.utcnow()
            time_min = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
            time_max = now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'start': self._parse_datetime(start),
                    'end': self._parse_datetime(event['end'].get('dateTime', event['end'].get('date'))),
                    'location': event.get('location', ''),
                })
            
            return formatted_events
            
        except Exception as e:
            self.logger.error(f"Error getting today's events: {e}")
            return []
    
    def create_event(self, summary: str, start_time: datetime, end_time: datetime,
                    description: str = '', location: str = '', attendees: List[str] = None) -> Optional[Dict]:
        """
        Create a new calendar event
        
        Args:
            summary: Event title
            start_time: Start datetime
            end_time: End datetime
            description: Event description
            location: Event location
            attendees: List of attendee emails
            
        Returns:
            Created event dictionary or None
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return None
            
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            if location:
                event['location'] = location
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            # Create event
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'
            ).execute()
            
            self.logger.info(f"Created event: {summary}")
            return {
                'id': created_event['id'],
                'summary': summary,
                'start': start_time,
                'html_link': created_event.get('htmlLink', '')
            }
            
        except Exception as e:
            self.logger.error(f"Error creating event: {e}")
            return None
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            self.logger.info(f"Deleted event: {event_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting event: {e}")
            return False
    
    def update_event(self, event_id: str, **kwargs) -> bool:
        """Update an event"""
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
                event['start']['dateTime'] = kwargs['start_time'].isoformat()
            if 'end_time' in kwargs:
                event['end']['dateTime'] = kwargs['end_time'].isoformat()
            
            # Update event
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            self.logger.info(f"Updated event: {event_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating event: {e}")
            return False
    
    def check_conflicts(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """
        Check for scheduling conflicts
        
        Args:
            start_time: Proposed start time
            end_time: Proposed end time
            
        Returns:
            List of conflicting events
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return []
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_time.isoformat() + 'Z',
                timeMax=end_time.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            conflicts = events_result.get('items', [])
            
            formatted_conflicts = []
            for event in conflicts:
                formatted_conflicts.append({
                    'summary': event.get('summary', 'No Title'),
                    'start': self._parse_datetime(event['start'].get('dateTime', event['start'].get('date'))),
                    'end': self._parse_datetime(event['end'].get('dateTime', event['end'].get('date')))
                })
            
            return formatted_conflicts
            
        except Exception as e:
            self.logger.error(f"Error checking conflicts: {e}")
            return []
    
    def _parse_datetime(self, date_str: str) -> datetime:
        """Parse datetime string"""
        try:
            # Try parsing with timezone
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                # All-day event
                return datetime.fromisoformat(date_str)
        except:
            return datetime.now()

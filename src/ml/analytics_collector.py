"""
Analytics Data Collector
Automatically collects and stores user activity data for ML training
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from src.core.logger import setup_logger


class AnalyticsCollector:
    """Collects and stores user activity data for analytics and ML"""
    
    def __init__(self, data_dir: Path = None):
        """Initialize analytics collector"""
        self.logger = setup_logger("ml.analytics_collector")
        self.data_dir = data_dir or Path(__file__).parent.parent.parent / "data" / "analytics"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Activity logs
        self.email_activities = []
        self.job_activities = []
        self.github_activities = []
        self.productivity_log = []
        
        self._load_activities()
        
        self.logger.info("Analytics Collector initialized")
    
    def log_email_opened(self, email_id: str, sender: str, subject: str, time_since_received: int):
        """Log email opened event"""
        self.email_activities.append({
            'event': 'opened',
            'email_id': email_id,
            'sender': sender,
            'subject': subject,
            'time_since_received_seconds': time_since_received,
            'timestamp': datetime.now().isoformat()
        })
        self._save_activities()
    
    def log_email_replied(self, email_id: str, time_since_received: int, response_length: int):
        """Log email replied event"""
        self.email_activities.append({
            'event': 'replied',
            'email_id': email_id,
            'time_since_received_seconds': time_since_received,
            'response_length': response_length,
            'timestamp': datetime.now().isoformat()
        })
        self._save_activities()
    
    def log_email_archived(self, email_id: str):
        """Log email archived event"""
        self.email_activities.append({
            'event': 'archived',
            'email_id': email_id,
            'timestamp': datetime.now().isoformat()
        })
        self._save_activities()
    
    def log_email_starred(self, email_id: str):
        """Log email starred event"""
        self.email_activities.append({
            'event': 'starred',
            'email_id': email_id,
            'timestamp': datetime.now().isoformat()
        })
        self._save_activities()
    
    def log_job_viewed(self, job_id: str, job_title: str, company: str, dwell_time: int):
        """Log job viewed event"""
        self.job_activities.append({
            'event': 'viewed',
            'job_id': job_id,
            'title': job_title,
            'company': company,
            'dwell_time_seconds': dwell_time,
            'timestamp': datetime.now().isoformat()
        })
        self._save_activities()
    
    def log_job_applied(self, job_id: str, job_title: str, company: str):
        """Log job application event"""
        self.job_activities.append({
            'event': 'applied',
            'job_id': job_id,
            'title': job_title,
            'company': company,
            'timestamp': datetime.now().isoformat()
        })
        self._save_activities()
    
    def log_job_saved(self, job_id: str, job_title: str):
        """Log job saved event"""
        self.job_activities.append({
            'event': 'saved',
            'job_id': job_id,
            'title': job_title,
            'timestamp': datetime.now().isoformat()
        })
        self._save_activities()
    
    def log_job_outcome(self, job_id: str, outcome: str, notes: str = ''):
        """
        Log job application outcome
        
        Args:
            job_id: Job identifier
            outcome: 'interview', 'offer', 'rejected', 'no_response'
            notes: Additional notes
        """
        self.job_activities.append({
            'event': 'outcome',
            'job_id': job_id,
            'outcome': outcome,
            'notes': notes,
            'timestamp': datetime.now().isoformat()
        })
        self._save_activities()
    
    def log_github_activity(self, repo: str, activity_type: str, details: Dict):
        """Log GitHub activity"""
        self.github_activities.append({
            'repo': repo,
            'activity_type': activity_type,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        self._save_activities()
    
    def log_productivity_session(self, task_type: str, duration: int, quality: int):
        """
        Log productivity session
        
        Args:
            task_type: Type of task (coding, email, meeting, etc.)
            duration: Duration in seconds
            quality: Self-reported quality (1-10)
        """
        now = datetime.now()
        self.productivity_log.append({
            'task_type': task_type,
            'duration_seconds': duration,
            'quality_score': quality,
            'hour': now.hour,
            'day_of_week': now.weekday(),
            'timestamp': now.isoformat()
        })
        self._save_activities()
    
    def log_command_used(self, command_type: str, source: str):
        """
        Log command usage
        
        Args:
            command_type: Type of command used
            source: Source (voice, keyboard, button)
        """
        # Could track command usage patterns
        pass
    
    def get_email_stats(self) -> Dict:
        """Get email activity statistics"""
        if not self.email_activities:
            return {}
        
        total_emails = len(self.email_activities)
        replied = sum(1 for a in self.email_activities if a['event'] == 'replied')
        starred = sum(1 for a in self.email_activities if a['event'] == 'starred')
        archived = sum(1 for a in self.email_activities if a['event'] == 'archived')
        
        # Average response time for replied emails
        reply_times = [a['time_since_received_seconds'] for a in self.email_activities if a['event'] == 'replied']
        avg_response_time = sum(reply_times) / len(reply_times) if reply_times else 0
        
        return {
            'total_activities': total_emails,
            'emails_replied': replied,
            'emails_starred': starred,
            'emails_archived': archived,
            'avg_response_time_hours': avg_response_time / 3600 if avg_response_time else 0,
            'reply_rate': replied / total_emails if total_emails else 0
        }
    
    def get_job_stats(self) -> Dict:
        """Get job activity statistics"""
        if not self.job_activities:
            return {}
        
        viewed = sum(1 for a in self.job_activities if a['event'] == 'viewed')
        applied = sum(1 for a in self.job_activities if a['event'] == 'applied')
        saved = sum(1 for a in self.job_activities if a['event'] == 'saved')
        
        # Outcomes
        interviews = sum(1 for a in self.job_activities if a.get('outcome') == 'interview')
        offers = sum(1 for a in self.job_activities if a.get('outcome') == 'offer')
        
        # Average dwell time for viewed jobs
        dwell_times = [a['dwell_time_seconds'] for a in self.job_activities if a['event'] == 'viewed' and 'dwell_time_seconds' in a]
        avg_dwell_time = sum(dwell_times) / len(dwell_times) if dwell_times else 0
        
        return {
            'jobs_viewed': viewed,
            'jobs_applied': applied,
            'jobs_saved': saved,
            'interviews_received': interviews,
            'offers_received': offers,
            'application_to_interview_rate': interviews / applied if applied else 0,
            'interview_to_offer_rate': offers / interviews if interviews else 0,
            'avg_dwell_time_seconds': avg_dwell_time
        }
    
    def get_productivity_stats(self) -> Dict:
        """Get productivity statistics"""
        if not self.productivity_log:
            return {}
        
        # By task type
        task_types = {}
        for log in self.productivity_log:
            task_type = log['task_type']
            if task_type not in task_types:
                task_types[task_type] = {'count': 0, 'total_duration': 0, 'total_quality': 0}
            
            task_types[task_type]['count'] += 1
            task_types[task_type]['total_duration'] += log['duration_seconds']
            task_types[task_type]['total_quality'] += log['quality_score']
        
        # Calculate averages
        for task_type in task_types:
            count = task_types[task_type]['count']
            task_types[task_type]['avg_duration_minutes'] = (task_types[task_type]['total_duration'] / 60) / count
            task_types[task_type]['avg_quality'] = task_types[task_type]['total_quality'] / count
        
        # Peak productivity hours
        hour_quality = {}
        for log in self.productivity_log:
            hour = log['hour']
            if hour not in hour_quality:
                hour_quality[hour] = []
            hour_quality[hour].append(log['quality_score'])
        
        peak_hours = sorted(hour_quality.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True)[:3]
        
        return {
            'total_sessions': len(self.productivity_log),
            'total_hours': sum(log['duration_seconds'] for log in self.productivity_log) / 3600,
            'avg_quality': sum(log['quality_score'] for log in self.productivity_log) / len(self.productivity_log),
            'task_type_stats': task_types,
            'peak_hours': [h[0] for h in peak_hours]
        }
    
    def get_github_stats(self) -> Dict:
        """Get GitHub activity statistics"""
        if not self.github_activities:
            return {}
        
        activity_counts = {}
        for activity in self.github_activities:
            act_type = activity['activity_type']
            activity_counts[act_type] = activity_counts.get(act_type, 0) + 1
        
        return {
            'total_activities': len(self.github_activities),
            'activity_breakdown': activity_counts
        }
    
    def export_for_ml(self) -> Dict:
        """Export data in format ready for ML training"""
        return {
            'email_activities': self.email_activities,
            'job_activities': self.job_activities,
            'github_activities': self.github_activities,
            'productivity_log': self.productivity_log
        }
    
    def _save_activities(self):
        """Save activities to disk"""
        try:
            data = {
                'email_activities': self.email_activities[-1000:],  # Keep last 1000
                'job_activities': self.job_activities[-500:],
                'github_activities': self.github_activities[-500:],
                'productivity_log': self.productivity_log[-1000:]
            }
            
            with open(self.data_dir / 'activities.json', 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save activities: {e}")
    
    def _load_activities(self):
        """Load activities from disk"""
        try:
            activity_file = self.data_dir / 'activities.json'
            if activity_file.exists():
                with open(activity_file, 'r') as f:
                    data = json.load(f)
                
                self.email_activities = data.get('email_activities', [])
                self.job_activities = data.get('job_activities', [])
                self.github_activities = data.get('github_activities', [])
                self.productivity_log = data.get('productivity_log', [])
                
                self.logger.info(f"Loaded {len(self.email_activities)} email activities, "
                               f"{len(self.job_activities)} job activities")
        except Exception as e:
            self.logger.error(f"Failed to load activities: {e}")

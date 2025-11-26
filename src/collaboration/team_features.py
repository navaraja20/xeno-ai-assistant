"""
Team Collaboration Features for XENO
Enables teams to work together with shared resources
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json
import os


@dataclass
class Team:
    """Team structure"""
    team_id: str
    name: str
    description: str
    owner: str
    members: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SharedCalendar:
    """Shared calendar for team events"""
    calendar_id: str
    team_id: str
    name: str
    description: str
    color: str
    events: List[Dict[str, Any]] = field(default_factory=list)
    permissions: Dict[str, str] = field(default_factory=dict)  # username: permission level


@dataclass
class TaskAssignment:
    """Task assignment structure"""
    task_id: str
    title: str
    description: str
    assigned_to: str
    assigned_by: str
    team_id: str
    due_date: Optional[str] = None
    priority: str = "medium"
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None


class TeamManager:
    """Manages teams and collaboration"""
    
    def __init__(self, data_dir: str = "data/teams"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.teams: Dict[str, Team] = {}
        self.load_teams()
    
    def create_team(
        self,
        team_id: str,
        name: str,
        description: str,
        owner: str
    ) -> Team:
        """Create a new team"""
        team = Team(
            team_id=team_id,
            name=name,
            description=description,
            owner=owner,
            members=[owner]
        )
        
        self.teams[team_id] = team
        self.save_teams()
        
        return team
    
    def add_member(self, team_id: str, username: str, added_by: str) -> bool:
        """Add member to team"""
        team = self.teams.get(team_id)
        if not team:
            return False
        
        # Check if requester is owner or admin
        if added_by != team.owner:
            # Check if added_by has permission
            pass
        
        if username not in team.members:
            team.members.append(username)
            self.save_teams()
        
        return True
    
    def remove_member(self, team_id: str, username: str, removed_by: str) -> bool:
        """Remove member from team"""
        team = self.teams.get(team_id)
        if not team:
            return False
        
        # Don't allow removing owner
        if username == team.owner:
            return False
        
        if username in team.members:
            team.members.remove(username)
            self.save_teams()
        
        return True
    
    def get_user_teams(self, username: str) -> List[Team]:
        """Get all teams user is member of"""
        return [
            team for team in self.teams.values()
            if username in team.members
        ]
    
    def is_team_member(self, team_id: str, username: str) -> bool:
        """Check if user is team member"""
        team = self.teams.get(team_id)
        return team and username in team.members
    
    def update_team_settings(
        self,
        team_id: str,
        settings: Dict[str, Any],
        updated_by: str
    ) -> bool:
        """Update team settings"""
        team = self.teams.get(team_id)
        if not team:
            return False
        
        # Check permission
        if updated_by != team.owner:
            return False
        
        team.settings.update(settings)
        self.save_teams()
        
        return True
    
    def save_teams(self):
        """Save teams to disk"""
        teams_file = os.path.join(self.data_dir, "teams.json")
        
        teams_data = {
            team_id: {
                "team_id": team.team_id,
                "name": team.name,
                "description": team.description,
                "owner": team.owner,
                "members": team.members,
                "created_at": team.created_at,
                "settings": team.settings
            }
            for team_id, team in self.teams.items()
        }
        
        with open(teams_file, 'w') as f:
            json.dump(teams_data, f, indent=2)
    
    def load_teams(self):
        """Load teams from disk"""
        teams_file = os.path.join(self.data_dir, "teams.json")
        
        if os.path.exists(teams_file):
            with open(teams_file, 'r') as f:
                teams_data = json.load(f)
            
            for team_id, team_dict in teams_data.items():
                self.teams[team_id] = Team(**team_dict)


class SharedCalendarManager:
    """Manages shared team calendars"""
    
    def __init__(self, data_dir: str = "data/teams"):
        self.data_dir = data_dir
        self.calendars: Dict[str, SharedCalendar] = {}
        self.load_calendars()
    
    def create_calendar(
        self,
        calendar_id: str,
        team_id: str,
        name: str,
        description: str,
        color: str = "#5865f2"
    ) -> SharedCalendar:
        """Create shared calendar"""
        calendar = SharedCalendar(
            calendar_id=calendar_id,
            team_id=team_id,
            name=name,
            description=description,
            color=color
        )
        
        self.calendars[calendar_id] = calendar
        self.save_calendars()
        
        return calendar
    
    def add_event(
        self,
        calendar_id: str,
        event: Dict[str, Any],
        created_by: str
    ) -> bool:
        """Add event to shared calendar"""
        calendar = self.calendars.get(calendar_id)
        if not calendar:
            return False
        
        # Check permission
        permission = calendar.permissions.get(created_by, "view")
        if permission not in ["edit", "admin"]:
            return False
        
        event["created_by"] = created_by
        event["created_at"] = datetime.now().isoformat()
        calendar.events.append(event)
        
        self.save_calendars()
        return True
    
    def get_team_calendars(self, team_id: str) -> List[SharedCalendar]:
        """Get all calendars for team"""
        return [
            cal for cal in self.calendars.values()
            if cal.team_id == team_id
        ]
    
    def set_permission(
        self,
        calendar_id: str,
        username: str,
        permission: str
    ) -> bool:
        """Set user permission for calendar (view/edit/admin)"""
        calendar = self.calendars.get(calendar_id)
        if not calendar:
            return False
        
        if permission not in ["view", "edit", "admin"]:
            return False
        
        calendar.permissions[username] = permission
        self.save_calendars()
        
        return True
    
    def save_calendars(self):
        """Save calendars to disk"""
        calendars_file = os.path.join(self.data_dir, "shared_calendars.json")
        
        calendars_data = {
            cal_id: {
                "calendar_id": cal.calendar_id,
                "team_id": cal.team_id,
                "name": cal.name,
                "description": cal.description,
                "color": cal.color,
                "events": cal.events,
                "permissions": cal.permissions
            }
            for cal_id, cal in self.calendars.items()
        }
        
        with open(calendars_file, 'w') as f:
            json.dump(calendars_data, f, indent=2)
    
    def load_calendars(self):
        """Load calendars from disk"""
        calendars_file = os.path.join(self.data_dir, "shared_calendars.json")
        
        if os.path.exists(calendars_file):
            with open(calendars_file, 'r') as f:
                calendars_data = json.load(f)
            
            for cal_id, cal_dict in calendars_data.items():
                self.calendars[cal_id] = SharedCalendar(**cal_dict)


class TaskDelegationManager:
    """Manages task assignments and delegation"""
    
    def __init__(self, data_dir: str = "data/teams"):
        self.data_dir = data_dir
        self.tasks: Dict[str, TaskAssignment] = {}
        self.load_tasks()
    
    def assign_task(
        self,
        task_id: str,
        title: str,
        description: str,
        assigned_to: str,
        assigned_by: str,
        team_id: str,
        due_date: Optional[str] = None,
        priority: str = "medium"
    ) -> TaskAssignment:
        """Assign task to team member"""
        task = TaskAssignment(
            task_id=task_id,
            title=title,
            description=description,
            assigned_to=assigned_to,
            assigned_by=assigned_by,
            team_id=team_id,
            due_date=due_date,
            priority=priority
        )
        
        self.tasks[task_id] = task
        self.save_tasks()
        
        return task
    
    def update_task_status(
        self,
        task_id: str,
        status: str,
        updated_by: str
    ) -> bool:
        """Update task status"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        # Check if updater is assigned user or assigner
        if updated_by not in [task.assigned_to, task.assigned_by]:
            return False
        
        task.status = status
        
        if status == "completed":
            task.completed_at = datetime.now().isoformat()
        
        self.save_tasks()
        return True
    
    def get_user_tasks(
        self,
        username: str,
        status: Optional[str] = None
    ) -> List[TaskAssignment]:
        """Get tasks assigned to user"""
        tasks = [
            task for task in self.tasks.values()
            if task.assigned_to == username
        ]
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        return tasks
    
    def get_team_tasks(
        self,
        team_id: str,
        status: Optional[str] = None
    ) -> List[TaskAssignment]:
        """Get all tasks for team"""
        tasks = [
            task for task in self.tasks.values()
            if task.team_id == team_id
        ]
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        return tasks
    
    def reassign_task(
        self,
        task_id: str,
        new_assignee: str,
        reassigned_by: str
    ) -> bool:
        """Reassign task to different user"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        # Check permission
        if reassigned_by != task.assigned_by:
            return False
        
        task.assigned_to = new_assignee
        self.save_tasks()
        
        return True
    
    def save_tasks(self):
        """Save tasks to disk"""
        tasks_file = os.path.join(self.data_dir, "task_assignments.json")
        
        tasks_data = {
            task_id: {
                "task_id": task.task_id,
                "title": task.title,
                "description": task.description,
                "assigned_to": task.assigned_to,
                "assigned_by": task.assigned_by,
                "team_id": task.team_id,
                "due_date": task.due_date,
                "priority": task.priority,
                "status": task.status,
                "created_at": task.created_at,
                "completed_at": task.completed_at
            }
            for task_id, task in self.tasks.items()
        }
        
        with open(tasks_file, 'w') as f:
            json.dump(tasks_data, f, indent=2)
    
    def load_tasks(self):
        """Load tasks from disk"""
        tasks_file = os.path.join(self.data_dir, "task_assignments.json")
        
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r') as f:
                tasks_data = json.load(f)
            
            for task_id, task_dict in tasks_data.items():
                self.tasks[task_id] = TaskAssignment(**task_dict)


class TeamAnalytics:
    """Team performance analytics"""
    
    def __init__(
        self,
        team_manager: TeamManager,
        task_manager: TaskDelegationManager
    ):
        self.team_manager = team_manager
        self.task_manager = task_manager
    
    def get_team_metrics(self, team_id: str) -> Dict[str, Any]:
        """Get team performance metrics"""
        team = self.team_manager.teams.get(team_id)
        if not team:
            return {}
        
        tasks = self.task_manager.get_team_tasks(team_id)
        
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == "completed"])
        pending_tasks = len([t for t in tasks if t.status == "pending"])
        in_progress_tasks = len([t for t in tasks if t.status == "in_progress"])
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Member activity
        member_stats = {}
        for member in team.members:
            member_tasks = self.task_manager.get_user_tasks(member)
            member_stats[member] = {
                "total_assigned": len(member_tasks),
                "completed": len([t for t in member_tasks if t.status == "completed"]),
                "pending": len([t for t in member_tasks if t.status == "pending"]),
                "in_progress": len([t for t in member_tasks if t.status == "in_progress"])
            }
        
        return {
            "team_id": team_id,
            "team_name": team.name,
            "member_count": len(team.members),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "completion_rate": round(completion_rate, 2),
            "member_stats": member_stats
        }
    
    def get_user_performance(self, username: str) -> Dict[str, Any]:
        """Get user performance across all teams"""
        teams = self.team_manager.get_user_teams(username)
        tasks = self.task_manager.get_user_tasks(username)
        
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == "completed"])
        
        # Calculate average completion time
        completion_times = []
        for task in tasks:
            if task.status == "completed" and task.completed_at:
                created = datetime.fromisoformat(task.created_at)
                completed = datetime.fromisoformat(task.completed_at)
                completion_times.append((completed - created).total_seconds() / 3600)  # hours
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        return {
            "username": username,
            "teams": [t.name for t in teams],
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": len([t for t in tasks if t.status == "pending"]),
            "completion_rate": round(completed_tasks / total_tasks * 100, 2) if total_tasks > 0 else 0,
            "avg_completion_time_hours": round(avg_completion_time, 2)
        }

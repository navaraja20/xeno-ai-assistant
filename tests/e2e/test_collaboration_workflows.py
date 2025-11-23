"""
End-to-End Collaboration Workflow Tests
Tests complete team collaboration scenarios
"""

import pytest
from pathlib import Path
import sys
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from src.collaboration.team_features import (
    TeamManager,
    SharedCalendarManager,
    TaskDelegationManager
)


@pytest.fixture
def collaboration_stack():
    """Fixture for collaboration components"""
    team_mgr = TeamManager()
    calendar_mgr = SharedCalendarManager()
    task_mgr = TaskDelegationManager()
    
    return {
        'team': team_mgr,
        'calendar': calendar_mgr,
        'task': task_mgr
    }


# ==================== Team Creation & Management ====================

def test_e2e_create_team_and_add_members(collaboration_stack):
    """E2E: Create team and add multiple members"""
    team_mgr = collaboration_stack['team']
    
    # Step 1: Create team
    team = team_mgr.create_team(
        team_id="dev_team_001",
        name="Development Team",
        description="Core development team",
        owner="alice"
    )
    
    assert team.team_id == "dev_team_001"
    assert team.owner == "alice"
    
    # Step 2: Add team members
    members = [
        ("bob", "developer"),
        ("charlie", "developer"),
        ("diana", "designer"),
        ("eve", "qa_engineer")
    ]
    
    for username, role in members:
        result = team_mgr.add_member(team.team_id, username, role)
        assert result is True
    
    # Step 3: Verify team structure
    team = team_mgr.teams[team.team_id]
    assert team.owner == "alice"
    assert len(team.members) == 5  # owner + 4 members
    assert "bob" in team.members
    assert "eve" in team.members


def test_e2e_team_member_permissions(collaboration_stack):
    """E2E: Test team member permissions and roles"""
    team_mgr = collaboration_stack['team']
    
    # Create team
    team = team_mgr.create_team(
        team_id="perm_team",
        name="Permission Test Team",
        description="Testing permissions",
        owner="owner_user"
    )
    team_id = team.team_id
    
    # Add member
    team_mgr.add_member(team_id, "member_user", "member")
    
    # Owner can update settings
    result = team_mgr.update_team_settings(
        team_id,
        {"feature_enabled": True},
        "owner_user"
    )
    assert result is True
    
    # Member cannot update settings
    result = team_mgr.update_team_settings(
        team_id,
        {"feature_enabled": False},
        "member_user"
    )
    assert result is False


def test_e2e_remove_team_member(collaboration_stack):
    """E2E: Remove member from team"""
    team_mgr = collaboration_stack['team']
    
    # Setup team
    team = team_mgr.create_team(
        team_id="remove_team",
        name="Remove Test",
        description="Test removal",
        owner="admin"
    )
    team_id = team.team_id
    team_mgr.add_member(team_id, "temp_member", "admin")
    
    # Verify member exists
    assert "temp_member" in team_mgr.teams[team_id].members
    
    # Remove member
    result = team_mgr.remove_member(team_id, "temp_member", "admin")
    assert result is True
    
    # Verify member removed
    assert "temp_member" not in team_mgr.teams[team_id].members


# ==================== Shared Calendar Workflows ====================

def test_e2e_create_shared_calendar_and_events(collaboration_stack):
    """E2E: Create shared calendar and add events"""
    team_mgr = collaboration_stack['team']
    calendar_mgr = collaboration_stack['calendar']
    
    # Step 1: Create team
    team = team_mgr.create_team(
        team_id="cal_team",
        name="Calendar Team",
        description="Team with calendar",
        owner="cal_owner"
    )
    team_id = team.team_id
    team_mgr.add_member(team_id, "cal_member", "cal_owner")
    
    # Step 2: Create shared calendar
    calendar = calendar_mgr.create_calendar(
        calendar_id="team_cal_001",
        team_id=team_id,
        name="Team Calendar",
        description="Shared team calendar"
    )
    
    assert calendar.calendar_id == "team_cal_001"
    
    # Step 3: Set permission and add events
    calendar_mgr.set_permission(calendar.calendar_id, "cal_owner", "admin")
    
    event = {
        "event_id": "meeting_001",
        "title": "Daily Standup",
        "description": "Daily team sync",
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(hours=1, minutes=30)).isoformat()
    }
    result = calendar_mgr.add_event(calendar.calendar_id, event, "cal_owner")
    assert result is True
    
    # Step 4: Verify calendar has events
    calendars = calendar_mgr.get_team_calendars(team_id)
    assert len(calendars) == 1
    assert len(calendar.events) == 1


def test_e2e_calendar_access_control(collaboration_stack):
    """E2E: Calendar access control for team members"""
    team_mgr = collaboration_stack['team']
    calendar_mgr = collaboration_stack['calendar']
    
    # Setup team
    team = team_mgr.create_team(
        team_id="access_team",
        name="Access Team",
        description="Access control test",
        owner="team_lead"
    )
    team_id = team.team_id
    team_mgr.add_member(team_id, "team_member", "team_lead")
    
    # Create calendar
    calendar = calendar_mgr.create_calendar(
        calendar_id="private_cal",
        team_id=team_id,
        name="Private Calendar",
        description="Private calendar"
    )
    
    # Set permissions
    calendar_mgr.set_permission(calendar.calendar_id, "team_member", "edit")
    
    # Team member can add event (they have edit permission)
    member_event = {
        "event_id": "member_event",
        "title": "Member Event",
        "description": "Created by member",
        "start_time": datetime.now().isoformat(),
        "end_time": (datetime.now() + timedelta(hours=1)).isoformat()
    }
    result = calendar_mgr.add_event(calendar.calendar_id, member_event, "team_member")
    assert result is True
    
    # Non-member cannot add event (no permission)
    outsider_event = {
        "event_id": "outsider_event",
        "title": "Outsider Event",
        "description": "Should fail",
        "start_time": datetime.now().isoformat(),
        "end_time": (datetime.now() + timedelta(hours=1)).isoformat()
    }
    result = calendar_mgr.add_event(calendar.calendar_id, outsider_event, "outsider")
    assert result is False


# ==================== Task Management Workflows ====================

def test_e2e_task_assignment_workflow(collaboration_stack):
    """E2E: Complete task assignment and tracking"""
    team_mgr = collaboration_stack['team']
    task_mgr = collaboration_stack['task']
    
    # Step 1: Create team
    team = team_mgr.create_team(
        team_id="task_team",
        name="Task Team",
        description="Task management team",
        owner="project_manager"
    )
    team_id = team.team_id
    team_mgr.add_member(team_id, "developer1", "project_manager")
    team_mgr.add_member(team_id, "developer2", "project_manager")
    
    # Step 2: Assign tasks
    task1 = task_mgr.assign_task(
        task_id="task_001",
        title="Implement Feature A",
        description="Build feature A with tests",
        assigned_to="developer1",
        assigned_by="project_manager",
        team_id=team_id,
        due_date=(datetime.now() + timedelta(days=7)).isoformat(),
        priority="high"
    )
    
    task2 = task_mgr.assign_task(
        task_id="task_002",
        title="Fix Bug #123",
        description="Critical bug fix",
        assigned_to="developer2",
        assigned_by="project_manager",
        team_id=team_id,
        due_date=(datetime.now() + timedelta(days=3)).isoformat(),
        priority="critical"
    )
    
    # Step 3: Verify task assignments
    dev1_tasks = task_mgr.get_user_tasks("developer1")
    assert len(dev1_tasks) == 1
    assert dev1_tasks[0].title == "Implement Feature A"
    
    dev2_tasks = task_mgr.get_user_tasks("developer2")
    assert len(dev2_tasks) == 1
    assert dev2_tasks[0].priority == "critical"


def test_e2e_task_status_progression(collaboration_stack):
    """E2E: Task status progression through workflow"""
    team_mgr = collaboration_stack['team']
    task_mgr = collaboration_stack['task']
    
    # Setup
    team = team_mgr.create_team(
        team_id="status_team",
        name="Status Team",
        description="Task status tracking",
        owner="lead"
    )
    team_id = team.team_id
    team_mgr.add_member(team_id, "worker", "lead")
    
    # Create task
    task_mgr.assign_task(
        task_id="status_task",
        title="Test Task",
        description="Task for status testing",
        assigned_to="worker",
        assigned_by="lead",
        team_id=team_id
    )
    
    # Initial status
    task = task_mgr.tasks["status_task"]
    assert task.status == "pending"
    
    # Progress through statuses (updated_by must be assigned_to or assigned_by)
    statuses = ["in_progress", "review", "completed"]
    for status in statuses:
        result = task_mgr.update_task_status("status_task", status, "worker")
        assert result is True
        assert task_mgr.tasks["status_task"].status == status


def test_e2e_task_reassignment(collaboration_stack):
    """E2E: Reassign task to different team member"""
    team_mgr = collaboration_stack['team']
    task_mgr = collaboration_stack['task']
    
    # Setup team
    team = team_mgr.create_team(
        team_id="reassign_team",
        name="Reassignment Team",
        description="Test reassignment",
        owner="manager"
    )
    team_id = team.team_id
    team_mgr.add_member(team_id, "dev_a", "manager")
    team_mgr.add_member(team_id, "dev_b", "manager")
    
    # Assign task to dev_a
    task_mgr.assign_task(
        task_id="reassign_task",
        title="Flexible Task",
        description="Can be reassigned",
        assigned_to="dev_a",
        assigned_by="manager",
        team_id=team_id
    )
    
    # Verify initial assignment
    assert task_mgr.tasks["reassign_task"].assigned_to == "dev_a"
    
    # Reassign to dev_b (must be done by assigned_by)
    result = task_mgr.reassign_task("reassign_task", "dev_b", "manager")
    assert result is True
    assert task_mgr.tasks["reassign_task"].assigned_to == "dev_b"


# ==================== Complex Multi-Component Workflows ====================

def test_e2e_complete_project_workflow(collaboration_stack):
    """E2E: Complete project workflow with team, calendar, and tasks"""
    team_mgr = collaboration_stack['team']
    calendar_mgr = collaboration_stack['calendar']
    task_mgr = collaboration_stack['task']
    
    # Phase 1: Team Setup
    team = team_mgr.create_team(
        team_id="project_alpha",
        name="Project Alpha Team",
        description="Complete project team",
        owner="project_lead"
    )
    team_id = team.team_id
    
    # Add team members
    team_mgr.add_member(team_id, "backend_dev", "project_lead")
    team_mgr.add_member(team_id, "frontend_dev", "project_lead")
    team_mgr.add_member(team_id, "qa_engineer", "project_lead")
    team_mgr.add_member(team_id, "designer", "project_lead")
    
    # Phase 2: Calendar Setup
    calendar = calendar_mgr.create_calendar(
        calendar_id="alpha_calendar",
        team_id=team_id,
        name="Alpha Project Calendar",
        description="Project Alpha calendar"
    )
    calendar_mgr.set_permission(calendar.calendar_id, "project_lead", "admin")
    
    # Add sprint planning meeting
    event = {
        "event_id": "sprint_planning",
        "title": "Sprint Planning",
        "description": "Plan next sprint",
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=1, hours=2)).isoformat()
    }
    calendar_mgr.add_event(calendar.calendar_id, event, "project_lead")
    
    # Phase 3: Task Assignment
    tasks_config = [
        ("task_backend", "API Development", "backend_dev", "high", 14),
        ("task_frontend", "UI Implementation", "frontend_dev", "high", 14),
        ("task_design", "Design System", "designer", "medium", 7),
        ("task_qa", "Test Plan", "qa_engineer", "medium", 7)
    ]
    
    for task_id, title, assignee, priority, days in tasks_config:
        task_mgr.assign_task(
            task_id=task_id,
            title=title,
            description=f"{title} for Project Alpha",
            assigned_to=assignee,
            assigned_by="project_lead",
            team_id=team_id,
            due_date=(datetime.now() + timedelta(days=days)).isoformat(),
            priority=priority
        )
    
    # Phase 4: Verification
    # Verify team size
    assert len(team_mgr.teams[team_id].members) == 5
    
    # Verify calendar
    calendars = calendar_mgr.get_team_calendars(team_id)
    assert len(calendars) == 1
    assert len(calendars[0].events) == 1
    
    # Verify tasks
    team_tasks = task_mgr.get_team_tasks(team_id)
    assert len(team_tasks) == 4
    
    # Verify task distribution
    backend_tasks = task_mgr.get_user_tasks("backend_dev")
    assert len(backend_tasks) == 1
    assert backend_tasks[0].priority == "high"


def test_e2e_sprint_workflow(collaboration_stack):
    """E2E: Complete agile sprint workflow"""
    team_mgr = collaboration_stack['team']
    calendar_mgr = collaboration_stack['calendar']
    task_mgr = collaboration_stack['task']
    
    # Setup sprint team
    team = team_mgr.create_team(
        team_id="sprint_team",
        name="Agile Sprint Team",
        description="2-week sprint team",
        owner="scrum_master"
    )
    team_id = team.team_id
    team_mgr.add_member(team_id, "developer", "scrum_master")
    
    # Sprint calendar
    calendar = calendar_mgr.create_calendar(
        calendar_id="sprint_cal",
        team_id=team_id,
        name="Sprint Calendar",
        description="Sprint ceremonies"
    )
    calendar_mgr.set_permission(calendar.calendar_id, "scrum_master", "admin")
    
    # Add sprint ceremonies
    ceremonies = [
        ("standup_mon", "Daily Standup", 1, 0.25),
        ("standup_tue", "Daily Standup", 2, 0.25),
        ("retro", "Sprint Retrospective", 14, 1),
        ("review", "Sprint Review", 14, 1.5)
    ]
    
    for event_id, title, day_offset, duration in ceremonies:
        event = {
            "event_id": event_id,
            "title": title,
            "description": f"Sprint {title}",
            "start_time": (datetime.now() + timedelta(days=day_offset)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=day_offset, hours=duration)).isoformat()
        }
        calendar_mgr.add_event(calendar.calendar_id, event, "scrum_master")
    
    # Sprint backlog
    task_mgr.assign_task(
        task_id="sprint_task",
        title="User Story #42",
        description="As a user, I want...",
        assigned_to="developer",
        assigned_by="scrum_master",
        team_id=team_id,
        due_date=(datetime.now() + timedelta(days=14)).isoformat(),
        priority="high"
    )
    
    # Simulate sprint progression (updated_by must be assigned_to or assigned_by)
    task_mgr.update_task_status("sprint_task", "in_progress", "developer")
    task_mgr.update_task_status("sprint_task", "review", "developer")
    task_mgr.update_task_status("sprint_task", "completed", "developer")
    
    # Verify sprint completion
    assert task_mgr.tasks["sprint_task"].status == "completed"
    sprint_events = calendar.events
    assert len(sprint_events) == 4

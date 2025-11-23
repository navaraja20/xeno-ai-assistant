"""
Unit tests for Team Collaboration Features
Tests team management, shared calendars, and task delegation
"""

import pytest
import os
import tempfile
import shutil
from datetime import datetime

from src.collaboration.team_features import (
    Team,
    TeamManager,
    SharedCalendar,
    SharedCalendarManager,
    TaskAssignment,
    TaskDelegationManager,
    TeamAnalytics
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for test data"""
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp)


@pytest.fixture
def team_manager(temp_dir):
    """Create TeamManager instance with temp directory"""
    return TeamManager(data_dir=temp_dir)


@pytest.fixture
def calendar_manager(temp_dir):
    """Create SharedCalendarManager instance"""
    return SharedCalendarManager(data_dir=temp_dir)


@pytest.fixture
def task_manager(temp_dir):
    """Create TaskDelegationManager instance"""
    return TaskDelegationManager(data_dir=temp_dir)


# ==================== TeamManager Tests ====================

def test_team_manager_create_team(team_manager):
    """Test creating a new team"""
    team = team_manager.create_team(
        team_id="team1",
        name="Engineering Team",
        description="Software engineering team",
        owner="alice"
    )
    
    assert team.team_id == "team1"
    assert team.name == "Engineering Team"
    assert team.owner == "alice"
    assert "alice" in team.members


def test_team_manager_add_member(team_manager):
    """Test adding member to team"""
    team_manager.create_team("team1", "Engineering", "Eng team", "alice")
    
    success = team_manager.add_member("team1", "bob", "alice")
    
    assert success
    team = team_manager.teams["team1"]
    assert "bob" in team.members


def test_team_manager_add_member_nonexistent_team(team_manager):
    """Test adding member to non-existent team"""
    success = team_manager.add_member("nonexistent", "bob", "alice")
    
    assert not success


def test_team_manager_remove_member(team_manager):
    """Test removing member from team"""
    team_manager.create_team("team1", "Engineering", "Eng team", "alice")
    team_manager.add_member("team1", "bob", "alice")
    
    success = team_manager.remove_member("team1", "bob", "alice")
    
    assert success
    team = team_manager.teams["team1"]
    assert "bob" not in team.members


def test_team_manager_cannot_remove_owner(team_manager):
    """Test that owner cannot be removed"""
    team_manager.create_team("team1", "Engineering", "Eng team", "alice")
    
    success = team_manager.remove_member("team1", "alice", "alice")
    
    assert not success


def test_team_manager_get_user_teams(team_manager):
    """Test getting all teams for a user"""
    team_manager.create_team("team1", "Team 1", "First team", "alice")
    team_manager.create_team("team2", "Team 2", "Second team", "bob")
    team_manager.add_member("team2", "alice", "bob")
    
    alice_teams = team_manager.get_user_teams("alice")
    
    assert len(alice_teams) == 2
    team_ids = [t.team_id for t in alice_teams]
    assert "team1" in team_ids
    assert "team2" in team_ids


def test_team_manager_is_team_member(team_manager):
    """Test checking team membership"""
    team_manager.create_team("team1", "Engineering", "Eng team", "alice")
    team_manager.add_member("team1", "bob", "alice")
    
    assert team_manager.is_team_member("team1", "alice")
    assert team_manager.is_team_member("team1", "bob")
    assert not team_manager.is_team_member("team1", "charlie")


def test_team_manager_update_team_settings(team_manager):
    """Test updating team settings"""
    team_manager.create_team("team1", "Engineering", "Eng team", "alice")
    
    new_settings = {"visibility": "public", "allow_invites": True}
    success = team_manager.update_team_settings("team1", new_settings, "alice")
    
    assert success
    team = team_manager.teams["team1"]
    assert team.settings["visibility"] == "public"
    assert team.settings["allow_invites"] is True


def test_team_manager_update_settings_non_owner(team_manager):
    """Test that non-owner cannot update settings"""
    team_manager.create_team("team1", "Engineering", "Eng team", "alice")
    team_manager.add_member("team1", "bob", "alice")
    
    new_settings = {"visibility": "public"}
    success = team_manager.update_team_settings("team1", new_settings, "bob")
    
    assert not success


def test_team_manager_save_and_load(team_manager):
    """Test saving and loading teams"""
    team_manager.create_team("team1", "Engineering", "Eng team", "alice")
    team_manager.add_member("team1", "bob", "alice")
    
    # Create new manager instance to test loading
    new_manager = TeamManager(data_dir=team_manager.data_dir)
    
    assert "team1" in new_manager.teams
    assert "bob" in new_manager.teams["team1"].members


# ==================== SharedCalendarManager Tests ====================

def test_calendar_manager_create_calendar(calendar_manager):
    """Test creating shared calendar"""
    calendar = calendar_manager.create_calendar(
        calendar_id="cal1",
        team_id="team1",
        name="Team Calendar",
        description="Engineering team calendar",
        color="#5865f2"
    )
    
    assert calendar.calendar_id == "cal1"
    assert calendar.team_id == "team1"
    assert calendar.name == "Team Calendar"
    assert calendar.color == "#5865f2"


def test_calendar_manager_get_team_calendars(calendar_manager):
    """Test getting calendars for a team"""
    calendar_manager.create_calendar("cal1", "team1", "Calendar 1", "First")
    calendar_manager.create_calendar("cal2", "team1", "Calendar 2", "Second")
    calendar_manager.create_calendar("cal3", "team2", "Calendar 3", "Third")
    
    team1_calendars = calendar_manager.get_team_calendars("team1")
    
    assert len(team1_calendars) == 2
    cal_ids = [c.calendar_id for c in team1_calendars]
    assert "cal1" in cal_ids
    assert "cal2" in cal_ids


def test_calendar_manager_add_event(calendar_manager):
    """Test adding event to calendar"""
    calendar = calendar_manager.create_calendar("cal1", "team1", "Calendar", "Desc")
    
    # Set permission first
    calendar.permissions["alice"] = "edit"
    
    event_data = {
        "event_id": "event1",
        "title": "Team Meeting",
        "start_time": "2024-01-15T10:00:00",
        "end_time": "2024-01-15T11:00:00",
        "description": "Weekly sync"
    }
    
    success = calendar_manager.add_event("cal1", event_data, "alice")
    
    assert success
    assert len(calendar.events) == 1
    assert calendar.events[0]["title"] == "Team Meeting"


def test_calendar_manager_add_event_no_permission(calendar_manager):
    """Test adding event without permission"""
    calendar_manager.create_calendar("cal1", "team1", "Calendar", "Desc")
    
    event_data = {"event_id": "event1", "title": "Meeting"}
    success = calendar_manager.add_event("cal1", event_data, "bob")
    
    assert not success


# ==================== TaskDelegationManager Tests ====================

def test_task_manager_assign_task(task_manager):
    """Test assigning task to user"""
    task = task_manager.assign_task(
        task_id="task1",
        title="Implement Feature X",
        description="Add new feature",
        assigned_to="bob",
        assigned_by="alice",
        team_id="team1",
        due_date="2024-02-01",
        priority="high"
    )
    
    assert task.task_id == "task1"
    assert task.title == "Implement Feature X"
    assert task.assigned_to == "bob"
    assert task.priority == "high"
    assert task.status == "pending"


def test_task_manager_get_user_tasks(task_manager):
    """Test getting tasks assigned to user"""
    task_manager.assign_task("task1", "Task 1", "Desc", "bob", "alice", "team1", "2024-02-01", "high")
    task_manager.assign_task("task2", "Task 2", "Desc", "bob", "alice", "team1", "2024-02-02", "medium")
    task_manager.assign_task("task3", "Task 3", "Desc", "charlie", "alice", "team1", "2024-02-03", "low")
    
    bob_tasks = task_manager.get_user_tasks("bob")
    
    assert len(bob_tasks) == 2
    task_ids = [t.task_id for t in bob_tasks]
    assert "task1" in task_ids
    assert "task2" in task_ids


def test_task_manager_update_task_status(task_manager):
    """Test updating task status"""
    task_manager.assign_task("task1", "Task", "Desc", "bob", "alice", "team1", "2024-02-01", "high")
    
    success = task_manager.update_task_status("task1", "in_progress", "bob")
    
    assert success
    task = task_manager.tasks["task1"]
    assert task.status == "in_progress"


def test_task_manager_get_team_tasks(task_manager):
    """Test getting all tasks for a team"""
    task_manager.assign_task("task1", "Task 1", "Desc", "bob", "alice", "team1", "2024-02-01", "high")
    task_manager.assign_task("task2", "Task 2", "Desc", "charlie", "alice", "team1", "2024-02-02", "medium")
    task_manager.assign_task("task3", "Task 3", "Desc", "eve", "dave", "team2", "2024-02-03", "low")
    
    team1_tasks = task_manager.get_team_tasks("team1")
    
    assert len(team1_tasks) == 2


def test_task_manager_get_tasks_by_status(task_manager):
    """Test filtering tasks by status"""
    task_manager.assign_task("task1", "Task 1", "Desc", "bob", "alice", "team1", "2024-02-01", "high")
    task_manager.assign_task("task2", "Task 2", "Desc", "bob", "alice", "team1", "2024-02-02", "low")
    
    task_manager.update_task_status("task1", "in_progress", "bob")
    
    pending_tasks = task_manager.get_user_tasks("bob", status="pending")
    in_progress_tasks = task_manager.get_user_tasks("bob", status="in_progress")
    
    assert len(pending_tasks) == 1
    assert len(in_progress_tasks) == 1


def test_task_manager_reassign_task(task_manager):
    """Test reassigning task to different user"""
    task_manager.assign_task("task1", "Task", "Desc", "bob", "alice", "team1", "2024-02-01", "high")
    
    success = task_manager.reassign_task("task1", "charlie", "alice")
    
    assert success
    task = task_manager.tasks["task1"]
    assert task.assigned_to == "charlie"


# ==================== TeamAnalytics Tests ====================

def test_team_analytics_basic(team_manager, task_manager):
    """Test basic team analytics creation"""
    analytics = TeamAnalytics(
        team_manager=team_manager,
        task_manager=task_manager
    )
    
    assert analytics.team_manager == team_manager
    assert analytics.task_manager == task_manager


def test_team_analytics_calculate_metrics(team_manager, task_manager):
    """Test calculating team metrics"""
    # Create team
    team_manager.create_team("team1", "Engineering", "Eng team", "alice")
    
    # Create tasks
    task_manager.assign_task("task1", "Task 1", "Desc", "bob", "alice", "team1", "2024-02-01", "high")
    task_manager.assign_task("task2", "Task 2", "Desc", "bob", "alice", "team1", "2024-02-02", "high")
    task_manager.assign_task("task3", "Task 3", "Desc", "bob", "alice", "team1", "2024-02-03", "high")
    
    # Complete one task
    task_manager.update_task_status("task1", "completed", "bob")
    
    # Get analytics
    analytics = TeamAnalytics(team_manager=team_manager, task_manager=task_manager)
    metrics = analytics.get_team_metrics("team1")
    
    assert "task_count" in metrics or "total_tasks" in metrics
    # Verify metrics are being calculated
    assert isinstance(metrics, dict)


# ==================== Integration Tests ====================

def test_team_collaboration_workflow(team_manager, calendar_manager, task_manager):
    """Test complete team collaboration workflow"""
    # 1. Create team
    team = team_manager.create_team(
        team_id="eng_team",
        name="Engineering",
        description="Engineering team",
        owner="alice"
    )
    
    # 2. Add members
    team_manager.add_member("eng_team", "bob", "alice")
    team_manager.add_member("eng_team", "charlie", "alice")
    
    # 3. Create shared calendar
    calendar = calendar_manager.create_calendar(
        calendar_id="eng_cal",
        team_id="eng_team",
        name="Engineering Calendar",
        description="Team events"
    )
    
    # 4. Add event (with permission)
    calendar.permissions["alice"] = "edit"
    event_data = {
        "event_id": "standup",
        "title": "Daily Standup",
        "start_time": "2024-01-15T09:00:00",
        "end_time": "2024-01-15T09:30:00",
        "description": "Daily sync"
    }
    success = calendar_manager.add_event("eng_cal", event_data, "alice")
    
    # 5. Create tasks
    task1 = task_manager.assign_task(
        task_id="feature_x",
        title="Build Feature X",
        description="Implement new feature",
        assigned_to="bob",
        assigned_by="alice",
        team_id="eng_team",
        due_date="2024-02-01",
        priority="high"
    )
    
    # Verify everything was created
    assert len(team.members) == 3
    assert calendar.team_id == "eng_team"
    assert success
    assert task1.assigned_to == "bob"

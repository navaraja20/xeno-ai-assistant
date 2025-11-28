# Task Statistics Plugin

Analytics plugin for XENO AI Assistant that analyzes task completion patterns.

## Description

The Task Statistics plugin provides detailed analytics on your task management:

- **Completion Rate**: Percentage of tasks completed
- **Priority Distribution**: Breakdown by priority levels
- **Tag Analysis**: Most frequently used tags
- **Average Completion Time**: How long tasks take on average
- **Daily Productivity**: Tasks completed by day of week
- **Smart Insights**: AI-generated recommendations

## Installation

1. Copy this plugin to the XENO plugins directory
2. Use the plugin manager to install: `plugin_manager.install_plugin('path/to/task_stats')`
3. Activate: `plugin_manager.activate_plugin('task_stats')`

## Usage

```python
from src.plugins import get_plugin_manager

manager = get_plugin_manager()
plugin = manager.get_plugin('task_stats')

# Analyze tasks
tasks = [
    {"title": "Task 1", "status": "completed", "priority": "high", ...},
    {"title": "Task 2", "status": "pending", "priority": "medium", ...},
]

results = plugin.analyze(tasks)
print(results['insights'])
```

## Configuration

```json
{
  "enabled": true,
  "include_archived": false
}
```

## Output Example

```json
{
  "total_tasks": 100,
  "completed_tasks": 85,
  "completion_rate": 0.85,
  "priority_distribution": {
    "high": 30,
    "medium": 50,
    "low": 20
  },
  "top_tags": {
    "work": 45,
    "personal": 30,
    "urgent": 15
  },
  "average_completion_hours": 18.5,
  "most_productive_day": "Tuesday",
  "insights": [
    "Excellent completion rate! You're staying on top of your tasks.",
    "Tasks are being completed quickly, usually within a day.",
    "You're most productive on Tuesdays."
  ]
}
```

## License

MIT

## Author

XENO Team
Plugin ID: task_stats
Version: 1.0.0

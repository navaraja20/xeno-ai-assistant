# GitHub Integration Plugin

Integration plugin for XENO AI Assistant that syncs tasks with GitHub issues.

## Description

The GitHub Integration plugin enables bidirectional sync between XENO tasks and GitHub issues:

- **Issue Sync**: Automatically sync GitHub issues as tasks
- **Task to Issue**: Create GitHub issues from tasks
- **Status Updates**: Sync task completion with issue status
- **Label Mapping**: Map task tags to GitHub labels
- **Auto-Sync**: Periodic automatic synchronization

## Installation

1. Copy this plugin to the XENO plugins directory
2. Use the plugin manager to install
3. Configure your GitHub API token
4. Activate the plugin

## Configuration

```json
{
  "api_key": "ghp_your_github_token_here",
  "repository": "username/repository",
  "sync_interval": 300,
  "auto_sync": true
}
```

### Getting a GitHub Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` scope
3. Copy the token and add to plugin configuration

## Usage

```python
from src.plugins import get_plugin_manager

manager = get_plugin_manager()
plugin = manager.get_plugin('github_integration')

# Manual sync
plugin.sync()

# Create issue from task
issue_id = plugin.create_issue(
    title="Implement new feature",
    body="Feature description...",
    labels=["enhancement", "priority:high"]
)

# Get issues
issues = plugin.get_issues()
for issue in issues:
    print(f"{issue['title']} - {issue['state']}")
```

## Features

- ✅ Sync GitHub issues to tasks
- ✅ Create issues from tasks
- ✅ Update issue status
- ✅ Label mapping
- ✅ Auto-sync on interval
- ⏳ Pull request support (coming soon)
- ⏳ Milestone tracking (coming soon)

## Permissions Required

- `tasks.read` - Read tasks
- `tasks.write` - Create/update tasks
- `network.access` - Access GitHub API

## License

MIT

## Author

XENO Team
Plugin ID: github_integration
Version: 1.0.0

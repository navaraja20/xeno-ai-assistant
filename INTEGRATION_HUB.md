# XENO Integration Hub 🔌

A powerful workflow automation system that connects XENO with 20+ external services. Build visual workflows with drag-and-drop interface, similar to Zapier or IFTTT.

## Supported Integrations 📱

### Communication
- **Slack** ✅ - Send messages, create channels, manage users
- **Discord** ✅ - Send messages, webhooks, manage roles
- **Email** (Built-in) - Gmail, Outlook integration

### Productivity
- **Notion** ✅ - Create pages, update databases, manage content
- **Trello** ✅ - Create boards, lists, cards, manage members
- **Todoist** ✅ - Create tasks, projects, labels

### Development
- **GitHub** (Browser Extension) - Repository actions, issues, PRs
- **GitLab** (Coming Soon)

### Other Services (Coming Soon)
- Asana - Project management
- Monday.com - Team collaboration
- Jira - Issue tracking
- Airtable - Database management
- Google Sheets - Spreadsheet automation
- Dropbox - File storage
- Twitter/X - Social media posting
- LinkedIn - Professional network
- Evernote - Note taking
- OneNote - Microsoft notes

## Features ✨

### Visual Workflow Builder
- **Drag-and-Drop Interface**: Build workflows visually
- **Node-Based System**: Trigger → Action(s) → Result
- **Real-Time Preview**: See workflow as you build
- **Connection Lines**: Visual data flow between nodes
- **Zoom & Pan**: Navigate large workflows easily

### Trigger Types
- ⏰ **Schedule**: Time-based triggers (daily, weekly, custom cron)
- 📨 **Webhook**: HTTP webhooks from external services
- ⚡ **Event**: Internal XENO events (email sent, task created)
- ❓ **Condition**: Conditional checks (if/else logic)
- 👆 **Manual**: Run workflows on-demand

### Action Types
- 📧 **Send Message**: Slack, Discord, Email
- 📝 **Create Content**: Notion pages, Trello cards, Todoist tasks
- 🔔 **Notify**: Desktop notifications, push notifications
- 🔄 **Data Transform**: Format, filter, transform data
- 🔁 **Loop**: Iterate over lists
- ➡️ **Conditional**: If/else branching

### Workflow Examples

**Example 1: LinkedIn Job Application Tracker**
```
Trigger: LinkedIn job application (Browser Extension)
↓
Action 1: Create Trello card in "Applications" list
↓
Action 2: Create Todoist task "Follow up in 3 days"
↓
Action 3: Send Slack message to #job-search channel
```

**Example 2: Daily Standup Automation**
```
Trigger: Schedule (Every day at 9 AM)
↓
Action 1: Get Todoist tasks for today
↓
Action 2: Get calendar events for today
↓
Action 3: Send formatted message to Discord/Slack
```

**Example 3: Email to Task**
```
Trigger: Important email received (ML prediction)
↓
Condition: If priority = "high"
↓
Action 1: Create Notion page with email content
↓
Action 2: Create Todoist task with due date
↓
Action 3: Send notification
```

## Quick Start 🚀

### 1. Install Dependencies
```bash
pip install aiohttp
```

### 2. Connect Services

#### Slack
1. Create Slack app: https://api.slack.com/apps
2. Add Bot Token Scopes:
   - `chat:write`
   - `channels:read`
   - `users:read`
3. Install to workspace
4. Copy Bot User OAuth Token

#### Notion
1. Create integration: https://www.notion.so/my-integrations
2. Copy Internal Integration Token
3. Share databases/pages with integration

#### Trello
1. Get API Key: https://trello.com/app-key
2. Generate Token (click link on API key page)
3. Copy both API Key and Token

#### Discord
1. Create application: https://discord.com/developers/applications
2. Create bot and copy token
3. Or use webhook URL for simple messages

#### Todoist
1. Go to Settings → Integrations
2. Copy API Token

### 3. Add Credentials to XENO

```python
from src.integrations import IntegrationCredentials

# Slack
slack_creds = IntegrationCredentials(
    service_name='slack',
    credential_type='api_key',
    credentials={'api_token': 'xoxb-your-token'}
)

# Notion
notion_creds = IntegrationCredentials(
    service_name='notion',
    credential_type='api_key',
    credentials={'api_token': 'secret_your-token'}
)

# Store credentials (encrypted)
# XENO will prompt for these in settings
```

### 4. Create Your First Workflow

**Option A: Visual Builder (GUI)**
1. Open XENO → Integration Hub
2. Click "New Workflow"
3. Drag "Schedule" trigger to canvas
4. Configure: Every day at 9 AM
5. Drag "Slack Message" action
6. Connect trigger to action
7. Configure message content
8. Click "Save" and "Enable"

**Option B: Code**
```python
from src.integrations import (
    Workflow, Trigger, Action,
    TriggerType, ActionType, registry
)
from src.integrations.slack_integration import SlackIntegration

# Register integration
registry.register(SlackIntegration)

# Create workflow
workflow = Workflow(
    workflow_id='daily-standup',
    name='Daily Standup',
    description='Send daily standup message',
    trigger=Trigger(
        trigger_id='schedule-1',
        trigger_type=TriggerType.SCHEDULE,
        config={'cron': '0 9 * * *'}  # 9 AM daily
    ),
    actions=[
        Action(
            action_id='slack-1',
            action_type=ActionType.API_CALL,
            service='slack',
            operation='send_message',
            parameters={
                'channel': '#general',
                'text': 'Good morning! Daily standup time.'
            }
        )
    ]
)

# Add to engine
from src.integrations import WorkflowEngine

engine = WorkflowEngine(registry)
engine.add_workflow(workflow)

# Run workflow
await engine.execute_workflow('daily-standup')
```

## Architecture 🏗️

```
┌─────────────────────────────────────────────┐
│           XENO Integration Hub              │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────┐    ┌──────────┐             │
│  │ Visual   │    │ Workflow │             │
│  │ Builder  │───▶│  Engine  │             │
│  └──────────┘    └──────────┘             │
│                       │                     │
│                       ▼                     │
│            ┌──────────────────┐            │
│            │ Integration      │            │
│            │ Registry         │            │
│            └──────────────────┘            │
│                   │                         │
│        ┌──────────┴──────────┐            │
│        ▼                      ▼             │
│   ┌─────────┐           ┌─────────┐       │
│   │  Slack  │           │ Notion  │       │
│   │   API   │           │   API   │       │
│   └─────────┘           └─────────┘       │
│                                             │
└─────────────────────────────────────────────┘
```

### Components

**IntegrationRegistry**
- Manages all service integrations
- Handles authentication
- Routes actions to correct service

**WorkflowEngine**
- Executes workflows
- Manages execution state
- Logs execution history
- Handles errors

**Visual Builder (PyQt6)**
- Drag-and-drop interface
- Node-based workflow design
- Real-time validation
- Export/import workflows

## API Reference 📚

### Creating Custom Integration

```python
from src.integrations import IntegrationBase
from typing import Dict, Any, List

class CustomIntegration(IntegrationBase):
    @property
    def service_name(self) -> str:
        return 'my_service'

    @property
    def supported_triggers(self) -> List[str]:
        return ['event_happened']

    @property
    def supported_actions(self) -> List[str]:
        return ['do_something', 'do_other']

    async def authenticate(self) -> bool:
        # Implement authentication
        return True

    async def test_connection(self) -> bool:
        # Test if service is reachable
        return True

    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == 'do_something':
            return await self.do_something(**parameters)
        raise ValueError(f"Unknown action: {action}")

    async def do_something(self, param1: str) -> Dict[str, Any]:
        # Implement action
        return {'success': True}

# Register integration
from src.integrations import registry
registry.register(CustomIntegration)
```

### Workflow Execution

```python
from src.integrations import WorkflowEngine

engine = WorkflowEngine(registry)

# Execute workflow
result = await engine.execute_workflow(
    workflow_id='my-workflow',
    context={'user_id': '123'}  # Optional context
)

# Check result
if result['success']:
    print("Workflow executed successfully")
    for action_result in result['results']:
        print(f"Action {action_result['action_id']}: {action_result['result']}")
else:
    print(f"Error: {result['error']}")

# Get execution history
history = engine.get_execution_history(workflow_id='my-workflow', limit=10)
for execution in history:
    print(f"{execution['timestamp']}: {execution['success']}")
```

## Configuration ⚙️

### Storage
Workflows and credentials are stored in:
```
data/
  integrations/
    workflows.json       # Workflow definitions
    credentials.json     # Encrypted credentials
    execution_log.json   # Execution history
```

### Security
- All API keys and tokens are encrypted at rest
- Uses `cryptography` library for AES-256 encryption
- Credentials never logged or transmitted
- Each integration has isolated credential storage

### Limits
- **Workflows**: Unlimited
- **Actions per workflow**: 50 max recommended
- **Execution history**: Last 1000 executions kept
- **Concurrent workflows**: 10 max

## Troubleshooting 🔧

### Connection Failed
```
Error: Slack API error: invalid_auth
```
**Solution**: Check API token in settings, regenerate if needed

### Workflow Not Executing
```
Warning: Workflow is disabled
```
**Solution**: Enable workflow in visual builder or via API

### Rate Limiting
```
Error: Slack API error: rate_limited
```
**Solution**: Add delays between actions, reduce execution frequency

### Missing Permissions
```
Error: Notion API error: unauthorized
```
**Solution**: Check integration has access to pages/databases

## Roadmap 🗺️

### Phase 1 (Current)
- [x] Core integration framework
- [x] 5 major integrations (Slack, Notion, Trello, Discord, Todoist)
- [x] Visual workflow builder
- [x] Basic triggers and actions

### Phase 2 (Next)
- [ ] 15 more integrations
- [ ] Advanced conditions (AND/OR logic)
- [ ] Data transformers (JSON, XML, CSV)
- [ ] Workflow templates library
- [ ] Import/export workflows

### Phase 3 (Future)
- [ ] Webhook server for receiving triggers
- [ ] Real-time workflow monitoring
- [ ] Workflow analytics dashboard
- [ ] Team collaboration (shared workflows)
- [ ] Marketplace for community workflows

## Examples 📝

See `examples/workflows/` for complete workflow examples:
- `daily_standup.json` - Daily team update
- `job_tracker.json` - Track job applications
- `email_to_tasks.json` - Convert emails to tasks
- `social_media_digest.json` - Daily social media summary
- `github_to_notion.json` - Sync GitHub issues to Notion

## Support 💬

For integration requests or issues:
- Check documentation above
- Review API limits for each service
- Ensure credentials are correct
- Check service status pages

## License 📄

Part of the XENO Personal Assistant project.

---

**Built with ❤️ for automation enthusiasts**

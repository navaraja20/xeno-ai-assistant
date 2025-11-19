"""
Workflow Manager for Integration Hub
Handles workflow persistence, templates, and execution scheduling
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from ..integrations import Workflow, Trigger, Action, WorkflowEngine, IntegrationRegistry


class WorkflowManager:
    """Manages workflow storage and templates"""
    
    def __init__(self, data_dir: str = "data/integrations"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.workflows_file = self.data_dir / "workflows.json"
        self.templates_file = self.data_dir / "templates.json"
        self.workflows: Dict[str, Workflow] = {}
        self.templates: Dict[str, Dict[str, Any]] = {}
        
        self.load_workflows()
        self.load_templates()
    
    def save_workflow(self, workflow: Workflow) -> bool:
        """Save workflow to disk"""
        try:
            self.workflows[workflow.workflow_id] = workflow
            
            # Convert workflows to dict format
            workflows_data = {
                wf_id: wf.to_dict()
                for wf_id, wf in self.workflows.items()
            }
            
            with open(self.workflows_file, 'w') as f:
                json.dump(workflows_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving workflow: {e}")
            return False
    
    def load_workflows(self) -> Dict[str, Workflow]:
        """Load workflows from disk"""
        try:
            if self.workflows_file.exists():
                with open(self.workflows_file, 'r') as f:
                    workflows_data = json.load(f)
                
                for wf_id, wf_dict in workflows_data.items():
                    self.workflows[wf_id] = Workflow.from_dict(wf_dict)
            
            return self.workflows
        except Exception as e:
            print(f"Error loading workflows: {e}")
            return {}
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete workflow"""
        try:
            if workflow_id in self.workflows:
                del self.workflows[workflow_id]
                
                workflows_data = {
                    wf_id: wf.to_dict()
                    for wf_id, wf in self.workflows.items()
                }
                
                with open(self.workflows_file, 'w') as f:
                    json.dump(workflows_data, f, indent=2)
                
                return True
            return False
        except Exception as e:
            print(f"Error deleting workflow: {e}")
            return False
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[Workflow]:
        """List all workflows"""
        return list(self.workflows.values())
    
    def export_workflow(self, workflow_id: str, file_path: str) -> bool:
        """Export workflow to JSON file"""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                return False
            
            with open(file_path, 'w') as f:
                json.dump(workflow.to_dict(), f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting workflow: {e}")
            return False
    
    def import_workflow(self, file_path: str) -> Optional[Workflow]:
        """Import workflow from JSON file"""
        try:
            with open(file_path, 'r') as f:
                workflow_dict = json.load(f)
            
            workflow = Workflow.from_dict(workflow_dict)
            self.save_workflow(workflow)
            
            return workflow
        except Exception as e:
            print(f"Error importing workflow: {e}")
            return None
    
    def save_template(self, name: str, template: Dict[str, Any]) -> bool:
        """Save workflow template"""
        try:
            self.templates[name] = template
            
            with open(self.templates_file, 'w') as f:
                json.dump(self.templates, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving template: {e}")
            return False
    
    def load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load workflow templates"""
        try:
            if self.templates_file.exists():
                with open(self.templates_file, 'r') as f:
                    self.templates = json.load(f)
            else:
                # Create default templates
                self._create_default_templates()
            
            return self.templates
        except Exception as e:
            print(f"Error loading templates: {e}")
            return {}
    
    def _create_default_templates(self):
        """Create default workflow templates"""
        default_templates = {
            'Daily Standup': {
                'description': 'Send daily standup message to team',
                'trigger': {
                    'type': 'schedule',
                    'config': {'cron': '0 9 * * 1-5'}  # 9 AM weekdays
                },
                'actions': [
                    {
                        'service': 'todoist',
                        'operation': 'get_tasks',
                        'parameters': {'filter': 'today'}
                    },
                    {
                        'service': 'slack',
                        'operation': 'send_message',
                        'parameters': {
                            'channel': '#general',
                            'text': 'Today\'s tasks: {{tasks}}'
                        }
                    }
                ]
            },
            'Job Application Tracker': {
                'description': 'Track job applications from LinkedIn',
                'trigger': {
                    'type': 'event',
                    'config': {'event': 'linkedin_application_sent'}
                },
                'actions': [
                    {
                        'service': 'trello',
                        'operation': 'create_card',
                        'parameters': {
                            'board_id': '{{board_id}}',
                            'list_id': '{{list_id}}',
                            'name': 'Application: {{company}}',
                            'desc': '{{job_title}} at {{company}}'
                        }
                    },
                    {
                        'service': 'todoist',
                        'operation': 'create_task',
                        'parameters': {
                            'content': 'Follow up: {{company}}',
                            'due_string': 'in 3 days'
                        }
                    }
                ]
            },
            'Email to Tasks': {
                'description': 'Convert important emails to tasks',
                'trigger': {
                    'type': 'event',
                    'config': {'event': 'important_email_received'}
                },
                'actions': [
                    {
                        'service': 'notion',
                        'operation': 'create_page',
                        'parameters': {
                            'parent_id': '{{database_id}}',
                            'properties': {
                                'Name': '{{email_subject}}',
                                'From': '{{email_from}}'
                            }
                        }
                    },
                    {
                        'service': 'todoist',
                        'operation': 'create_task',
                        'parameters': {
                            'content': 'Reply: {{email_subject}}',
                            'description': '{{email_body}}'
                        }
                    }
                ]
            },
            'Social Media Digest': {
                'description': 'Daily summary of social media activity',
                'trigger': {
                    'type': 'schedule',
                    'config': {'cron': '0 18 * * *'}  # 6 PM daily
                },
                'actions': [
                    {
                        'service': 'twitter',
                        'operation': 'get_mentions',
                        'parameters': {'max_results': 10}
                    },
                    {
                        'service': 'notion',
                        'operation': 'create_page',
                        'parameters': {
                            'parent_id': '{{database_id}}',
                            'properties': {
                                'Name': 'Social Digest - {{date}}',
                                'Content': '{{mentions_summary}}'
                            }
                        }
                    }
                ]
            },
            'GitHub to Notion': {
                'description': 'Sync GitHub issues to Notion',
                'trigger': {
                    'type': 'webhook',
                    'config': {'path': '/github/issues'}
                },
                'actions': [
                    {
                        'service': 'notion',
                        'operation': 'create_page',
                        'parameters': {
                            'parent_id': '{{database_id}}',
                            'properties': {
                                'Name': '{{issue_title}}',
                                'Status': '{{issue_state}}',
                                'URL': '{{issue_url}}'
                            }
                        }
                    }
                ]
            }
        }
        
        for name, template in default_templates.items():
            self.save_template(name, template)
    
    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Get template by name"""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List all template names"""
        return list(self.templates.keys())
    
    def create_workflow_from_template(
        self,
        template_name: str,
        workflow_id: str,
        workflow_name: str,
        parameters: Dict[str, Any]
    ) -> Optional[Workflow]:
        """Create workflow from template with parameter substitution"""
        template = self.get_template(template_name)
        if not template:
            return None
        
        # Substitute parameters
        template_str = json.dumps(template)
        for key, value in parameters.items():
            template_str = template_str.replace(f'{{{{{key}}}}}', str(value))
        
        template_dict = json.loads(template_str)
        
        # Create workflow
        from ..integrations import TriggerType, ActionType
        
        trigger = Trigger(
            trigger_id=f"{workflow_id}_trigger",
            trigger_type=TriggerType(template_dict['trigger']['type']),
            config=template_dict['trigger']['config']
        )
        
        actions = []
        for i, action_dict in enumerate(template_dict['actions']):
            action = Action(
                action_id=f"{workflow_id}_action_{i}",
                action_type=ActionType.API_CALL,
                service=action_dict['service'],
                operation=action_dict['operation'],
                parameters=action_dict['parameters']
            )
            actions.append(action)
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=workflow_name,
            description=template_dict['description'],
            trigger=trigger,
            actions=actions,
            enabled=True
        )
        
        self.save_workflow(workflow)
        return workflow


class WorkflowScheduler:
    """Handles scheduled workflow execution"""
    
    def __init__(self, workflow_manager: WorkflowManager, workflow_engine: WorkflowEngine):
        self.workflow_manager = workflow_manager
        self.workflow_engine = workflow_engine
        self.scheduled_tasks: Dict[str, Any] = {}
    
    def schedule_workflow(self, workflow_id: str):
        """Schedule workflow for execution based on trigger"""
        workflow = self.workflow_manager.get_workflow(workflow_id)
        if not workflow or not workflow.enabled:
            return
        
        from ..integrations import TriggerType
        
        if workflow.trigger.trigger_type == TriggerType.SCHEDULE:
            # Parse cron expression and schedule
            cron = workflow.trigger.config.get('cron')
            if cron:
                self._schedule_cron(workflow_id, cron)
    
    def _schedule_cron(self, workflow_id: str, cron: str):
        """Schedule workflow with cron expression"""
        # This would integrate with APScheduler
        # For now, just log
        print(f"Scheduling workflow {workflow_id} with cron: {cron}")
    
    async def execute_scheduled_workflow(self, workflow_id: str):
        """Execute a scheduled workflow"""
        result = await self.workflow_engine.execute_workflow(workflow_id)
        return result
    
    def cancel_workflow(self, workflow_id: str):
        """Cancel scheduled workflow"""
        if workflow_id in self.scheduled_tasks:
            # Cancel scheduled task
            del self.scheduled_tasks[workflow_id]

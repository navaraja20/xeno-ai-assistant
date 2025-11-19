"""
XENO Integration Hub - Core Integration Framework
Connects XENO with 20+ external services for workflow automation
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Types of triggers for automation"""
    SCHEDULE = "schedule"  # Time-based
    WEBHOOK = "webhook"  # HTTP webhook
    EVENT = "event"  # Internal XENO event
    CONDITION = "condition"  # Conditional check
    MANUAL = "manual"  # Manual execution


class ActionType(Enum):
    """Types of actions that can be executed"""
    API_CALL = "api_call"
    WEBHOOK = "webhook"
    EMAIL = "email"
    NOTIFICATION = "notification"
    DATA_TRANSFORM = "data_transform"
    CONDITIONAL = "conditional"
    LOOP = "loop"


@dataclass
class IntegrationCredentials:
    """Credentials for external service"""
    service_name: str
    credential_type: str  # oauth, api_key, basic_auth
    credentials: Dict[str, str]  # Encrypted in storage
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Trigger:
    """Workflow trigger definition"""
    trigger_id: str
    trigger_type: TriggerType
    config: Dict[str, Any]
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'trigger_id': self.trigger_id,
            'trigger_type': self.trigger_type.value,
            'config': self.config,
            'enabled': self.enabled
        }


@dataclass
class Action:
    """Workflow action definition"""
    action_id: str
    action_type: ActionType
    service: str
    operation: str
    parameters: Dict[str, Any]
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'action_id': self.action_id,
            'action_type': self.action_type.value,
            'service': self.service,
            'operation': self.operation,
            'parameters': self.parameters,
            'conditions': self.conditions
        }


@dataclass
class Workflow:
    """Complete automation workflow"""
    workflow_id: str
    name: str
    description: str
    trigger: Trigger
    actions: List[Action]
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    run_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'workflow_id': self.workflow_id,
            'name': self.name,
            'description': self.description,
            'trigger': self.trigger.to_dict(),
            'actions': [a.to_dict() for a in self.actions],
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat(),
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'run_count': self.run_count
        }


class IntegrationBase(ABC):
    """Base class for all service integrations"""
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        self.credentials = credentials
        self.connected = False
    
    @property
    @abstractmethod
    def service_name(self) -> str:
        """Name of the integrated service"""
        pass
    
    @property
    @abstractmethod
    def supported_triggers(self) -> List[str]:
        """List of trigger types this integration supports"""
        pass
    
    @property
    @abstractmethod
    def supported_actions(self) -> List[str]:
        """List of action types this integration supports"""
        pass
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the service"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if connection is working"""
        pass
    
    @abstractmethod
    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action on the service"""
        pass
    
    def get_available_actions(self) -> List[Dict[str, Any]]:
        """Get list of available actions with metadata"""
        return []
    
    def get_available_triggers(self) -> List[Dict[str, Any]]:
        """Get list of available triggers with metadata"""
        return []


class IntegrationRegistry:
    """Registry for managing all integrations"""
    
    def __init__(self):
        self._integrations: Dict[str, type] = {}
        self._instances: Dict[str, IntegrationBase] = {}
    
    def register(self, integration_class: type):
        """Register an integration class"""
        if not issubclass(integration_class, IntegrationBase):
            raise ValueError("Integration must inherit from IntegrationBase")
        
        instance = integration_class()
        service_name = instance.service_name
        self._integrations[service_name] = integration_class
        logger.info(f"Registered integration: {service_name}")
    
    def get_integration(self, service_name: str, credentials: Optional[IntegrationCredentials] = None) -> IntegrationBase:
        """Get integration instance"""
        if service_name not in self._integrations:
            raise ValueError(f"Integration not found: {service_name}")
        
        # Return cached instance if exists and no new credentials
        if service_name in self._instances and credentials is None:
            return self._instances[service_name]
        
        # Create new instance
        integration = self._integrations[service_name](credentials)
        self._instances[service_name] = integration
        return integration
    
    def list_integrations(self) -> List[str]:
        """List all registered integrations"""
        return list(self._integrations.keys())
    
    def get_integration_info(self, service_name: str) -> Dict[str, Any]:
        """Get information about an integration"""
        integration = self.get_integration(service_name)
        return {
            'service_name': integration.service_name,
            'supported_triggers': integration.supported_triggers,
            'supported_actions': integration.supported_actions,
            'connected': integration.connected
        }


class WorkflowEngine:
    """Engine for executing workflows"""
    
    def __init__(self, registry: IntegrationRegistry):
        self.registry = registry
        self.workflows: Dict[str, Workflow] = {}
        self.execution_log: List[Dict[str, Any]] = []
    
    def add_workflow(self, workflow: Workflow):
        """Add a workflow to the engine"""
        self.workflows[workflow.workflow_id] = workflow
        logger.info(f"Added workflow: {workflow.name}")
    
    def remove_workflow(self, workflow_id: str):
        """Remove a workflow from the engine"""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            logger.info(f"Removed workflow: {workflow_id}")
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[Workflow]:
        """List all workflows"""
        return list(self.workflows.values())
    
    async def execute_workflow(self, workflow_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a workflow"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        if not workflow.enabled:
            logger.warning(f"Workflow is disabled: {workflow.name}")
            return {'success': False, 'error': 'Workflow is disabled'}
        
        logger.info(f"Executing workflow: {workflow.name}")
        
        execution_context = context or {}
        results = []
        
        try:
            # Execute each action in sequence
            for action in workflow.actions:
                # Check conditions
                if action.conditions and not self._evaluate_conditions(action.conditions, execution_context):
                    logger.info(f"Skipping action {action.action_id} - conditions not met")
                    continue
                
                # Get integration
                integration = self.registry.get_integration(action.service)
                
                # Execute action
                result = await integration.execute_action(action.operation, action.parameters)
                
                # Store result in context for next actions
                execution_context[f'action_{action.action_id}_result'] = result
                results.append({
                    'action_id': action.action_id,
                    'success': True,
                    'result': result
                })
                
                logger.info(f"Action {action.action_id} executed successfully")
            
            # Update workflow stats
            workflow.last_run = datetime.now()
            workflow.run_count += 1
            
            # Log execution
            self._log_execution(workflow, True, results)
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'results': results,
                'executed_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            self._log_execution(workflow, False, results, str(e))
            
            return {
                'success': False,
                'workflow_id': workflow_id,
                'error': str(e),
                'executed_at': datetime.now().isoformat()
            }
    
    def _evaluate_conditions(self, conditions: List[Dict[str, Any]], context: Dict[str, Any]) -> bool:
        """Evaluate if conditions are met"""
        for condition in conditions:
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            actual_value = context.get(field)
            
            if operator == 'equals' and actual_value != value:
                return False
            elif operator == 'not_equals' and actual_value == value:
                return False
            elif operator == 'contains' and value not in str(actual_value):
                return False
            elif operator == 'greater_than' and actual_value <= value:
                return False
            elif operator == 'less_than' and actual_value >= value:
                return False
        
        return True
    
    def _log_execution(self, workflow: Workflow, success: bool, results: List[Dict], error: Optional[str] = None):
        """Log workflow execution"""
        log_entry = {
            'workflow_id': workflow.workflow_id,
            'workflow_name': workflow.name,
            'success': success,
            'results': results,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        self.execution_log.append(log_entry)
        
        # Keep only last 1000 executions
        if len(self.execution_log) > 1000:
            self.execution_log = self.execution_log[-1000:]
    
    def get_execution_history(self, workflow_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get execution history"""
        logs = self.execution_log
        
        if workflow_id:
            logs = [log for log in logs if log['workflow_id'] == workflow_id]
        
        return logs[-limit:]


# Global registry instance
registry = IntegrationRegistry()

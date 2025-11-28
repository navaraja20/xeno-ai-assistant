"""
Plugin Base Classes
Defines the base architecture for XENO plugins
"""

import json
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from src.core.logger import setup_logger


class PluginType(Enum):
    """Plugin types"""

    AUTOMATION = "automation"  # Task automation plugins
    INTEGRATION = "integration"  # External service integrations
    UI = "ui"  # User interface extensions
    ANALYTICS = "analytics"  # Analytics and reporting
    AI = "ai"  # AI-powered features
    UTILITY = "utility"  # General utilities


class PluginStatus(Enum):
    """Plugin status"""

    INACTIVE = "inactive"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


class PluginManifest:
    """Plugin metadata and configuration"""

    def __init__(
        self,
        id: str,
        name: str,
        version: str,
        author: str,
        description: str,
        plugin_type: PluginType,
        entry_point: str,
        dependencies: List[str] = None,
        permissions: List[str] = None,
        config_schema: Dict[str, Any] = None,
    ):
        self.id = id
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.plugin_type = plugin_type
        self.entry_point = entry_point
        self.dependencies = dependencies or []
        self.permissions = permissions or []
        self.config_schema = config_schema or {}

        # Runtime metadata
        self.installed_at = datetime.now()
        self.last_updated = None
        self.status = PluginStatus.INACTIVE

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "plugin_type": self.plugin_type.value,
            "entry_point": self.entry_point,
            "dependencies": self.dependencies,
            "permissions": self.permissions,
            "config_schema": self.config_schema,
            "installed_at": self.installed_at.isoformat(),
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginManifest":
        """Create from dictionary"""
        manifest = cls(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            author=data["author"],
            description=data["description"],
            plugin_type=PluginType(data["plugin_type"]),
            entry_point=data["entry_point"],
            dependencies=data.get("dependencies", []),
            permissions=data.get("permissions", []),
            config_schema=data.get("config_schema", {}),
        )

        if "installed_at" in data:
            manifest.installed_at = datetime.fromisoformat(data["installed_at"])
        if "last_updated" in data and data["last_updated"]:
            manifest.last_updated = datetime.fromisoformat(data["last_updated"])
        if "status" in data:
            manifest.status = PluginStatus(data["status"])

        return manifest


class PluginContext:
    """Context provided to plugins"""

    def __init__(self):
        self.logger = None
        self.config = {}
        self.data_dir = None
        self.api = None  # API access object

        # Event callbacks
        self._event_handlers: Dict[str, List[Callable]] = {}

    def on_event(self, event_name: str, handler: Callable):
        """Register event handler"""
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)

    def emit_event(self, event_name: str, data: Any = None):
        """Emit event to registered handlers"""
        if event_name in self._event_handlers:
            for handler in self._event_handlers[event_name]:
                try:
                    handler(data)
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Event handler error: {e}")


class PluginAPI:
    """API interface for plugins"""

    def __init__(self):
        self.logger = setup_logger("plugin.api")

        # API endpoints (to be implemented by plugin manager)
        self._task_api = None
        self._notification_api = None
        self._memory_api = None
        self._workflow_api = None
        self._analytics_api = None

    # Task API
    def create_task(self, title: str, **kwargs) -> Optional[str]:
        """Create a new task"""
        if self._task_api:
            return self._task_api.create_task(title, **kwargs)
        return None

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        if self._task_api:
            return self._task_api.get_task(task_id)
        return None

    def update_task(self, task_id: str, **kwargs) -> bool:
        """Update task"""
        if self._task_api:
            return self._task_api.update_task(task_id, **kwargs)
        return False

    def delete_task(self, task_id: str) -> bool:
        """Delete task"""
        if self._task_api:
            return self._task_api.delete_task(task_id)
        return False

    def list_tasks(self, **filters) -> List[Dict[str, Any]]:
        """List tasks with filters"""
        if self._task_api:
            return self._task_api.list_tasks(**filters)
        return []

    # Notification API
    def send_notification(self, title: str, message: str, **kwargs) -> bool:
        """Send notification"""
        if self._notification_api:
            return self._notification_api.send_notification(title, message, **kwargs)
        return False

    # Memory API
    def store_memory(self, key: str, value: Any) -> bool:
        """Store data in plugin memory"""
        if self._memory_api:
            return self._memory_api.store(key, value)
        return False

    def get_memory(self, key: str) -> Optional[Any]:
        """Retrieve data from plugin memory"""
        if self._memory_api:
            return self._memory_api.get(key)
        return None

    # Workflow API
    def execute_workflow(self, workflow_id: str, context: Dict[str, Any] = None) -> bool:
        """Execute a workflow"""
        if self._workflow_api:
            return self._workflow_api.execute(workflow_id, context)
        return False

    # Analytics API
    def track_event(self, event_name: str, properties: Dict[str, Any] = None):
        """Track analytics event"""
        if self._analytics_api:
            self._analytics_api.track(event_name, properties)


class Plugin(ABC):
    """Base plugin class"""

    def __init__(self):
        self.manifest: Optional[PluginManifest] = None
        self.context: Optional[PluginContext] = None
        self.api: Optional[PluginAPI] = None
        self.logger = setup_logger(f"plugin.{self.__class__.__name__}")

        self._is_active = False
        self._config = {}

    @abstractmethod
    def initialize(self, context: PluginContext, config: Dict[str, Any]) -> bool:
        """
        Initialize plugin

        Args:
            context: Plugin context with logger, data_dir, etc.
            config: Plugin configuration

        Returns:
            True if initialization successful
        """
        pass

    @abstractmethod
    def activate(self) -> bool:
        """
        Activate plugin

        Returns:
            True if activation successful
        """
        pass

    @abstractmethod
    def deactivate(self) -> bool:
        """
        Deactivate plugin

        Returns:
            True if deactivation successful
        """
        pass

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        if self.manifest:
            return self.manifest.to_dict()
        return {}

    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema"""
        return {}

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration"""
        # Basic validation - can be overridden
        schema = self.get_config_schema()
        if not schema:
            return True

        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in config:
                self.logger.error(f"Missing required config field: {field}")
                return False

        return True

    def on_event(self, event_name: str, data: Any = None):
        """Handle system event"""
        # Override in subclass to handle events
        pass

    @property
    def is_active(self) -> bool:
        """Check if plugin is active"""
        return self._is_active


class AutomationPlugin(Plugin):
    """Base class for automation plugins"""

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute automation

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        pass


class IntegrationPlugin(Plugin):
    """Base class for integration plugins"""

    @abstractmethod
    def connect(self) -> bool:
        """Connect to external service"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from external service"""
        pass

    @abstractmethod
    def sync(self) -> bool:
        """Sync data with external service"""
        pass


class UIPlugin(Plugin):
    """Base class for UI plugins"""

    @abstractmethod
    def render(self, parent_widget) -> Any:
        """
        Render UI component

        Args:
            parent_widget: Parent Qt widget

        Returns:
            Widget instance
        """
        pass


class AnalyticsPlugin(Plugin):
    """Base class for analytics plugins"""

    @abstractmethod
    def analyze(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze data

        Args:
            data: Data to analyze

        Returns:
            Analysis results
        """
        pass


class AIPlugin(Plugin):
    """Base class for AI plugins"""

    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """
        Process input with AI

        Args:
            input_data: Input data

        Returns:
            Processed output
        """
        pass


class UtilityPlugin(Plugin):
    """Base class for utility plugins"""

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute utility function"""
        pass

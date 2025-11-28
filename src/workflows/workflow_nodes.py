"""
Workflow Node Definitions
Pre-built node types for visual workflow automation
"""

import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from src.core.logger import setup_logger


class NodeCategory(Enum):
    """Categories of workflow nodes"""

    TRIGGER = "trigger"
    ACTION = "action"
    LOGIC = "logic"
    DATA = "data"
    INTEGRATION = "integration"
    AI = "ai"
    UTILITY = "utility"


class PortType(Enum):
    """Types of node ports"""

    EXEC = "exec"  # Execution flow
    DATA = "data"  # Data value
    BOOLEAN = "boolean"
    NUMBER = "number"
    STRING = "string"
    OBJECT = "object"
    ARRAY = "array"


class NodePort:
    """Input/Output port on a node"""

    def __init__(
        self,
        port_id: str,
        name: str,
        port_type: PortType,
        is_input: bool,
        required: bool = False,
        default_value: Any = None,
    ):
        self.port_id = port_id
        self.name = name
        self.port_type = port_type
        self.is_input = is_input
        self.required = required
        self.default_value = default_value
        self.connected_to: Optional[str] = None  # Connected port ID

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "port_id": self.port_id,
            "name": self.name,
            "port_type": self.port_type.value,
            "is_input": self.is_input,
            "required": self.required,
            "default_value": self.default_value,
            "connected_to": self.connected_to,
        }


class WorkflowNode:
    """Base class for workflow nodes"""

    def __init__(
        self,
        node_id: str,
        node_type: str,
        category: NodeCategory,
        display_name: str,
        description: str = "",
    ):
        self.node_id = node_id
        self.node_type = node_type
        self.category = category
        self.display_name = display_name
        self.description = description

        # Visual properties
        self.position = {"x": 0, "y": 0}
        self.color = "#007ACC"

        # Ports
        self.input_ports: List[NodePort] = []
        self.output_ports: List[NodePort] = []

        # Configuration
        self.config: Dict[str, Any] = {}

        # Execution state
        self.enabled = True
        self.last_executed: Optional[datetime] = None
        self.execution_count = 0
        self.error_count = 0
        self.last_error: Optional[str] = None

        self.logger = setup_logger(f"workflow.node.{node_type}")

    def add_input_port(
        self,
        port_id: str,
        name: str,
        port_type: PortType,
        required: bool = False,
        default_value: Any = None,
    ):
        """Add input port"""
        port = NodePort(port_id, name, port_type, True, required, default_value)
        self.input_ports.append(port)
        return port

    def add_output_port(self, port_id: str, name: str, port_type: PortType):
        """Add output port"""
        port = NodePort(port_id, name, port_type, False)
        self.output_ports.append(port)
        return port

    def get_input_value(self, port_id: str, context: Dict[str, Any]) -> Any:
        """Get value from input port"""
        for port in self.input_ports:
            if port.port_id == port_id:
                # Check if connected
                if port.connected_to:
                    return context.get(port.connected_to)
                # Return default value
                return port.default_value
        return None

    def set_output_value(self, port_id: str, value: Any, context: Dict[str, Any]):
        """Set value to output port"""
        for port in self.output_ports:
            if port.port_id == port_id:
                context[f"{self.node_id}.{port_id}"] = value
                return True
        return False

    def execute(self, context: Dict[str, Any]) -> bool:
        """Execute node logic (override in subclasses)"""
        try:
            self.last_executed = datetime.now()
            self.execution_count += 1

            # Default implementation
            self.logger.info(f"Executing node: {self.display_name}")
            return True

        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            self.logger.error(f"Node execution error: {e}")
            return False

    def validate(self) -> List[str]:
        """Validate node configuration"""
        errors = []

        # Check required inputs are connected
        for port in self.input_ports:
            if port.required and not port.connected_to and port.default_value is None:
                errors.append(f"Required input '{port.name}' is not connected")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "category": self.category.value,
            "display_name": self.display_name,
            "description": self.description,
            "position": self.position,
            "color": self.color,
            "input_ports": [p.to_dict() for p in self.input_ports],
            "output_ports": [p.to_dict() for p in self.output_ports],
            "config": self.config,
            "enabled": self.enabled,
            "execution_stats": {
                "last_executed": (
                    self.last_executed.isoformat() if self.last_executed else None
                ),
                "execution_count": self.execution_count,
                "error_count": self.error_count,
                "last_error": self.last_error,
            },
        }


# ===== TRIGGER NODES =====


class TimerTriggerNode(WorkflowNode):
    """Triggers workflow on a timer"""

    def __init__(self, node_id: str):
        super().__init__(
            node_id,
            "trigger.timer",
            NodeCategory.TRIGGER,
            "Timer Trigger",
            "Triggers workflow at specified intervals",
        )
        self.color = "#28A745"

        # Output: execution flow
        self.add_output_port("exec", "Execute", PortType.EXEC)
        self.add_output_port("timestamp", "Timestamp", PortType.STRING)

        # Config
        self.config = {
            "interval_seconds": 60,
            "run_once": False,
        }

    def execute(self, context: Dict[str, Any]) -> bool:
        super().execute(context)
        self.set_output_value("timestamp", datetime.now().isoformat(), context)
        return True


class EventTriggerNode(WorkflowNode):
    """Triggers workflow on events"""

    def __init__(self, node_id: str):
        super().__init__(
            node_id,
            "trigger.event",
            NodeCategory.TRIGGER,
            "Event Trigger",
            "Triggers workflow on specific events",
        )
        self.color = "#28A745"

        self.add_output_port("exec", "Execute", PortType.EXEC)
        self.add_output_port("event_data", "Event Data", PortType.OBJECT)

        self.config = {
            "event_type": "task_created",  # task_created, email_received, etc.
        }


class ManualTriggerNode(WorkflowNode):
    """Manual workflow trigger"""

    def __init__(self, node_id: str):
        super().__init__(
            node_id,
            "trigger.manual",
            NodeCategory.TRIGGER,
            "Manual Trigger",
            "Manually trigger workflow execution",
        )
        self.color = "#28A745"

        self.add_output_port("exec", "Execute", PortType.EXEC)


# ===== ACTION NODES =====


class CreateTaskNode(WorkflowNode):
    """Create a new task"""

    def __init__(self, node_id: str):
        super().__init__(
            node_id,
            "action.create_task",
            NodeCategory.ACTION,
            "Create Task",
            "Creates a new task in the system",
        )
        self.color = "#007ACC"

        self.add_input_port("exec", "Execute", PortType.EXEC, required=True)
        self.add_input_port("title", "Title", PortType.STRING, required=True)
        self.add_input_port("description", "Description", PortType.STRING)
        self.add_input_port("priority", "Priority", PortType.STRING, default_value="medium")

        self.add_output_port("exec", "Execute", PortType.EXEC)
        self.add_output_port("task_id", "Task ID", PortType.STRING)

    def execute(self, context: Dict[str, Any]) -> bool:
        super().execute(context)

        title = self.get_input_value("title", context)
        description = self.get_input_value("description", context)
        priority = self.get_input_value("priority", context)

        # TODO: Integrate with task manager
        task_id = f"task_{datetime.now().timestamp()}"

        self.logger.info(f"Created task: {title} (priority: {priority})")
        self.set_output_value("task_id", task_id, context)

        return True


class SendEmailNode(WorkflowNode):
    """Send email"""

    def __init__(self, node_id: str):
        super().__init__(
            node_id,
            "action.send_email",
            NodeCategory.ACTION,
            "Send Email",
            "Sends an email message",
        )
        self.color = "#007ACC"

        self.add_input_port("exec", "Execute", PortType.EXEC, required=True)
        self.add_input_port("to", "To", PortType.STRING, required=True)
        self.add_input_port("subject", "Subject", PortType.STRING, required=True)
        self.add_input_port("body", "Body", PortType.STRING, required=True)

        self.add_output_port("exec", "Execute", PortType.EXEC)
        self.add_output_port("success", "Success", PortType.BOOLEAN)


class SendNotificationNode(WorkflowNode):
    """Send notification"""

    def __init__(self, node_id: str):
        super().__init__(
            node_id,
            "action.send_notification",
            NodeCategory.ACTION,
            "Send Notification",
            "Sends a system notification",
        )
        self.color = "#007ACC"

        self.add_input_port("exec", "Execute", PortType.EXEC, required=True)
        self.add_input_port("title", "Title", PortType.STRING, required=True)
        self.add_input_port("message", "Message", PortType.STRING, required=True)
        self.add_input_port("priority", "Priority", PortType.STRING, default_value="normal")

        self.add_output_port("exec", "Execute", PortType.EXEC)


# ===== LOGIC NODES =====


class IfNode(WorkflowNode):
    """Conditional branch"""

    def __init__(self, node_id: str):
        super().__init__(
            node_id,
            "logic.if",
            NodeCategory.LOGIC,
            "If",
            "Conditional execution branch",
        )
        self.color = "#FFC107"

        self.add_input_port("exec", "Execute", PortType.EXEC, required=True)
        self.add_input_port("condition", "Condition", PortType.BOOLEAN, required=True)

        self.add_output_port("true", "True", PortType.EXEC)
        self.add_output_port("false", "False", PortType.EXEC)

    def execute(self, context: Dict[str, Any]) -> bool:
        super().execute(context)

        condition = self.get_input_value("condition", context)

        if condition:
            context["__next_port__"] = "true"
        else:
            context["__next_port__"] = "false"

        return True


class CompareNode(WorkflowNode):
    """Compare two values"""

    def __init__(self, node_id: str):
        super().__init__(
            node_id,
            "logic.compare",
            NodeCategory.LOGIC,
            "Compare",
            "Compares two values",
        )
        self.color = "#FFC107"

        self.add_input_port("value_a", "Value A", PortType.DATA, required=True)
        self.add_input_port("value_b", "Value B", PortType.DATA, required=True)

        self.add_output_port("result", "Result", PortType.BOOLEAN)

        self.config = {
            "operator": "==",  # ==, !=, >, <, >=, <=
        }

    def execute(self, context: Dict[str, Any]) -> bool:
        super().execute(context)

        value_a = self.get_input_value("value_a", context)
        value_b = self.get_input_value("value_b", context)
        operator = self.config.get("operator", "==")

        result = False
        if operator == "==":
            result = value_a == value_b
        elif operator == "!=":
            result = value_a != value_b
        elif operator == ">":
            result = value_a > value_b
        elif operator == "<":
            result = value_a < value_b
        elif operator == ">=":
            result = value_a >= value_b
        elif operator == "<=":
            result = value_a <= value_b

        self.set_output_value("result", result, context)
        return True


class ForEachNode(WorkflowNode):
    """Loop through array"""

    def __init__(self, node_id: str):
        super().__init__(
            node_id,
            "logic.for_each",
            NodeCategory.LOGIC,
            "For Each",
            "Iterates through array items",
        )
        self.color = "#FFC107"

        self.add_input_port("exec", "Execute", PortType.EXEC, required=True)
        self.add_input_port("array", "Array", PortType.ARRAY, required=True)

        self.add_output_port("loop_body", "Loop Body", PortType.EXEC)
        self.add_output_port("item", "Item", PortType.DATA)
        self.add_output_port("index", "Index", PortType.NUMBER)
        self.add_output_port("completed", "Completed", PortType.EXEC)


# ===== DATA NODES =====


class GetVariableNode(WorkflowNode):
    """Get variable value"""

    def __init__(self, node_id: str):
        super().__init__(
            node_id,
            "data.get_variable",
            NodeCategory.DATA,
            "Get Variable",
            "Retrieves a variable value",
        )
        self.color = "#6F42C1"

        self.add_output_port("value", "Value", PortType.DATA)

        self.config = {
            "variable_name": "",
        }

    def execute(self, context: Dict[str, Any]) -> bool:
        super().execute(context)

        var_name = self.config.get("variable_name", "")
        value = context.get(var_name)

        self.set_output_value("value", value, context)
        return True


class SetVariableNode(WorkflowNode):
    """Set variable value"""

    def __init__(self, node_id: str):
        super().__init__(
            node_id,
            "data.set_variable",
            NodeCategory.DATA,
            "Set Variable",
            "Sets a variable value",
        )
        self.color = "#6F42C1"

        self.add_input_port("exec", "Execute", PortType.EXEC, required=True)
        self.add_input_port("value", "Value", PortType.DATA, required=True)

        self.add_output_port("exec", "Execute", PortType.EXEC)

        self.config = {
            "variable_name": "",
        }

    def execute(self, context: Dict[str, Any]) -> bool:
        super().execute(context)

        var_name = self.config.get("variable_name", "")
        value = self.get_input_value("value", context)

        context[var_name] = value
        return True


class FormatStringNode(WorkflowNode):
    """Format string with variables"""

    def __init__(self, node_id: str):
        super().__init__(
            node_id,
            "data.format_string",
            NodeCategory.DATA,
            "Format String",
            "Formats a string with variables",
        )
        self.color = "#6F42C1"

        self.add_input_port("template", "Template", PortType.STRING, required=True)
        self.add_input_port("var1", "Variable 1", PortType.DATA)
        self.add_input_port("var2", "Variable 2", PortType.DATA)
        self.add_input_port("var3", "Variable 3", PortType.DATA)

        self.add_output_port("result", "Result", PortType.STRING)


# ===== AI NODES =====


class AITextGenerationNode(WorkflowNode):
    """Generate text using AI"""

    def __init__(self, node_id: str):
        super().__init__(
            node_id,
            "ai.text_generation",
            NodeCategory.AI,
            "AI Text Generation",
            "Generates text using AI model",
        )
        self.color = "#E83E8C"

        self.add_input_port("exec", "Execute", PortType.EXEC, required=True)
        self.add_input_port("prompt", "Prompt", PortType.STRING, required=True)

        self.add_output_port("exec", "Execute", PortType.EXEC)
        self.add_output_port("result", "Result", PortType.STRING)

        self.config = {
            "model": "gemini-1.5-flash",
            "max_tokens": 500,
        }


class AISentimentAnalysisNode(WorkflowNode):
    """Analyze sentiment of text"""

    def __init__(self, node_id: str):
        super().__init__(
            node_id,
            "ai.sentiment_analysis",
            NodeCategory.AI,
            "Sentiment Analysis",
            "Analyzes sentiment of text",
        )
        self.color = "#E83E8C"

        self.add_input_port("exec", "Execute", PortType.EXEC, required=True)
        self.add_input_port("text", "Text", PortType.STRING, required=True)

        self.add_output_port("exec", "Execute", PortType.EXEC)
        self.add_output_port("sentiment", "Sentiment", PortType.STRING)
        self.add_output_port("score", "Score", PortType.NUMBER)


# ===== UTILITY NODES =====


class DelayNode(WorkflowNode):
    """Delay execution"""

    def __init__(self, node_id: str):
        super().__init__(
            node_id,
            "utility.delay",
            NodeCategory.UTILITY,
            "Delay",
            "Delays execution for specified time",
        )
        self.color = "#6C757D"

        self.add_input_port("exec", "Execute", PortType.EXEC, required=True)
        self.add_input_port("seconds", "Seconds", PortType.NUMBER, default_value=1)

        self.add_output_port("exec", "Execute", PortType.EXEC)


class LogNode(WorkflowNode):
    """Log message"""

    def __init__(self, node_id: str):
        super().__init__(
            node_id,
            "utility.log",
            NodeCategory.UTILITY,
            "Log",
            "Logs a message",
        )
        self.color = "#6C757D"

        self.add_input_port("exec", "Execute", PortType.EXEC, required=True)
        self.add_input_port("message", "Message", PortType.STRING, required=True)

        self.add_output_port("exec", "Execute", PortType.EXEC)

        self.config = {
            "log_level": "info",  # debug, info, warning, error
        }

    def execute(self, context: Dict[str, Any]) -> bool:
        super().execute(context)

        message = self.get_input_value("message", context)
        log_level = self.config.get("log_level", "info")

        if log_level == "debug":
            self.logger.debug(message)
        elif log_level == "info":
            self.logger.info(message)
        elif log_level == "warning":
            self.logger.warning(message)
        elif log_level == "error":
            self.logger.error(message)

        return True


# Node registry
NODE_REGISTRY = {
    # Triggers
    "trigger.timer": TimerTriggerNode,
    "trigger.event": EventTriggerNode,
    "trigger.manual": ManualTriggerNode,
    # Actions
    "action.create_task": CreateTaskNode,
    "action.send_email": SendEmailNode,
    "action.send_notification": SendNotificationNode,
    # Logic
    "logic.if": IfNode,
    "logic.compare": CompareNode,
    "logic.for_each": ForEachNode,
    # Data
    "data.get_variable": GetVariableNode,
    "data.set_variable": SetVariableNode,
    "data.format_string": FormatStringNode,
    # AI
    "ai.text_generation": AITextGenerationNode,
    "ai.sentiment_analysis": AISentimentAnalysisNode,
    # Utility
    "utility.delay": DelayNode,
    "utility.log": LogNode,
}


def create_node(node_type: str, node_id: str = None) -> Optional[WorkflowNode]:
    """Create a node by type"""
    if node_type not in NODE_REGISTRY:
        return None

    if node_id is None:
        node_id = f"{node_type}_{datetime.now().timestamp()}"

    node_class = NODE_REGISTRY[node_type]
    return node_class(node_id)


def get_available_nodes() -> List[Dict[str, Any]]:
    """Get list of all available node types"""
    nodes = []

    for node_type, node_class in NODE_REGISTRY.items():
        # Create temporary instance to get info
        temp_node = node_class("temp")
        nodes.append({
            "node_type": node_type,
            "category": temp_node.category.value,
            "display_name": temp_node.display_name,
            "description": temp_node.description,
            "color": temp_node.color,
        })

    return nodes

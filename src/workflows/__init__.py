"""
Workflows Module
Visual workflow automation system with drag-and-drop node editor
"""

# Core workflow components
from src.workflows.workflow_engine import (
    Connection,
    Workflow,
    WorkflowExecutor,
    WorkflowManager,
    WorkflowStatus,
    get_workflow_manager,
)

# Node definitions
from src.workflows.workflow_nodes import (  # Specific node types
    AISentimentAnalysisNode,
    AITextGenerationNode,
    CompareNode,
    CreateTaskNode,
    DelayNode,
    EventTriggerNode,
    ForEachNode,
    FormatStringNode,
    GetVariableNode,
    IfNode,
    LogNode,
    ManualTriggerNode,
    NodeCategory,
    NodePort,
    PortType,
    SendEmailNode,
    SendNotificationNode,
    SetVariableNode,
    TimerTriggerNode,
    WorkflowNode,
    create_node,
    get_available_nodes,
)

# Visual studio
from src.workflows.workflow_studio import WorkflowStudio, launch_workflow_studio

# Templates
from src.workflows.workflow_templates import WorkflowTemplates

__all__ = [
    # Engine
    "Workflow",
    "WorkflowExecutor",
    "WorkflowManager",
    "WorkflowStatus",
    "Connection",
    "get_workflow_manager",
    # Nodes
    "WorkflowNode",
    "NodePort",
    "NodeCategory",
    "PortType",
    "create_node",
    "get_available_nodes",
    # Node types
    "TimerTriggerNode",
    "EventTriggerNode",
    "ManualTriggerNode",
    "CreateTaskNode",
    "SendEmailNode",
    "SendNotificationNode",
    "IfNode",
    "CompareNode",
    "ForEachNode",
    "GetVariableNode",
    "SetVariableNode",
    "FormatStringNode",
    "AITextGenerationNode",
    "AISentimentAnalysisNode",
    "DelayNode",
    "LogNode",
    # Templates
    "WorkflowTemplates",
    # Studio
    "WorkflowStudio",
    "launch_workflow_studio",
]

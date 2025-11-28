"""
Workflow Execution Engine
Executes workflows by traversing the node graph
"""

import json
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from src.core.logger import setup_logger
from src.workflows.workflow_nodes import WorkflowNode, create_node


class WorkflowStatus(Enum):
    """Workflow execution status"""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Connection:
    """Connection between two node ports"""

    def __init__(
        self,
        connection_id: str,
        from_node: str,
        from_port: str,
        to_node: str,
        to_port: str,
    ):
        self.connection_id = connection_id
        self.from_node = from_node
        self.from_port = from_port
        self.to_node = to_node
        self.to_port = to_port

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "connection_id": self.connection_id,
            "from_node": self.from_node,
            "from_port": self.from_port,
            "to_node": self.to_node,
            "to_port": self.to_port,
        }


class Workflow:
    """Workflow definition"""

    def __init__(
        self,
        workflow_id: str,
        name: str,
        description: str = "",
    ):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description

        # Graph components
        self.nodes: Dict[str, WorkflowNode] = {}
        self.connections: List[Connection] = []

        # Metadata
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.version = 1

        # Execution
        self.enabled = True
        self.execution_count = 0

    def add_node(self, node: WorkflowNode) -> bool:
        """Add node to workflow"""
        if node.node_id in self.nodes:
            return False

        self.nodes[node.node_id] = node
        self.modified_at = datetime.now()
        return True

    def remove_node(self, node_id: str) -> bool:
        """Remove node from workflow"""
        if node_id not in self.nodes:
            return False

        # Remove connections
        self.connections = [
            c for c in self.connections if c.from_node != node_id and c.to_node != node_id
        ]

        del self.nodes[node_id]
        self.modified_at = datetime.now()
        return True

    def add_connection(self, connection: Connection) -> bool:
        """Add connection between nodes"""
        # Verify nodes exist
        if connection.from_node not in self.nodes or connection.to_node not in self.nodes:
            return False

        # Update port connection info
        from_node = self.nodes[connection.from_node]
        to_node = self.nodes[connection.to_node]

        # Find ports
        from_port_obj = None
        to_port_obj = None

        for port in from_node.output_ports:
            if port.port_id == connection.from_port:
                from_port_obj = port
                break

        for port in to_node.input_ports:
            if port.port_id == connection.to_port:
                to_port_obj = port
                break

        if not from_port_obj or not to_port_obj:
            return False

        # Set connection
        to_port_obj.connected_to = f"{connection.from_node}.{connection.from_port}"

        self.connections.append(connection)
        self.modified_at = datetime.now()
        return True

    def remove_connection(self, connection_id: str) -> bool:
        """Remove connection"""
        connection = None
        for c in self.connections:
            if c.connection_id == connection_id:
                connection = c
                break

        if not connection:
            return False

        # Update port
        to_node = self.nodes.get(connection.to_node)
        if to_node:
            for port in to_node.input_ports:
                if port.port_id == connection.to_port:
                    port.connected_to = None
                    break

        self.connections.remove(connection)
        self.modified_at = datetime.now()
        return True

    def validate(self) -> List[str]:
        """Validate workflow"""
        errors = []

        # Check for nodes
        if not self.nodes:
            errors.append("Workflow has no nodes")
            return errors

        # Find trigger nodes
        trigger_nodes = [n for n in self.nodes.values() if n.category.value == "trigger"]

        if not trigger_nodes:
            errors.append("Workflow has no trigger node")

        # Validate each node
        for node in self.nodes.values():
            node_errors = node.validate()
            errors.extend([f"{node.display_name}: {e}" for e in node_errors])

        # Check for orphaned nodes
        connected_nodes = set()
        for conn in self.connections:
            connected_nodes.add(conn.from_node)
            connected_nodes.add(conn.to_node)

        for node_id in self.nodes.keys():
            if node_id not in connected_nodes and len(self.nodes) > 1:
                node = self.nodes[node_id]
                if node.category.value != "trigger":
                    errors.append(f"Node '{node.display_name}' is not connected")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "connections": [c.to_dict() for c in self.connections],
            "metadata": {
                "created_at": self.created_at.isoformat(),
                "modified_at": self.modified_at.isoformat(),
                "version": self.version,
                "enabled": self.enabled,
                "execution_count": self.execution_count,
            },
        }

    def to_json(self) -> str:
        """Export to JSON"""
        return json.dumps(self.to_dict(), indent=2)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Workflow":
        """Create workflow from dictionary"""
        workflow = Workflow(
            workflow_id=data["workflow_id"],
            name=data["name"],
            description=data.get("description", ""),
        )

        # Restore metadata
        metadata = data.get("metadata", {})
        workflow.created_at = datetime.fromisoformat(
            metadata.get("created_at", datetime.now().isoformat())
        )
        workflow.modified_at = datetime.fromisoformat(
            metadata.get("modified_at", datetime.now().isoformat())
        )
        workflow.version = metadata.get("version", 1)
        workflow.enabled = metadata.get("enabled", True)
        workflow.execution_count = metadata.get("execution_count", 0)

        # Restore nodes
        for node_id, node_data in data.get("nodes", {}).items():
            node = create_node(node_data["node_type"], node_id)
            if node:
                # Restore properties
                node.position = node_data.get("position", {"x": 0, "y": 0})
                node.color = node_data.get("color", "#007ACC")
                node.config = node_data.get("config", {})
                node.enabled = node_data.get("enabled", True)

                # Restore port connections
                for port_data in node_data.get("input_ports", []):
                    for port in node.input_ports:
                        if port.port_id == port_data["port_id"]:
                            port.connected_to = port_data.get("connected_to")
                            break

                workflow.add_node(node)

        # Restore connections
        for conn_data in data.get("connections", []):
            connection = Connection(
                connection_id=conn_data["connection_id"],
                from_node=conn_data["from_node"],
                from_port=conn_data["from_port"],
                to_node=conn_data["to_node"],
                to_port=conn_data["to_port"],
            )
            workflow.connections.append(connection)

        return workflow

    @staticmethod
    def from_json(json_str: str) -> "Workflow":
        """Import from JSON"""
        data = json.loads(json_str)
        return Workflow.from_dict(data)


class WorkflowExecutor:
    """Executes workflows"""

    def __init__(self):
        self.logger = setup_logger("workflow.executor")
        self.status = WorkflowStatus.IDLE
        self.current_workflow: Optional[Workflow] = None

        # Execution state
        self.context: Dict[str, Any] = {}
        self.execution_log: List[Dict[str, Any]] = []
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def execute(self, workflow: Workflow, initial_data: Dict[str, Any] = None) -> bool:
        """Execute workflow"""
        try:
            self.logger.info(f"Starting workflow execution: {workflow.name}")

            # Validate workflow
            errors = workflow.validate()
            if errors:
                self.logger.error(f"Workflow validation failed: {errors}")
                self.status = WorkflowStatus.FAILED
                return False

            # Initialize
            self.current_workflow = workflow
            self.status = WorkflowStatus.RUNNING
            self.context = initial_data or {}
            self.execution_log = []
            self.started_at = datetime.now()
            self.completed_at = None

            # Find trigger nodes
            trigger_nodes = [n for n in workflow.nodes.values() if n.category.value == "trigger"]

            if not trigger_nodes:
                self.logger.error("No trigger nodes found")
                self.status = WorkflowStatus.FAILED
                return False

            # Execute from each trigger
            for trigger in trigger_nodes:
                if not trigger.enabled:
                    continue

                self._execute_from_node(trigger)

            # Complete
            self.status = WorkflowStatus.COMPLETED
            self.completed_at = datetime.now()
            workflow.execution_count += 1

            duration = (self.completed_at - self.started_at).total_seconds()
            self.logger.info(f"Workflow completed in {duration:.2f}s")

            return True

        except Exception as e:
            self.logger.error(f"Workflow execution error: {e}")
            self.status = WorkflowStatus.FAILED
            self.completed_at = datetime.now()
            return False

    def _execute_from_node(self, node: WorkflowNode) -> bool:
        """Execute workflow starting from a node"""
        if not node.enabled:
            return True

        # Log execution
        self._log_node_execution(node, "started")

        # Execute node
        success = node.execute(self.context)

        if not success:
            self._log_node_execution(node, "failed")
            return False

        self._log_node_execution(node, "completed")

        # Find next nodes
        next_nodes = self._get_next_nodes(node)

        # Execute next nodes
        for next_node in next_nodes:
            self._execute_from_node(next_node)

        return True

    def _get_next_nodes(self, node: WorkflowNode) -> List[WorkflowNode]:
        """Get nodes connected to this node's output"""
        next_nodes = []

        for connection in self.current_workflow.connections:
            if connection.from_node == node.node_id:
                # Check if this is the correct output port
                # For conditional nodes, check the __next_port__ context
                next_port = self.context.get("__next_port__")
                if next_port and connection.from_port != next_port:
                    continue

                to_node = self.current_workflow.nodes.get(connection.to_node)
                if to_node and to_node.enabled:
                    next_nodes.append(to_node)

        # Clear __next_port__ context
        if "__next_port__" in self.context:
            del self.context["__next_port__"]

        return next_nodes

    def _log_node_execution(self, node: WorkflowNode, status: str):
        """Log node execution"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "node_id": node.node_id,
            "node_type": node.node_type,
            "display_name": node.display_name,
            "status": status,
        }

        if status == "failed" and node.last_error:
            log_entry["error"] = node.last_error

        self.execution_log.append(log_entry)

    def pause(self):
        """Pause execution"""
        if self.status == WorkflowStatus.RUNNING:
            self.status = WorkflowStatus.PAUSED
            self.logger.info("Workflow paused")

    def resume(self):
        """Resume execution"""
        if self.status == WorkflowStatus.PAUSED:
            self.status = WorkflowStatus.RUNNING
            self.logger.info("Workflow resumed")

    def cancel(self):
        """Cancel execution"""
        self.status = WorkflowStatus.CANCELLED
        self.completed_at = datetime.now()
        self.logger.info("Workflow cancelled")

    def get_execution_report(self) -> Dict[str, Any]:
        """Get execution report"""
        if not self.started_at:
            return {"status": "not_started"}

        duration = 0
        if self.completed_at:
            duration = (self.completed_at - self.started_at).total_seconds()

        return {
            "workflow_id": self.current_workflow.workflow_id if self.current_workflow else None,
            "workflow_name": self.current_workflow.name if self.current_workflow else None,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": duration,
            "nodes_executed": len(self.execution_log),
            "execution_log": self.execution_log,
            "context": self.context,
        }


class WorkflowManager:
    """Manages workflows"""

    def __init__(self, workflows_dir: str = "data/workflows"):
        self.logger = setup_logger("workflow.manager")
        self.workflows_dir = Path(workflows_dir)
        self.workflows_dir.mkdir(parents=True, exist_ok=True)

        # Loaded workflows
        self.workflows: Dict[str, Workflow] = {}

        # Executor
        self.executor = WorkflowExecutor()

        # Load workflows
        self._load_workflows()

    def create_workflow(self, name: str, description: str = "") -> Workflow:
        """Create new workflow"""
        workflow_id = f"workflow_{datetime.now().timestamp()}"
        workflow = Workflow(workflow_id, name, description)

        self.workflows[workflow_id] = workflow
        self._save_workflow(workflow)

        self.logger.info(f"Created workflow: {name}")
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete workflow"""
        if workflow_id not in self.workflows:
            return False

        workflow = self.workflows[workflow_id]
        del self.workflows[workflow_id]

        # Delete file
        workflow_file = self.workflows_dir / f"{workflow_id}.json"
        if workflow_file.exists():
            workflow_file.unlink()

        self.logger.info(f"Deleted workflow: {workflow.name}")
        return True

    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows"""
        return [
            {
                "workflow_id": wf.workflow_id,
                "name": wf.name,
                "description": wf.description,
                "node_count": len(wf.nodes),
                "connection_count": len(wf.connections),
                "enabled": wf.enabled,
                "execution_count": wf.execution_count,
                "modified_at": wf.modified_at.isoformat(),
            }
            for wf in self.workflows.values()
        ]

    def execute_workflow(self, workflow_id: str, initial_data: Dict[str, Any] = None) -> bool:
        """Execute workflow"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            self.logger.error(f"Workflow not found: {workflow_id}")
            return False

        if not workflow.enabled:
            self.logger.error(f"Workflow disabled: {workflow.name}")
            return False

        return self.executor.execute(workflow, initial_data)

    def _save_workflow(self, workflow: Workflow):
        """Save workflow to disk"""
        workflow_file = self.workflows_dir / f"{workflow.workflow_id}.json"

        with open(workflow_file, "w") as f:
            f.write(workflow.to_json())

    def _load_workflows(self):
        """Load workflows from disk"""
        for workflow_file in self.workflows_dir.glob("*.json"):
            try:
                with open(workflow_file, "r") as f:
                    workflow = Workflow.from_json(f.read())
                    self.workflows[workflow.workflow_id] = workflow

                self.logger.debug(f"Loaded workflow: {workflow.name}")

            except Exception as e:
                self.logger.error(f"Error loading workflow {workflow_file}: {e}")

        self.logger.info(f"Loaded {len(self.workflows)} workflows")

    def save_all(self):
        """Save all workflows"""
        for workflow in self.workflows.values():
            self._save_workflow(workflow)

        self.logger.info(f"Saved {len(self.workflows)} workflows")

    def export_workflow(self, workflow_id: str, output_file: str) -> bool:
        """Export workflow to file"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False

        with open(output_file, "w") as f:
            f.write(workflow.to_json())

        self.logger.info(f"Exported workflow to {output_file}")
        return True

    def import_workflow(self, input_file: str) -> Optional[str]:
        """Import workflow from file"""
        try:
            with open(input_file, "r") as f:
                workflow = Workflow.from_json(f.read())

            # Generate new ID to avoid conflicts
            workflow.workflow_id = f"workflow_{datetime.now().timestamp()}"

            self.workflows[workflow.workflow_id] = workflow
            self._save_workflow(workflow)

            self.logger.info(f"Imported workflow: {workflow.name}")
            return workflow.workflow_id

        except Exception as e:
            self.logger.error(f"Error importing workflow: {e}")
            return None


# Global instance
_workflow_manager: Optional[WorkflowManager] = None


def get_workflow_manager() -> WorkflowManager:
    """Get global workflow manager"""
    global _workflow_manager
    if _workflow_manager is None:
        _workflow_manager = WorkflowManager()
    return _workflow_manager

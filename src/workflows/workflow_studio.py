"""
Visual Workflow Studio
Drag-and-drop node editor for workflow creation
"""

import json
from typing import Dict, List, Optional

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsPathItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.logger import setup_logger
from src.workflows.workflow_engine import Connection, Workflow, get_workflow_manager
from src.workflows.workflow_nodes import (
    NodeCategory,
    PortType,
    WorkflowNode,
    create_node,
    get_available_nodes,
)


class PortGraphicsItem(QGraphicsEllipseItem):
    """Visual representation of a node port"""

    def __init__(self, port_id: str, port_name: str, is_input: bool, port_type: PortType):
        super().__init__(-6, -6, 12, 12)

        self.port_id = port_id
        self.port_name = port_name
        self.is_input = is_input
        self.port_type = port_type

        # Visual style
        color = QColor("#FFC107") if port_type == PortType.EXEC else QColor("#17A2B8")
        self.setBrush(QBrush(color))
        self.setPen(QPen(QColor("#FFFFFF"), 2))

        # Interaction
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # Connection tracking
        self.connections: List["ConnectionGraphicsItem"] = []

    def hoverEnterEvent(self, event):
        """Handle hover enter"""
        self.setBrush(QBrush(QColor("#FFFFFF")))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Handle hover leave"""
        color = QColor("#FFC107") if self.port_type == PortType.EXEC else QColor("#17A2B8")
        self.setBrush(QBrush(color))
        super().hoverLeaveEvent(event)


class NodeGraphicsItem(QGraphicsRectItem):
    """Visual representation of a workflow node"""

    def __init__(self, node: WorkflowNode):
        super().__init__(0, 0, 200, 100)

        self.node = node
        self.input_ports: Dict[str, PortGraphicsItem] = {}
        self.output_ports: Dict[str, PortGraphicsItem] = {}

        # Visual style
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        color = QColor(node.color)
        self.setBrush(QBrush(color.lighter(150)))
        self.setPen(QPen(color, 2))

        # Title
        self.title = QGraphicsTextItem(node.display_name, self)
        self.title.setDefaultTextColor(QColor("#FFFFFF"))
        font = QFont("Arial", 10, QFont.Weight.Bold)
        self.title.setFont(font)
        self.title.setPos(10, 5)

        # Category label
        self.category_label = QGraphicsTextItem(node.category.value.upper(), self)
        self.category_label.setDefaultTextColor(QColor("#CCCCCC"))
        font = QFont("Arial", 7)
        self.category_label.setFont(font)
        self.category_label.setPos(10, 25)

        # Create ports
        self._create_ports()

        # Set position from node
        self.setPos(node.position["x"], node.position["y"])

    def _create_ports(self):
        """Create port graphics"""
        # Input ports (left side)
        port_y = 50
        for i, port in enumerate(self.node.input_ports):
            port_item = PortGraphicsItem(port.port_id, port.name, True, port.port_type)
            port_item.setParentItem(self)
            port_item.setPos(-6, port_y + i * 20)

            self.input_ports[port.port_id] = port_item

            # Port label
            label = QGraphicsTextItem(port.name, self)
            label.setDefaultTextColor(QColor("#CCCCCC"))
            label.setFont(QFont("Arial", 8))
            label.setPos(10, port_y + i * 20 - 10)

        # Output ports (right side)
        port_y = 50
        for i, port in enumerate(self.node.output_ports):
            port_item = PortGraphicsItem(port.port_id, port.name, False, port.port_type)
            port_item.setParentItem(self)
            port_item.setPos(200 + 6, port_y + i * 20)

            self.output_ports[port.port_id] = port_item

            # Port label
            label = QGraphicsTextItem(port.name, self)
            label.setDefaultTextColor(QColor("#CCCCCC"))
            label.setFont(QFont("Arial", 8))
            label.setPos(140, port_y + i * 20 - 10)

        # Adjust height based on ports
        max_ports = max(len(self.node.input_ports), len(self.node.output_ports))
        new_height = max(100, 50 + max_ports * 20 + 20)
        self.setRect(0, 0, 200, new_height)

    def itemChange(self, change, value):
        """Handle item changes"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            # Update node position
            pos = value
            self.node.position["x"] = pos.x()
            self.node.position["y"] = pos.y()

            # Update connections
            for port in self.input_ports.values():
                for conn in port.connections:
                    conn.update_path()

            for port in self.output_ports.values():
                for conn in port.connections:
                    conn.update_path()

        return super().itemChange(change, value)

    def get_port_scene_pos(self, port_item: PortGraphicsItem) -> QPointF:
        """Get port position in scene coordinates"""
        return self.mapToScene(port_item.pos())


class ConnectionGraphicsItem(QGraphicsPathItem):
    """Visual representation of a connection"""

    def __init__(
        self,
        connection: Connection,
        from_node: NodeGraphicsItem,
        to_node: NodeGraphicsItem,
    ):
        super().__init__()

        self.connection = connection
        self.from_node = from_node
        self.to_node = to_node

        # Get port items
        self.from_port = from_node.output_ports.get(connection.from_port)
        self.to_port = to_node.input_ports.get(connection.to_port)

        # Visual style
        self.setPen(QPen(QColor("#FFFFFF"), 2))
        self.setZValue(-1)  # Behind nodes

        # Track in ports
        if self.from_port:
            self.from_port.connections.append(self)
        if self.to_port:
            self.to_port.connections.append(self)

        # Initial path
        self.update_path()

    def update_path(self):
        """Update connection path"""
        if not self.from_port or not self.to_port:
            return

        # Get positions
        start_pos = self.from_node.get_port_scene_pos(self.from_port)
        end_pos = self.to_node.get_port_scene_pos(self.to_port)

        # Create bezier curve
        path = QPainterPath(start_pos)

        # Control points for smooth curve
        dx = end_pos.x() - start_pos.x()
        ctrl1 = QPointF(start_pos.x() + dx * 0.5, start_pos.y())
        ctrl2 = QPointF(end_pos.x() - dx * 0.5, end_pos.y())

        path.cubicTo(ctrl1, ctrl2, end_pos)

        self.setPath(path)


class WorkflowCanvas(QGraphicsView):
    """Canvas for workflow editing"""

    node_selected = pyqtSignal(object)

    def __init__(self):
        super().__init__()

        self.logger = setup_logger("workflow.canvas")

        # Scene
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-2000, -2000, 4000, 4000)
        self.setScene(self.scene)

        # View settings
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        # Background
        self.setBackgroundBrush(QBrush(QColor("#2B2B2B")))

        # Tracking
        self.node_items: Dict[str, NodeGraphicsItem] = {}
        self.connection_items: Dict[str, ConnectionGraphicsItem] = {}

        # Connection creation
        self.temp_connection: Optional[QGraphicsLineItem] = None
        self.connection_start_port: Optional[PortGraphicsItem] = None

    def add_node_to_canvas(self, node: WorkflowNode, position: QPointF = None):
        """Add node to canvas"""
        if position:
            node.position["x"] = position.x()
            node.position["y"] = position.y()

        node_item = NodeGraphicsItem(node)
        self.scene.addItem(node_item)
        self.node_items[node.node_id] = node_item

        self.logger.debug(f"Added node to canvas: {node.display_name}")

    def add_connection_to_canvas(
        self, connection: Connection, from_node: WorkflowNode, to_node: WorkflowNode
    ):
        """Add connection to canvas"""
        from_item = self.node_items.get(from_node.node_id)
        to_item = self.node_items.get(to_node.node_id)

        if not from_item or not to_item:
            return

        conn_item = ConnectionGraphicsItem(connection, from_item, to_item)
        self.scene.addItem(conn_item)
        self.connection_items[connection.connection_id] = conn_item

    def clear_canvas(self):
        """Clear all items from canvas"""
        self.scene.clear()
        self.node_items.clear()
        self.connection_items.clear()

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicked on port
            item = self.itemAt(event.pos())

            if isinstance(item, PortGraphicsItem) and not item.is_input:
                # Start connection from output port
                self.connection_start_port = item
                self.temp_connection = QGraphicsLineItem()
                self.temp_connection.setPen(QPen(QColor("#FFFFFF"), 2, Qt.PenStyle.DashLine))
                self.scene.addItem(self.temp_connection)

                start_pos = item.parentItem().get_port_scene_pos(item)
                self.temp_connection.setLine(
                    start_pos.x(), start_pos.y(), start_pos.x(), start_pos.y()
                )

                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move"""
        if self.temp_connection:
            # Update temporary connection
            start_pos = self.connection_start_port.parentItem().get_port_scene_pos(
                self.connection_start_port
            )
            end_pos = self.mapToScene(event.pos())

            self.temp_connection.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())

            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if self.temp_connection:
            # Check if released on input port
            item = self.itemAt(event.pos())

            if isinstance(item, PortGraphicsItem) and item.is_input:
                # Create connection
                from_node_item = self.connection_start_port.parentItem()
                to_node_item = item.parentItem()

                # Emit signal for connection creation
                self.create_connection_signal(
                    from_node_item.node.node_id,
                    self.connection_start_port.port_id,
                    to_node_item.node.node_id,
                    item.port_id,
                )

            # Remove temporary connection
            self.scene.removeItem(self.temp_connection)
            self.temp_connection = None
            self.connection_start_port = None

            return

        super().mouseReleaseEvent(event)

    def create_connection_signal(self, from_node, from_port, to_node, to_port):
        """Signal for connection creation (override in parent)"""
        pass

    def wheelEvent(self, event):
        """Handle zoom with mouse wheel"""
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1 / zoom_factor, 1 / zoom_factor)


class WorkflowStudio(QMainWindow):
    """Main workflow studio window"""

    def __init__(self):
        super().__init__()

        self.logger = setup_logger("workflow.studio")
        self.workflow_manager = get_workflow_manager()

        # Current workflow
        self.current_workflow: Optional[Workflow] = None

        # Setup UI
        self._setup_ui()

        # Create default workflow
        self._create_new_workflow()

    def _setup_ui(self):
        """Setup user interface"""
        self.setWindowTitle("XENO Workflow Studio")
        self.setGeometry(100, 100, 1400, 800)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout
        main_layout = QHBoxLayout(central)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Node palette
        left_panel = self._create_node_palette()
        splitter.addWidget(left_panel)

        # Center panel - Canvas
        self.canvas = WorkflowCanvas()
        self.canvas.create_connection_signal = self._create_connection
        splitter.addWidget(self.canvas)

        # Right panel - Properties
        right_panel = self._create_properties_panel()
        splitter.addWidget(right_panel)

        # Set splitter sizes
        splitter.setSizes([250, 900, 250])

        main_layout.addWidget(splitter)

        # Toolbar
        self._create_toolbar()

    def _create_node_palette(self) -> QWidget:
        """Create node palette"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title
        title = QLabel("Node Palette")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Node list
        self.node_list = QListWidget()
        self.node_list.itemDoubleClicked.connect(self._add_node_from_palette)

        # Populate with available nodes
        for node_info in get_available_nodes():
            item = QListWidgetItem(node_info["display_name"])
            item.setData(Qt.ItemDataRole.UserRole, node_info)

            # Color code by category
            if node_info["category"] == "trigger":
                item.setBackground(QColor("#28A745"))
            elif node_info["category"] == "action":
                item.setBackground(QColor("#007ACC"))
            elif node_info["category"] == "logic":
                item.setBackground(QColor("#FFC107"))
            elif node_info["category"] == "ai":
                item.setBackground(QColor("#E83E8C"))

            self.node_list.addItem(item)

        layout.addWidget(self.node_list)

        return panel

    def _create_properties_panel(self) -> QWidget:
        """Create properties panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title
        title = QLabel("Properties")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Properties display
        self.properties_text = QTextEdit()
        self.properties_text.setReadOnly(True)
        layout.addWidget(self.properties_text)

        # Execution log
        log_title = QLabel("Execution Log")
        log_title.setStyleSheet("font-size: 12px; font-weight: bold; padding: 5px;")
        layout.addWidget(log_title)

        self.execution_log = QTextEdit()
        self.execution_log.setReadOnly(True)
        layout.addWidget(self.execution_log)

        return panel

    def _create_toolbar(self):
        """Create toolbar"""
        toolbar = self.addToolBar("Main")

        # New workflow
        new_btn = QPushButton("New")
        new_btn.clicked.connect(self._create_new_workflow)
        toolbar.addWidget(new_btn)

        # Save workflow
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save_workflow)
        toolbar.addWidget(save_btn)

        # Load workflow
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self._load_workflow)
        toolbar.addWidget(load_btn)

        toolbar.addSeparator()

        # Execute workflow
        execute_btn = QPushButton("Execute")
        execute_btn.clicked.connect(self._execute_workflow)
        toolbar.addWidget(execute_btn)

        # Validate workflow
        validate_btn = QPushButton("Validate")
        validate_btn.clicked.connect(self._validate_workflow)
        toolbar.addWidget(validate_btn)

        toolbar.addSeparator()

        # Export/Import
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self._export_workflow)
        toolbar.addWidget(export_btn)

        import_btn = QPushButton("Import")
        import_btn.clicked.connect(self._import_workflow)
        toolbar.addWidget(import_btn)

    def _add_node_from_palette(self, item: QListWidgetItem):
        """Add node from palette"""
        if not self.current_workflow:
            return

        node_info = item.data(Qt.ItemDataRole.UserRole)
        node = create_node(node_info["node_type"])

        if node:
            # Add to workflow
            self.current_workflow.add_node(node)

            # Add to canvas at center
            center = self.canvas.mapToScene(self.canvas.viewport().rect().center())
            self.canvas.add_node_to_canvas(node, center)

            self.logger.info(f"Added node: {node.display_name}")

    def _create_connection(self, from_node, from_port, to_node, to_port):
        """Create connection between nodes"""
        if not self.current_workflow:
            return

        connection_id = f"conn_{len(self.current_workflow.connections)}"
        connection = Connection(connection_id, from_node, from_port, to_node, to_port)

        if self.current_workflow.add_connection(connection):
            # Add to canvas
            from_node_obj = self.current_workflow.nodes[from_node]
            to_node_obj = self.current_workflow.nodes[to_node]

            self.canvas.add_connection_to_canvas(connection, from_node_obj, to_node_obj)

            self.logger.info("Created connection")

    def _create_new_workflow(self):
        """Create new workflow"""
        workflow = self.workflow_manager.create_workflow("New Workflow")
        self.current_workflow = workflow

        # Clear canvas
        self.canvas.clear_canvas()

        self.logger.info("Created new workflow")

    def _save_workflow(self):
        """Save current workflow"""
        if not self.current_workflow:
            return

        self.workflow_manager._save_workflow(self.current_workflow)
        self.logger.info("Workflow saved")

        QMessageBox.information(self, "Success", "Workflow saved successfully")

    def _load_workflow(self):
        """Load workflow"""
        workflows = self.workflow_manager.list_workflows()

        if not workflows:
            QMessageBox.information(self, "Info", "No workflows found")
            return

        # TODO: Show workflow selection dialog
        # For now, load first workflow
        workflow_id = workflows[0]["workflow_id"]
        workflow = self.workflow_manager.get_workflow(workflow_id)

        if workflow:
            self.current_workflow = workflow

            # Clear and reload canvas
            self.canvas.clear_canvas()

            # Add nodes
            for node in workflow.nodes.values():
                self.canvas.add_node_to_canvas(node)

            # Add connections
            for connection in workflow.connections:
                from_node = workflow.nodes[connection.from_node]
                to_node = workflow.nodes[connection.to_node]
                self.canvas.add_connection_to_canvas(connection, from_node, to_node)

            self.logger.info(f"Loaded workflow: {workflow.name}")

    def _execute_workflow(self):
        """Execute current workflow"""
        if not self.current_workflow:
            return

        self.execution_log.clear()
        self.execution_log.append("Starting workflow execution...\n")

        success = self.workflow_manager.execute_workflow(self.current_workflow.workflow_id)

        # Show execution log
        report = self.workflow_manager.executor.get_execution_report()

        self.execution_log.append(f"Status: {report['status']}")
        self.execution_log.append(f"Duration: {report['duration_seconds']:.2f}s")
        self.execution_log.append(f"Nodes executed: {report['nodes_executed']}\n")

        self.execution_log.append("Execution Log:")
        for entry in report["execution_log"]:
            self.execution_log.append(
                f"  [{entry['timestamp']}] {entry['display_name']}: {entry['status']}"
            )

        if success:
            QMessageBox.information(self, "Success", "Workflow executed successfully")
        else:
            QMessageBox.warning(self, "Error", "Workflow execution failed")

    def _validate_workflow(self):
        """Validate current workflow"""
        if not self.current_workflow:
            return

        errors = self.current_workflow.validate()

        if errors:
            error_text = "\n".join(errors)
            QMessageBox.warning(self, "Validation Errors", error_text)
        else:
            QMessageBox.information(self, "Success", "Workflow is valid")

    def _export_workflow(self):
        """Export workflow"""
        if not self.current_workflow:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Workflow", "", "JSON Files (*.json)"
        )

        if file_path:
            self.workflow_manager.export_workflow(self.current_workflow.workflow_id, file_path)
            QMessageBox.information(self, "Success", "Workflow exported successfully")

    def _import_workflow(self):
        """Import workflow"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Workflow", "", "JSON Files (*.json)"
        )

        if file_path:
            workflow_id = self.workflow_manager.import_workflow(file_path)
            if workflow_id:
                QMessageBox.information(self, "Success", "Workflow imported successfully")
                self._load_workflow()


def launch_workflow_studio():
    """Launch workflow studio"""
    import sys

    app = QApplication(sys.argv)
    studio = WorkflowStudio()
    studio.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch_workflow_studio()

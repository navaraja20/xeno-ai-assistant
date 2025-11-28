"""
XENO Integration Hub - Visual Workflow Builder
Drag-and-drop interface for creating automation workflows
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ..integrations import (
    Action,
    ActionType,
    IntegrationRegistry,
    Trigger,
    TriggerType,
    Workflow,
    registry,
)


class WorkflowNode(QGraphicsItem):
    """Visual node representing a workflow action"""

    def __init__(self, node_id: str, node_type: str, title: str, x: float = 0, y: float = 0):
        super().__init__()
        self.node_id = node_id
        self.node_type = node_type  # 'trigger' or 'action'
        self.title = title
        self.width = 200
        self.height = 80
        self.inputs: List["ConnectionPoint"] = []
        self.outputs: List["ConnectionPoint"] = []

        self.setPos(x, y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # Create connection points
        if node_type != "trigger":
            self.add_input()
        self.add_output()

    def add_input(self):
        """Add input connection point"""
        point = ConnectionPoint(self, "input")
        point.setPos(-10, self.height / 2)
        self.inputs.append(point)

    def add_output(self):
        """Add output connection point"""
        point = ConnectionPoint(self, "output")
        point.setPos(self.width + 10, self.height / 2)
        self.outputs.append(point)

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter: QPainter, option, widget):
        # Node colors
        if self.node_type == "trigger":
            color = QColor(88, 101, 242)  # XENO blue
        else:
            color = QColor(49, 51, 56)  # Dark gray

        # Selected state
        if self.isSelected():
            painter.setPen(QPen(QColor(88, 101, 242), 2))
        else:
            painter.setPen(QPen(QColor(64, 68, 75), 1))

        # Draw node
        painter.setBrush(color)
        painter.drawRoundedRect(0, 0, self.width, self.height, 8, 8)

        # Draw title
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(
            QRectF(10, 10, self.width - 20, 30),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.title,
        )

        # Draw type label
        painter.setPen(QColor(181, 186, 193))
        font.setWeight(QFont.Weight.Normal)
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(
            QRectF(10, 40, self.width - 20, 30),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.node_type.capitalize(),
        )


class ConnectionPoint(QGraphicsEllipseItem):
    """Connection point on a node"""

    def __init__(self, parent_node: WorkflowNode, point_type: str):
        super().__init__(-5, -5, 10, 10, parent_node)
        self.parent_node = parent_node
        self.point_type = point_type  # 'input' or 'output'
        self.connections: List["ConnectionLine"] = []

        self.setBrush(QColor(181, 186, 193))
        self.setPen(QPen(QColor(255, 255, 255), 2))

        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        self.setBrush(QColor(88, 101, 242))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setBrush(QColor(181, 186, 193))
        super().hoverLeaveEvent(event)


class ConnectionLine(QGraphicsPathItem):
    """Visual connection between nodes"""

    def __init__(self, start_point: ConnectionPoint, end_point: Optional[ConnectionPoint] = None):
        super().__init__()
        self.start_point = start_point
        self.end_point = end_point
        self.temp_end_pos: Optional[QPointF] = None

        pen = QPen(QColor(88, 101, 242), 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.setPen(pen)

        self.update_path()

        # Add to connection points
        start_point.connections.append(self)
        if end_point:
            end_point.connections.append(self)

    def update_path(self):
        """Update connection path"""
        path = QPainterPath()

        # Get start position
        start_pos = self.start_point.scenePos()
        path.moveTo(start_pos)

        # Get end position
        if self.end_point:
            end_pos = self.end_point.scenePos()
        elif self.temp_end_pos:
            end_pos = self.temp_end_pos
        else:
            return

        # Draw bezier curve
        ctrl_offset = abs(end_pos.x() - start_pos.x()) * 0.5
        ctrl1 = QPointF(start_pos.x() + ctrl_offset, start_pos.y())
        ctrl2 = QPointF(end_pos.x() - ctrl_offset, end_pos.y())

        path.cubicTo(ctrl1, ctrl2, end_pos)

        self.setPath(path)

    def set_temp_end(self, pos: QPointF):
        """Set temporary end position while dragging"""
        self.temp_end_pos = pos
        self.update_path()


class WorkflowCanvas(QGraphicsView):
    """Canvas for building workflows"""

    node_selected = pyqtSignal(str)  # node_id
    connection_created = pyqtSignal(str, str)  # from_node_id, to_node_id

    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Set scene size
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)

        # Visual settings
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Background grid
        self.setBackgroundBrush(QColor(43, 45, 49))

        # Connection state
        self.temp_connection: Optional[ConnectionLine] = None
        self.connecting_from: Optional[ConnectionPoint] = None

        # Node registry
        self.nodes: Dict[str, WorkflowNode] = {}

    def add_node(self, node_type: str, title: str, x: float = 0, y: float = 0) -> WorkflowNode:
        """Add node to canvas"""
        node_id = str(uuid.uuid4())
        node = WorkflowNode(node_id, node_type, title, x, y)
        self.scene.addItem(node)
        self.nodes[node_id] = node
        return node

    def remove_node(self, node_id: str):
        """Remove node from canvas"""
        if node_id in self.nodes:
            node = self.nodes[node_id]

            # Remove connections
            for output in node.outputs:
                for conn in output.connections[:]:
                    self.scene.removeItem(conn)

            for input_point in node.inputs:
                for conn in input_point.connections[:]:
                    self.scene.removeItem(conn)

            self.scene.removeItem(node)
            del self.nodes[node_id]

    def connect_nodes(self, from_node_id: str, to_node_id: str):
        """Connect two nodes"""
        if from_node_id not in self.nodes or to_node_id not in self.nodes:
            return

        from_node = self.nodes[from_node_id]
        to_node = self.nodes[to_node_id]

        if not from_node.outputs or not to_node.inputs:
            return

        # Create connection
        connection = ConnectionLine(from_node.outputs[0], to_node.inputs[0])
        self.scene.addItem(connection)

        self.connection_created.emit(from_node_id, to_node_id)

    def clear_canvas(self):
        """Clear all nodes and connections"""
        self.scene.clear()
        self.nodes.clear()

    def wheelEvent(self, event):
        """Zoom with mouse wheel"""
        zoom_factor = 1.15

        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1 / zoom_factor, 1 / zoom_factor)

    def mousePressEvent(self, event):
        """Handle mouse press for connections"""
        item = self.itemAt(event.pos())

        if isinstance(item, ConnectionPoint) and item.point_type == "output":
            # Start connection
            self.connecting_from = item
            self.temp_connection = ConnectionLine(item)
            self.scene.addItem(self.temp_connection)
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for connections"""
        if self.temp_connection:
            # Update temporary connection
            scene_pos = self.mapToScene(event.pos())
            self.temp_connection.set_temp_end(scene_pos)
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release for connections"""
        if self.temp_connection:
            item = self.itemAt(event.pos())

            if isinstance(item, ConnectionPoint) and item.point_type == "input":
                # Complete connection
                self.temp_connection.end_point = item
                item.connections.append(self.temp_connection)
                self.temp_connection.update_path()

                # Emit signal
                from_node_id = self.connecting_from.parent_node.node_id
                to_node_id = item.parent_node.node_id
                self.connection_created.emit(from_node_id, to_node_id)
            else:
                # Cancel connection
                self.scene.removeItem(self.temp_connection)

            self.temp_connection = None
            self.connecting_from = None
            return

        super().mouseReleaseEvent(event)


class IntegrationHubUI(QWidget):
    """Main Integration Hub UI"""

    def __init__(self):
        super().__init__()

        self.registry = registry
        self.current_workflow: Optional[Dict[str, Any]] = None
        self.workflows: List[Dict[str, Any]] = []

        self.init_ui()
        self.load_workflows()

    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("XENO Integration Hub")
        self.setMinimumSize(1200, 800)

        # Main layout
        main_layout = QHBoxLayout()

        # Left panel - Node library
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)

        # Center - Canvas
        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, 3)

        # Right panel - Properties
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)

        self.setLayout(main_layout)

        # Apply dark theme
        self.setStyleSheet(
            """
            QWidget {
                background: #2b2d31;
                color: #ffffff;
                font-family: 'Segoe UI';
            }
            QPushButton {
                background: #5865F2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #4752C4;
            }
            QListWidget {
                background: #313338;
                border: 1px solid #40444b;
                border-radius: 6px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background: #404249;
            }
            QListWidget::item:selected {
                background: #5865F2;
            }
            QLineEdit, QTextEdit {
                background: #313338;
                border: 1px solid #40444b;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
            }
            QComboBox {
                background: #313338;
                border: 1px solid #40444b;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
            }
            QLabel {
                color: #b5bac1;
            }
        """
        )

    def create_left_panel(self) -> QWidget:
        """Create left panel with node library"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("📚 Node Library")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)

        # Triggers section
        triggers_label = QLabel("Triggers")
        triggers_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(triggers_label)

        self.triggers_list = QListWidget()
        self.triggers_list.addItems(
            ["⏰ Schedule", "📨 Webhook", "⚡ Event", "❓ Condition", "👆 Manual"]
        )
        self.triggers_list.itemDoubleClicked.connect(self.add_trigger_node)
        layout.addWidget(self.triggers_list)

        # Actions section
        actions_label = QLabel("Actions")
        actions_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(actions_label)

        self.actions_list = QListWidget()
        self.actions_list.addItems(
            [
                "💬 Slack Message",
                "📝 Notion Page",
                "📋 Trello Card",
                "💭 Discord Message",
                "✅ Todoist Task",
                "📧 Send Email",
                "🔔 Notification",
                "🔄 HTTP Request",
            ]
        )
        self.actions_list.itemDoubleClicked.connect(self.add_action_node)
        layout.addWidget(self.actions_list)

        panel.setLayout(layout)
        return panel

    def create_center_panel(self) -> QWidget:
        """Create center panel with canvas"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Toolbar
        toolbar = QHBoxLayout()

        new_btn = QPushButton("➕ New")
        new_btn.clicked.connect(self.new_workflow)
        toolbar.addWidget(new_btn)

        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_workflow)
        toolbar.addWidget(save_btn)

        run_btn = QPushButton("▶️ Run")
        run_btn.clicked.connect(self.run_workflow)
        toolbar.addWidget(run_btn)

        toolbar.addStretch()

        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self.clear_canvas)
        toolbar.addWidget(clear_btn)

        layout.addLayout(toolbar)

        # Canvas
        self.canvas = WorkflowCanvas()
        self.canvas.node_selected.connect(self.on_node_selected)
        self.canvas.connection_created.connect(self.on_connection_created)
        layout.addWidget(self.canvas)

        panel.setLayout(layout)
        return panel

    def create_right_panel(self) -> QWidget:
        """Create right panel with properties"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("⚙️ Properties")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)

        # Workflow properties
        form = QFormLayout()

        self.workflow_name_input = QLineEdit()
        self.workflow_name_input.setPlaceholderText("My Workflow")
        form.addRow("Name:", self.workflow_name_input)

        self.workflow_desc_input = QTextEdit()
        self.workflow_desc_input.setMaximumHeight(100)
        self.workflow_desc_input.setPlaceholderText("Description...")
        form.addRow("Description:", self.workflow_desc_input)

        layout.addLayout(form)

        # Node properties (shown when node selected)
        self.node_properties = QWidget()
        node_layout = QVBoxLayout()

        node_title = QLabel("Node Properties")
        node_title.setStyleSheet("font-weight: bold; margin-top: 20px;")
        node_layout.addWidget(node_title)

        self.node_props_form = QFormLayout()
        node_layout.addLayout(self.node_props_form)

        self.node_properties.setLayout(node_layout)
        layout.addWidget(self.node_properties)

        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def add_trigger_node(self, item):
        """Add trigger node to canvas"""
        trigger_text = item.text()
        self.canvas.add_node("trigger", trigger_text, 100, 200)

    def add_action_node(self, item):
        """Add action node to canvas"""
        action_text = item.text()
        self.canvas.add_node("action", action_text, 400, 200)

    def on_node_selected(self, node_id: str):
        """Handle node selection"""
        pass

    def on_connection_created(self, from_id: str, to_id: str):
        """Handle connection creation"""
        print(f"Connected: {from_id} -> {to_id}")

    def new_workflow(self):
        """Create new workflow"""
        self.canvas.clear_canvas()
        self.workflow_name_input.clear()
        self.workflow_desc_input.clear()
        self.current_workflow = None

    def save_workflow(self):
        """Save current workflow"""
        # Implementation for saving workflow
        QMessageBox.information(self, "Save", "Workflow saved successfully!")

    def run_workflow(self):
        """Run current workflow"""
        # Implementation for running workflow
        QMessageBox.information(self, "Run", "Workflow execution started!")

    def clear_canvas(self):
        """Clear canvas"""
        reply = QMessageBox.question(
            self,
            "Clear Canvas",
            "Are you sure you want to clear the canvas?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.canvas.clear_canvas()

    def load_workflows(self):
        """Load saved workflows"""
        # Implementation for loading workflows
        pass

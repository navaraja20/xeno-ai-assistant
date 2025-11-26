"""
IoT Dashboard UI for XENO
Displays wearable data and smart home controls
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout, QSlider, QComboBox,
    QGroupBox, QProgressBar, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor
import asyncio
from typing import Optional, Dict, Any, List


class IoTDashboardUI(QWidget):
    """Main IoT dashboard interface"""
    
    device_command = pyqtSignal(str, str, dict)  # device_id, command, params
    scene_activated = pyqtSignal(str)  # scene_name
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1000, 700)
        self.setWindowTitle("XENO IoT Dashboard")
        
        # Apply dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2d31;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                background-color: #313338;
                border: 1px solid #40444b;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #ffffff;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #5865f2;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4752c4;
            }
            QPushButton:pressed {
                background-color: #3c45a5;
            }
            QLabel {
                color: #b5bac1;
            }
            QSlider::groove:horizontal {
                background: #40444b;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #5865f2;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QComboBox {
                background-color: #383a40;
                border: 1px solid #40444b;
                border-radius: 5px;
                padding: 5px;
                color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #b5bac1;
                width: 0;
                height: 0;
            }
            QProgressBar {
                background-color: #40444b;
                border: none;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #5865f2;
                border-radius: 5px;
            }
            QScrollArea {
                border: none;
            }
            QTabWidget::pane {
                border: 1px solid #40444b;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #313338;
                color: #b5bac1;
                padding: 10px 20px;
                border: 1px solid #40444b;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #5865f2;
                color: #ffffff;
            }
        """)
        
        self.init_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_health_display)
        self.update_timer.start(5000)  # Update every 5 seconds
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🏠 IoT & Wearable Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)
        
        # Tab widget
        tabs = QTabWidget()
        
        # Wearable tab
        wearable_tab = self.create_wearable_tab()
        tabs.addTab(wearable_tab, "⌚ Wearable Data")
        
        # Smart Home tab
        smart_home_tab = self.create_smart_home_tab()
        tabs.addTab(smart_home_tab, "🏠 Smart Home")
        
        # Scenes tab
        scenes_tab = self.create_scenes_tab()
        tabs.addTab(scenes_tab, "🎬 Scenes")
        
        layout.addWidget(tabs)
        
        self.setLayout(layout)
    
    def create_wearable_tab(self) -> QWidget:
        """Create wearable data tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Health metrics
        health_group = QGroupBox("Health Metrics")
        health_layout = QGridLayout()
        
        # Heart rate
        self.heart_rate_label = QLabel("-- bpm")
        self.heart_rate_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #ed4245;")
        health_layout.addWidget(QLabel("❤️ Heart Rate:"), 0, 0)
        health_layout.addWidget(self.heart_rate_label, 0, 1)
        
        # Steps
        self.steps_label = QLabel("-- steps")
        self.steps_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #5865f2;")
        self.steps_progress = QProgressBar()
        self.steps_progress.setMaximum(10000)
        health_layout.addWidget(QLabel("👟 Steps:"), 1, 0)
        health_layout.addWidget(self.steps_label, 1, 1)
        health_layout.addWidget(self.steps_progress, 2, 0, 1, 2)
        
        # Calories
        self.calories_label = QLabel("-- cal")
        self.calories_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #faa61a;")
        health_layout.addWidget(QLabel("🔥 Calories:"), 3, 0)
        health_layout.addWidget(self.calories_label, 3, 1)
        
        # Sleep
        self.sleep_label = QLabel("-- hrs")
        self.sleep_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #57f287;")
        health_layout.addWidget(QLabel("😴 Sleep:"), 4, 0)
        health_layout.addWidget(self.sleep_label, 4, 1)
        
        # Activity
        self.activity_label = QLabel("--")
        self.activity_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        health_layout.addWidget(QLabel("🏃 Activity:"), 5, 0)
        health_layout.addWidget(self.activity_label, 5, 1)
        
        health_group.setLayout(health_layout)
        layout.addWidget(health_group)
        
        # Battery
        battery_group = QGroupBox("Device Battery")
        battery_layout = QHBoxLayout()
        self.battery_progress = QProgressBar()
        self.battery_progress.setMaximum(100)
        self.battery_label = QLabel("--%")
        battery_layout.addWidget(QLabel("🔋"))
        battery_layout.addWidget(self.battery_progress)
        battery_layout.addWidget(self.battery_label)
        battery_group.setLayout(battery_layout)
        layout.addWidget(battery_group)
        
        # Sync status
        sync_layout = QHBoxLayout()
        self.sync_status = QLabel("Status: Not connected")
        self.sync_status.setStyleSheet("color: #ed4245;")
        sync_btn = QPushButton("🔄 Sync Now")
        sync_btn.clicked.connect(self.sync_wearable)
        sync_layout.addWidget(self.sync_status)
        sync_layout.addWidget(sync_btn)
        layout.addLayout(sync_layout)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_smart_home_tab(self) -> QWidget:
        """Create smart home control tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Scroll area for devices
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Lights
        lights_group = self.create_lights_control()
        scroll_layout.addWidget(lights_group)
        
        # Thermostat
        thermostat_group = self.create_thermostat_control()
        scroll_layout.addWidget(thermostat_group)
        
        # Lock
        lock_group = self.create_lock_control()
        scroll_layout.addWidget(lock_group)
        
        # Camera
        camera_group = self.create_camera_control()
        scroll_layout.addWidget(camera_group)
        
        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        
        layout.addWidget(scroll)
        widget.setLayout(layout)
        return widget
    
    def create_lights_control(self) -> QGroupBox:
        """Create lights control group"""
        group = QGroupBox("💡 Lights")
        layout = QVBoxLayout()
        
        # Light 1
        light1_layout = QHBoxLayout()
        light1_layout.addWidget(QLabel("Living Room"))
        light1_toggle = QPushButton("ON")
        light1_toggle.setCheckable(True)
        light1_toggle.clicked.connect(lambda checked: self.toggle_light("light_1", checked))
        light1_layout.addWidget(light1_toggle)
        
        brightness_slider = QSlider(Qt.Orientation.Horizontal)
        brightness_slider.setRange(0, 100)
        brightness_slider.setValue(100)
        brightness_slider.valueChanged.connect(lambda v: self.set_brightness("light_1", v))
        light1_layout.addWidget(brightness_slider)
        
        layout.addLayout(light1_layout)
        
        # Light 2
        light2_layout = QHBoxLayout()
        light2_layout.addWidget(QLabel("Bedroom"))
        light2_toggle = QPushButton("OFF")
        light2_toggle.setCheckable(True)
        light2_toggle.clicked.connect(lambda checked: self.toggle_light("light_2", checked))
        light2_layout.addWidget(light2_toggle)
        layout.addLayout(light2_layout)
        
        group.setLayout(layout)
        return group
    
    def create_thermostat_control(self) -> QGroupBox:
        """Create thermostat control group"""
        group = QGroupBox("🌡️ Thermostat")
        layout = QVBoxLayout()
        
        # Temperature display
        temp_layout = QHBoxLayout()
        self.current_temp = QLabel("72°F")
        self.current_temp.setStyleSheet("font-size: 32px; font-weight: bold; color: #5865f2;")
        temp_layout.addWidget(QLabel("Current:"))
        temp_layout.addWidget(self.current_temp)
        temp_layout.addStretch()
        layout.addLayout(temp_layout)
        
        # Target temperature
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target:"))
        
        temp_slider = QSlider(Qt.Orientation.Horizontal)
        temp_slider.setRange(60, 85)
        temp_slider.setValue(72)
        self.target_temp = QLabel("72°F")
        temp_slider.valueChanged.connect(lambda v: self.set_temperature(v))
        
        target_layout.addWidget(temp_slider)
        target_layout.addWidget(self.target_temp)
        layout.addLayout(target_layout)
        
        # Mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        mode_combo = QComboBox()
        mode_combo.addItems(["Auto", "Heat", "Cool", "Off"])
        mode_combo.currentTextChanged.connect(self.set_hvac_mode)
        mode_layout.addWidget(mode_combo)
        layout.addLayout(mode_layout)
        
        group.setLayout(layout)
        return group
    
    def create_lock_control(self) -> QGroupBox:
        """Create lock control group"""
        group = QGroupBox("🔐 Door Lock")
        layout = QVBoxLayout()
        
        status_layout = QHBoxLayout()
        self.lock_status = QLabel("🔒 Locked")
        self.lock_status.setStyleSheet("font-size: 18px; font-weight: bold; color: #57f287;")
        status_layout.addWidget(self.lock_status)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        button_layout = QHBoxLayout()
        lock_btn = QPushButton("🔒 Lock")
        lock_btn.clicked.connect(lambda: self.control_lock("lock"))
        unlock_btn = QPushButton("🔓 Unlock")
        unlock_btn.clicked.connect(lambda: self.control_lock("unlock"))
        
        button_layout.addWidget(lock_btn)
        button_layout.addWidget(unlock_btn)
        layout.addLayout(button_layout)
        
        group.setLayout(layout)
        return group
    
    def create_camera_control(self) -> QGroupBox:
        """Create camera control group"""
        group = QGroupBox("📹 Security Camera")
        layout = QVBoxLayout()
        
        status_layout = QHBoxLayout()
        self.camera_status = QLabel("⚫ Not Recording")
        status_layout.addWidget(self.camera_status)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        button_layout = QHBoxLayout()
        record_btn = QPushButton("🔴 Record")
        record_btn.clicked.connect(lambda: self.control_camera("start_recording"))
        stop_btn = QPushButton("⏹️ Stop")
        stop_btn.clicked.connect(lambda: self.control_camera("stop_recording"))
        snapshot_btn = QPushButton("📸 Snapshot")
        snapshot_btn.clicked.connect(lambda: self.control_camera("take_snapshot"))
        
        button_layout.addWidget(record_btn)
        button_layout.addWidget(stop_btn)
        button_layout.addWidget(snapshot_btn)
        layout.addLayout(button_layout)
        
        group.setLayout(layout)
        return group
    
    def create_scenes_tab(self) -> QWidget:
        """Create scenes tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        scenes_group = QGroupBox("Quick Scenes")
        scenes_layout = QGridLayout()
        
        # Scene buttons
        scenes = [
            ("🌅 Good Morning", "good_morning", "Turn on lights, open blinds, set thermostat to 72°F"),
            ("🌙 Good Night", "good_night", "Turn off all lights, lock doors, set security mode"),
            ("🏠 I'm Home", "home", "Turn on lights, unlock door, comfortable temperature"),
            ("🚗 Leaving", "leaving", "Turn off lights, lock doors, set away mode, lower thermostat"),
            ("🎬 Movie Time", "movie", "Dim lights to 20%, close blinds, comfortable temperature"),
            ("💼 Work Mode", "work", "Bright lights, comfortable temperature, focus mode")
        ]
        
        row = 0
        col = 0
        for name, scene_id, description in scenes:
            scene_btn = QPushButton(name)
            scene_btn.setMinimumHeight(60)
            scene_btn.setToolTip(description)
            scene_btn.clicked.connect(lambda checked, s=scene_id: self.activate_scene(s))
            scenes_layout.addWidget(scene_btn, row, col)
            
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        scenes_group.setLayout(scenes_layout)
        layout.addWidget(scenes_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def update_health_display(self):
        """Update health metrics display"""
        # This would be called by the wearable manager with real data
        pass
    
    def update_wearable_data(self, data: Dict[str, Any]):
        """Update wearable data display"""
        if "heart_rate" in data:
            self.heart_rate_label.setText(f"{data['heart_rate']} bpm")
        
        if "steps" in data:
            steps = data["steps"]
            self.steps_label.setText(f"{steps:,} steps")
            self.steps_progress.setValue(min(steps, 10000))
        
        if "calories" in data:
            self.calories_label.setText(f"{data['calories']} cal")
        
        if "sleep_hours" in data:
            self.sleep_label.setText(f"{data['sleep_hours']:.1f} hrs")
        
        if "activity_type" in data:
            self.activity_label.setText(data["activity_type"])
        
        if "battery" in data:
            battery = data["battery"]
            self.battery_progress.setValue(battery)
            self.battery_label.setText(f"{battery}%")
            
            if battery > 50:
                self.battery_progress.setStyleSheet("QProgressBar::chunk { background-color: #57f287; }")
            elif battery > 20:
                self.battery_progress.setStyleSheet("QProgressBar::chunk { background-color: #faa61a; }")
            else:
                self.battery_progress.setStyleSheet("QProgressBar::chunk { background-color: #ed4245; }")
        
        self.sync_status.setText("Status: ✅ Connected")
        self.sync_status.setStyleSheet("color: #57f287;")
    
    def toggle_light(self, device_id: str, on: bool):
        """Toggle light on/off"""
        command = "turn_on" if on else "turn_off"
        self.device_command.emit(device_id, command, {})
    
    def set_brightness(self, device_id: str, brightness: int):
        """Set light brightness"""
        self.device_command.emit(device_id, "set_brightness", {"brightness": brightness})
    
    def set_temperature(self, temp: int):
        """Set thermostat temperature"""
        self.target_temp.setText(f"{temp}°F")
        self.device_command.emit("thermostat_1", "set_temperature", {"temp": temp})
    
    def set_hvac_mode(self, mode: str):
        """Set HVAC mode"""
        self.device_command.emit("thermostat_1", "set_mode", {"mode": mode.lower()})
    
    def control_lock(self, command: str):
        """Control door lock"""
        self.device_command.emit("lock_1", command, {})
        if command == "lock":
            self.lock_status.setText("🔒 Locked")
            self.lock_status.setStyleSheet("font-size: 18px; font-weight: bold; color: #57f287;")
        else:
            self.lock_status.setText("🔓 Unlocked")
            self.lock_status.setStyleSheet("font-size: 18px; font-weight: bold; color: #faa61a;")
    
    def control_camera(self, command: str):
        """Control security camera"""
        self.device_command.emit("camera_1", command, {})
        if command == "start_recording":
            self.camera_status.setText("🔴 Recording")
            self.camera_status.setStyleSheet("color: #ed4245;")
        elif command == "stop_recording":
            self.camera_status.setText("⚫ Not Recording")
            self.camera_status.setStyleSheet("color: #b5bac1;")
    
    def activate_scene(self, scene_name: str):
        """Activate a scene"""
        self.scene_activated.emit(scene_name)
    
    def sync_wearable(self):
        """Trigger wearable sync"""
        self.sync_status.setText("Status: 🔄 Syncing...")
        self.sync_status.setStyleSheet("color: #faa61a;")
        # Actual sync would be handled by wearable manager

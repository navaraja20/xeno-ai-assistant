"""
Demo: 3D Avatar & Holographic UI
Demonstrates avatar with AI emotions and holographic effects
"""

import sys
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QComboBox,
    QGroupBox,
)

from src.avatar import (
    AvatarWidget,
    EmotionState,
    AvatarPose,
    HologramEffect,
)
from src.core.logger import setup_logger


class AvatarDemo(QMainWindow):
    """Avatar demo application"""
    
    def __init__(self):
        super().__init__()
        
        self.logger = setup_logger("demo.avatar")
        
        self.setWindowTitle("XENO 3D Avatar & Holographic UI Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QHBoxLayout(central)
        
        # Avatar widget
        self.avatar_widget = AvatarWidget()
        layout.addWidget(self.avatar_widget, 2)
        
        # Control panel
        controls = self._create_controls()
        layout.addWidget(controls, 1)
        
        # Auto-demo timer
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self._auto_demo)
        
        self.logger.info("Avatar demo initialized")
    
    def _create_controls(self) -> QWidget:
        """Create control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Avatar Controls")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ffff;")
        layout.addWidget(title)
        
        # Emotion controls
        emotion_group = QGroupBox("Emotions")
        emotion_layout = QVBoxLayout(emotion_group)
        
        self.emotion_combo = QComboBox()
        for emotion in EmotionState:
            self.emotion_combo.addItem(emotion.value.title(), emotion)
        self.emotion_combo.currentIndexChanged.connect(self._on_emotion_changed)
        emotion_layout.addWidget(self.emotion_combo)
        
        layout.addWidget(emotion_group)
        
        # Pose controls
        pose_group = QGroupBox("Poses")
        pose_layout = QVBoxLayout(pose_group)
        
        poses = [
            ("Wave", "wave"),
            ("Celebrate", "celebrate"),
            ("Think", "think"),
            ("Point", "point"),
            ("Type", "type"),
            ("Listen", "listen"),
        ]
        
        for name, action in poses:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, a=action: self.avatar_widget.trigger_action(a))
            btn.setStyleSheet("""
                QPushButton {
                    background: #5865F2;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background: #4752C4;
                }
            """)
            pose_layout.addWidget(btn)
        
        layout.addWidget(pose_group)
        
        # Effect controls
        effect_group = QGroupBox("Holographic Effects")
        effect_layout = QVBoxLayout(effect_group)
        
        effects = [
            ("Glow", HologramEffect.GLOW),
            ("Scan Lines", HologramEffect.SCAN_LINES),
            ("Particles", HologramEffect.PARTICLES),
            ("Grid", HologramEffect.GRID),
            ("Hexagons", HologramEffect.HEXAGONS),
            ("Circuit Board", HologramEffect.CIRCUIT_BOARD),
            ("Shimmer", HologramEffect.SHIMMER),
            ("Data Stream", HologramEffect.DATA_STREAM),
        ]
        
        for name, effect in effects:
            btn = QPushButton(f"Toggle {name}")
            btn.clicked.connect(lambda checked, e=effect: self.avatar_widget.toggle_effect(e))
            btn.setStyleSheet("""
                QPushButton {
                    background: #007ACC;
                    color: white;
                    border: none;
                    padding: 6px;
                    border-radius: 3px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: #005A9E;
                }
            """)
            effect_layout.addWidget(btn)
        
        layout.addWidget(effect_group)
        
        # Auto demo
        demo_btn = QPushButton("▶ Start Auto Demo")
        demo_btn.clicked.connect(self._toggle_auto_demo)
        demo_btn.setStyleSheet("""
            QPushButton {
                background: #28A745;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        layout.addWidget(demo_btn)
        
        layout.addStretch()
        
        # Style panel
        panel.setStyleSheet("""
            QWidget {
                background: #2b2d31;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #00ffff;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #00ffff;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QComboBox {
                background: #40444b;
                color: white;
                border: 1px solid #00ffff;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        
        return panel
    
    def _on_emotion_changed(self, index):
        """Handle emotion change"""
        emotion = self.emotion_combo.currentData()
        if emotion:
            self.avatar_widget.set_emotion(emotion)
    
    def _toggle_auto_demo(self):
        """Toggle auto demo"""
        if self.demo_timer.isActive():
            self.demo_timer.stop()
            self.logger.info("Auto demo stopped")
        else:
            self.demo_timer.start(3000)  # Change every 3 seconds
            self.logger.info("Auto demo started")
    
    def _auto_demo(self):
        """Auto demo cycle"""
        # Cycle through emotions
        current_index = self.emotion_combo.currentIndex()
        next_index = (current_index + 1) % self.emotion_combo.count()
        self.emotion_combo.setCurrentIndex(next_index)
        
        # Random action every other cycle
        if next_index % 2 == 0:
            actions = ["wave", "celebrate", "think", "point"]
            import random
            self.avatar_widget.trigger_action(random.choice(actions))


def main():
    """Run avatar demo"""
    app = QApplication(sys.argv)
    
    # Dark theme
    app.setStyleSheet("""
        QMainWindow {
            background: #1e1e2e;
        }
    """)
    
    demo = AvatarDemo()
    demo.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

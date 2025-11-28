"""
3D Avatar Widget
PyQt6 widget for rendering 3D avatar with holographic effects
"""

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from src.avatar.avatar_engine import EmotionState, AvatarPose, get_avatar_engine
from src.avatar.holographic_effects import HologramEffect, get_holographic_renderer
from src.core.logger import setup_logger


class AvatarWidget(QWidget):
    """3D Avatar display widget with holographic effects"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = setup_logger("avatar.widget")
        
        # Avatar engine
        self.avatar_engine = get_avatar_engine()
        
        # Holographic renderer
        self.holo_renderer = get_holographic_renderer()
        
        # UI settings
        self.setMinimumSize(400, 600)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Active effects
        self.active_effects = [
            HologramEffect.GLOW,
            HologramEffect.SCAN_LINES,
            HologramEffect.PARTICLES,
        ]
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer)
        self.timer.start(16)  # ~60 FPS
        
        # Start avatar
        self.avatar_engine.start()
        
        self.logger.info("Avatar widget initialized")
    
    def paintEvent(self, event):
        """Paint the avatar and holographic effects"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = QRectF(self.rect())
        
        # Background
        painter.fillRect(rect, QColor(20, 20, 30, 200))
        
        # Render holographic effects
        if HologramEffect.GRID in self.active_effects:
            self.holo_renderer.render_grid(painter, rect)
        
        if HologramEffect.HEXAGONS in self.active_effects:
            self.holo_renderer.render_hexagons(painter, rect)
        
        if HologramEffect.CIRCUIT_BOARD in self.active_effects:
            self.holo_renderer.render_circuit_board(painter, rect)
        
        # Render avatar (simplified - placeholder)
        avatar_data = self.avatar_engine.get_render_data()
        self._render_avatar_simple(painter, rect, avatar_data)
        
        # Overlay effects
        if HologramEffect.SCAN_LINES in self.active_effects:
            self.holo_renderer.render_scan_lines(painter, rect)
        
        if HologramEffect.GLOW in self.active_effects:
            center = rect.center()
            self.holo_renderer.render_pulse(painter, center, 150)
        
        if HologramEffect.PARTICLES in self.active_effects:
            self.holo_renderer.render_particles(painter, rect)
        
        if HologramEffect.SHIMMER in self.active_effects:
            self.holo_renderer.render_shimmer(painter, rect)
        
        if HologramEffect.DATA_STREAM in self.active_effects:
            self.holo_renderer.render_data_stream(painter, rect)
    
    def _render_avatar_simple(self, painter: QPainter, rect: QRectF, avatar_data: dict):
        """Render simplified avatar (placeholder for full 3D)"""
        center_x = rect.center().x()
        
        # Get emotion color
        emotion = avatar_data["emotion"]
        emotion_colors = {
            "happy": QColor(0, 255, 100),
            "excited": QColor(255, 200, 0),
            "thinking": QColor(100, 100, 255),
            "neutral": QColor(0, 255, 255),
            "focused": QColor(255, 100, 0),
        }
        color = emotion_colors.get(emotion, QColor(0, 255, 255))
        
        # Head
        head_y = rect.top() + 100
        self.holo_renderer.render_glow(
            painter,
            QRectF(center_x - 60, head_y, 120, 120),
            intensity=1.0 if avatar_data["is_speaking"] else 0.7
        )
        
        # Eyes (glow when speaking)
        if avatar_data["is_speaking"]:
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(center_x - 25, head_y + 40), 8, 8)
            painter.drawEllipse(QPointF(center_x + 25, head_y + 40), 8, 8)
        
        # Body glow
        body_y = head_y + 140
        self.holo_renderer.render_glow(
            painter,
            QRectF(center_x - 80, body_y, 160, 200),
            intensity=0.5
        )
        
        # Status text
        painter.setPen(color)
        painter.drawText(
            int(rect.left() + 10),
            int(rect.bottom() - 30),
            f"Status: {avatar_data['pose'].replace('_', ' ').title()}"
        )
        painter.drawText(
            int(rect.left() + 10),
            int(rect.bottom() - 10),
            f"Emotion: {emotion.title()}"
        )
    
    def _on_timer(self):
        """Update animation"""
        self.avatar_engine.update()
        self.holo_renderer.update(0.016)  # ~60 FPS
        self.update()  # Trigger repaint
    
    def set_emotion(self, emotion: EmotionState):
        """Set avatar emotion"""
        self.avatar_engine.avatar.set_emotion(emotion)
    
    def set_pose(self, pose: AvatarPose):
        """Set avatar pose"""
        self.avatar_engine.avatar.set_pose(pose)
    
    def trigger_action(self, action: str):
        """Trigger avatar action"""
        self.avatar_engine.trigger_action(action)
    
    def toggle_effect(self, effect: HologramEffect):
        """Toggle holographic effect"""
        if effect in self.active_effects:
            self.active_effects.remove(effect)
        else:
            self.active_effects.append(effect)


def create_avatar_widget(parent=None) -> AvatarWidget:
    """Create avatar widget"""
    return AvatarWidget(parent)

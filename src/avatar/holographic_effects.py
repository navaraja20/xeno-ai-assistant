"""
Holographic UI Effects
Futuristic holographic interface effects
"""

import math
import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from PyQt6.QtCore import QPointF, QPropertyAnimation, QRectF, Qt, QTimer, pyqtProperty
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import QGraphicsEffect, QWidget

from src.core.logger import setup_logger


class HologramEffect(Enum):
    """Types of holographic effects"""
    
    SCAN_LINES = "scan_lines"
    GLOW = "glow"
    FLICKER = "flicker"
    PARTICLES = "particles"
    GRID = "grid"
    HEXAGONS = "hexagons"
    CIRCUIT_BOARD = "circuit_board"
    DATA_STREAM = "data_stream"
    PULSE = "pulse"
    SHIMMER = "shimmer"


@dataclass
class Particle:
    """Holographic particle"""
    x: float
    y: float
    vx: float
    vy: float
    size: float
    lifetime: float
    age: float
    color: QColor


class HolographicGlow(QGraphicsEffect):
    """Holographic glow effect for widgets"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._glow_color = QColor(0, 255, 255, 100)  # Cyan glow
        self._glow_intensity = 1.0
        self._glow_radius = 20
    
    def draw(self, painter: QPainter):
        """Draw the glow effect"""
        # Draw source
        self.drawSource(painter)
        
        # Apply glow (simplified - proper implementation would use blur)
        painter.save()
        painter.setOpacity(self._glow_intensity * 0.3)
        
        # Draw glow ring
        pen = QPen(self._glow_color, self._glow_radius)
        painter.setPen(pen)
        
        source_rect = self.sourceBoundingRect()
        painter.drawRect(source_rect)
        
        painter.restore()
    
    def setGlowColor(self, color: QColor):
        """Set glow color"""
        self._glow_color = color
        self.update()
    
    def setGlowIntensity(self, intensity: float):
        """Set glow intensity (0-1)"""
        self._glow_intensity = max(0.0, min(1.0, intensity))
        self.update()


class HolographicRenderer:
    """Renders holographic effects"""
    
    def __init__(self):
        self.logger = setup_logger("hologram.renderer")
        
        # Effect state
        self.scan_line_offset = 0.0
        self.flicker_intensity = 1.0
        self.time = 0.0
        
        # Particles
        self.particles: List[Particle] = []
        self.max_particles = 100
        
        # Colors
        self.primary_color = QColor(0, 255, 255)  # Cyan
        self.secondary_color = QColor(255, 0, 255)  # Magenta
        self.accent_color = QColor(255, 255, 0)  # Yellow
        
        self.logger.info("Holographic renderer initialized")
    
    def render_scan_lines(self, painter: QPainter, rect: QRectF):
        """Render horizontal scan lines"""
        painter.save()
        
        line_spacing = 4
        opacity = 0.1
        
        # Draw scan lines
        pen = QPen(self.primary_color, 1)
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.setOpacity(opacity)
        
        y = rect.top() + self.scan_line_offset
        while y < rect.bottom():
            painter.drawLine(
                QPointF(rect.left(), y),
                QPointF(rect.right(), y)
            )
            y += line_spacing
        
        painter.restore()
    
    def render_glow(self, painter: QPainter, rect: QRectF, intensity: float = 1.0):
        """Render pulsing glow"""
        painter.save()
        
        # Create radial gradient
        center = rect.center()
        radius = max(rect.width(), rect.height()) / 2
        
        gradient = QRadialGradient(center, radius)
        
        color = QColor(self.primary_color)
        color.setAlpha(int(100 * intensity))
        gradient.setColorAt(0.0, color)
        
        color.setAlpha(0)
        gradient.setColorAt(1.0, color)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(rect)
        
        painter.restore()
    
    def render_particles(self, painter: QPainter, rect: QRectF):
        """Render floating particles"""
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for particle in self.particles:
            # Calculate alpha based on age
            alpha = 1.0 - (particle.age / particle.lifetime)
            
            color = QColor(particle.color)
            color.setAlphaF(alpha)
            
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            
            painter.drawEllipse(
                QPointF(particle.x, particle.y),
                particle.size,
                particle.size
            )
        
        painter.restore()
    
    def render_grid(self, painter: QPainter, rect: QRectF):
        """Render holographic grid"""
        painter.save()
        
        grid_size = 50
        opacity = 0.2
        
        pen = QPen(self.primary_color, 1)
        pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(pen)
        painter.setOpacity(opacity)
        
        # Vertical lines
        x = rect.left()
        while x <= rect.right():
            painter.drawLine(
                QPointF(x, rect.top()),
                QPointF(x, rect.bottom())
            )
            x += grid_size
        
        # Horizontal lines
        y = rect.top()
        while y <= rect.bottom():
            painter.drawLine(
                QPointF(rect.left(), y),
                QPointF(rect.right(), y)
            )
            y += grid_size
        
        painter.restore()
    
    def render_hexagons(self, painter: QPainter, rect: QRectF):
        """Render hexagonal pattern"""
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        hex_size = 30
        opacity = 0.15
        
        pen = QPen(self.primary_color, 2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setOpacity(opacity)
        
        # Draw hexagons in grid
        y = rect.top()
        row = 0
        
        while y < rect.bottom():
            x = rect.left()
            if row % 2 == 1:
                x += hex_size * 1.5
            
            while x < rect.right():
                self._draw_hexagon(painter, QPointF(x, y), hex_size)
                x += hex_size * 3
            
            y += hex_size * 2.6
            row += 1
        
        painter.restore()
    
    def render_circuit_board(self, painter: QPainter, rect: QRectF):
        """Render circuit board pattern"""
        painter.save()
        
        pen = QPen(self.primary_color, 1)
        painter.setPen(pen)
        painter.setOpacity(0.3)
        
        # Random circuit paths
        random.seed(42)  # Deterministic
        
        for _ in range(20):
            points = []
            x = random.uniform(rect.left(), rect.right())
            y = random.uniform(rect.top(), rect.bottom())
            points.append(QPointF(x, y))
            
            # Generate path
            for __ in range(random.randint(3, 8)):
                if random.random() > 0.5:
                    x += random.uniform(-50, 50)
                else:
                    y += random.uniform(-50, 50)
                
                x = max(rect.left(), min(rect.right(), x))
                y = max(rect.top(), min(rect.bottom(), y))
                
                points.append(QPointF(x, y))
            
            # Draw path
            path = QPainterPath()
            path.moveTo(points[0])
            for point in points[1:]:
                path.lineTo(point)
            
            painter.drawPath(path)
            
            # Draw nodes
            for point in points:
                painter.drawEllipse(point, 3, 3)
        
        painter.restore()
    
    def render_data_stream(self, painter: QPainter, rect: QRectF):
        """Render flowing data stream"""
        painter.save()
        
        stream_width = 30
        opacity = 0.4
        
        # Create flowing gradient
        gradient = QLinearGradient(
            rect.left(), rect.top(),
            rect.right(), rect.bottom()
        )
        
        # Animate gradient offset
        offset = (self.time % 2.0) / 2.0
        
        color1 = QColor(self.primary_color)
        color1.setAlpha(0)
        color2 = QColor(self.primary_color)
        color2.setAlpha(int(255 * opacity))
        
        gradient.setColorAt(offset, color1)
        gradient.setColorAt(min(1.0, offset + 0.3), color2)
        gradient.setColorAt(min(1.0, offset + 0.6), color1)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(rect)
        
        painter.restore()
    
    def render_pulse(self, painter: QPainter, center: QPointF, radius: float):
        """Render pulsing ring"""
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Pulse animation
        pulse = math.sin(self.time * 3.0) * 0.5 + 0.5
        current_radius = radius * (0.8 + pulse * 0.4)
        
        # Gradient
        gradient = QRadialGradient(center, current_radius)
        
        color = QColor(self.primary_color)
        color.setAlpha(0)
        gradient.setColorAt(0.0, color)
        
        color.setAlpha(int(100 * pulse))
        gradient.setColorAt(0.8, color)
        
        color.setAlpha(0)
        gradient.setColorAt(1.0, color)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, current_radius, current_radius)
        
        painter.restore()
    
    def render_shimmer(self, painter: QPainter, rect: QRectF):
        """Render shimmer effect"""
        painter.save()
        
        # Create sweeping gradient
        angle = (self.time * 50) % 360
        
        gradient = QConicalGradient(rect.center(), angle)
        
        color1 = QColor(self.primary_color)
        color1.setAlpha(0)
        color2 = QColor(self.primary_color)
        color2.setAlpha(50)
        
        gradient.setColorAt(0.0, color1)
        gradient.setColorAt(0.3, color2)
        gradient.setColorAt(0.5, color1)
        gradient.setColorAt(1.0, color1)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(rect)
        
        painter.restore()
    
    def update(self, delta_time: float):
        """Update animations"""
        self.time += delta_time
        
        # Update scan lines
        self.scan_line_offset = (self.scan_line_offset + 100 * delta_time) % 4
        
        # Update flicker
        self.flicker_intensity = 0.95 + 0.05 * math.sin(self.time * 30)
        
        # Update particles
        self._update_particles(delta_time)
        
        # Spawn new particles
        if len(self.particles) < self.max_particles and random.random() < 0.1:
            self._spawn_particle()
    
    def _update_particles(self, delta_time: float):
        """Update particle system"""
        particles_to_remove = []
        
        for i, particle in enumerate(self.particles):
            # Update position
            particle.x += particle.vx * delta_time
            particle.y += particle.vy * delta_time
            
            # Update age
            particle.age += delta_time
            
            # Mark dead particles
            if particle.age >= particle.lifetime:
                particles_to_remove.append(i)
        
        # Remove dead particles
        for i in reversed(particles_to_remove):
            self.particles.pop(i)
    
    def _spawn_particle(self):
        """Spawn new particle"""
        particle = Particle(
            x=random.uniform(0, 1920),
            y=random.uniform(0, 1080),
            vx=random.uniform(-50, 50),
            vy=random.uniform(-50, 50),
            size=random.uniform(2, 6),
            lifetime=random.uniform(2.0, 5.0),
            age=0.0,
            color=random.choice([self.primary_color, self.secondary_color, self.accent_color])
        )
        self.particles.append(particle)
    
    def _draw_hexagon(self, painter: QPainter, center: QPointF, size: float):
        """Draw a hexagon"""
        path = QPainterPath()
        
        for i in range(6):
            angle = math.pi / 3 * i
            x = center.x() + size * math.cos(angle)
            y = center.y() + size * math.sin(angle)
            
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        
        path.closeSubpath()
        painter.drawPath(path)


# Global renderer
_holographic_renderer: Optional[HolographicRenderer] = None


def get_holographic_renderer() -> HolographicRenderer:
    """Get global holographic renderer"""
    global _holographic_renderer
    if _holographic_renderer is None:
        _holographic_renderer = HolographicRenderer()
    return _holographic_renderer

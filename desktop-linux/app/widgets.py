from PyQt6.QtWidgets import QAbstractButton, QSizePolicy
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import QSize, QPropertyAnimation, pyqtProperty, QEasingCurve, Qt

class SwitchButton(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # Slider track & thumb metrics
        self.track_width = 40
        self.track_height = 20
        self.thumb_size = 14
        self.margin = 3
        
        # Animated thumb position property
        # Unchecked: X = margin = 3
        # Checked: X = track_width - thumb_size - margin = 40 - 14 - 3 = 23
        self._thumb_position = float(self.margin)
        
        self._animation = QPropertyAnimation(self, b"thumb_position", self)
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Connect clicked signal to animate state transition
        self.toggled.connect(self._animate_toggle)
        
        # Colors (Indigo/Violet accent for Life Tracker)
        self.color_track_unchecked = QColor("#1e1e24")
        self.color_track_checked = QColor("#6366f1")  # Indigo
        self.color_thumb = QColor("#ffffff")
        self.color_border = QColor("#2d2d3d")

    @pyqtProperty(float)
    def thumb_position(self):
        return self._thumb_position

    @thumb_position.setter
    def thumb_position(self, pos):
        self._thumb_position = pos
        self.update()

    def _animate_toggle(self, checked):
        self._animation.stop()
        start = self._thumb_position
        end = float(self.track_width - self.thumb_size - self.margin) if checked else float(self.margin)
        self._animation.setStartValue(start)
        self._animation.setEndValue(end)
        self._animation.start()

    def sizeHint(self):
        return QSize(self.track_width, self.track_height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Interpolate track background color based on position
        min_pos = float(self.margin)
        max_pos = float(self.track_width - self.thumb_size - self.margin)
        
        progress = 0.0
        if max_pos > min_pos:
            progress = (self._thumb_position - min_pos) / (max_pos - min_pos)
            progress = max(0.0, min(1.0, progress))
            
        # Linear color interpolation
        r = int(self.color_track_unchecked.red() + progress * (self.color_track_checked.red() - self.color_track_unchecked.red()))
        g = int(self.color_track_unchecked.green() + progress * (self.color_track_checked.green() - self.color_track_unchecked.green()))
        b = int(self.color_track_unchecked.blue() + progress * (self.color_track_checked.blue() - self.color_track_unchecked.blue()))
        track_color = QColor(r, g, b)
        
        # Draw track
        painter.setPen(QPen(self.color_border, 1))
        painter.setBrush(QBrush(track_color))
        painter.drawRoundedRect(0, 0, self.track_width, self.track_height, self.track_height / 2, self.track_height / 2)
        
        # Draw thumb
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.color_thumb))
        painter.drawEllipse(int(self._thumb_position), self.margin, self.thumb_size, self.thumb_size)
        
        painter.end()

    def setChecked(self, checked):
        # Override to snap thumb position without animation if set programmatically
        super().setChecked(checked)
        self._animation.stop()
        self._thumb_position = float(self.track_width - self.thumb_size - self.margin) if checked else float(self.margin)
        self.update()

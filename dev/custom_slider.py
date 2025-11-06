import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QAbstractSlider, QVBoxLayout, QLabel
)
from PySide6.QtGui import QPainter, QPen, QBrush, QFont
from PySide6.QtCore import Qt, QPointF, QRectF


class CustomValueSlider(QAbstractSlider):
    """
    A custom QAbstractSlider that draws its own ticks, numbers, and handle,
    and snaps to the specified singleStep.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # We only support horizontal for this example
        self.setOrientation(Qt.Orientation.Horizontal)
        
        # --- Internal state for dragging
        self._is_dragging = False

        # --- Constants for drawing
        # These define the visual appearance. Tweak them!
        self.HANDLE_RADIUS = 10
        self.TRACK_HEIGHT = 4
        self.TICK_HEIGHT = 8
        
        # Vertical padding to avoid clipping
        self.TOP_MARGIN = 60  # Increased to make room for floating value
        self.BOTTOM_MARGIN = 30 # Extra space for text
        self.LEFT_MARGIN = 15
        self.RIGHT_MARGIN = 15

        # Set a reasonable default size
        self.setMinimumHeight(self.TOP_MARGIN + self.BOTTOM_MARGIN + self.HANDLE_RADIUS * 2)
        self.setMinimumWidth(200)

    # --- Sizing Hints ---
    
    def sizeHint(self):
        # Provide a default "good" size
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        # Provide a minimum sensible size
        return (250, 75)

    # --- Mouse Handling ---
    
    def mousePressEvent(self, event):
        # Set the value on click and start "dragging"
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            new_value = self._value_from_pos(event.position())
            self.setValue(new_value)
            event.accept()

    def mouseMoveEvent(self, event):
        # If we are dragging, update the value
        if self._is_dragging:
            new_value = self._value_from_pos(event.position())
            self.setValue(new_value)
            event.accept()

    def mouseReleaseEvent(self, event):
        # Stop dragging
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            event.accept()

    # --- The Magic: Painting ---

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        
        usable_width = width - self.LEFT_MARGIN - self.RIGHT_MARGIN
        track_y = self.TOP_MARGIN + self.HANDLE_RADIUS

        # 1. --- Draw the Track ---
        track_pen = QPen(Qt.GlobalColor.gray, self.TRACK_HEIGHT)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawLine(self.LEFT_MARGIN, track_y, 
                         width - self.RIGHT_MARGIN, track_y)

        # 2. --- Draw Ticks and Numbers ---
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        font = QFont()
        font.setPointSize(10)
        fm = painter.fontMetrics()
        painter.setFont(font)
        
        step = self.singleStep()
        if step == 0:  
            return
            
        total_steps = int((self.maximum() - self.minimum()) / step)
        if total_steps <= 0:
            return

        # --- Dynamic Tick Calculation ---
        max_label_width = fm.horizontalAdvance(str(self.maximum())) + 20
        max_visible_ticks = max(1, usable_width // max_label_width)
        tick_interval = 1
        if total_steps > max_visible_ticks:
            tick_interval = round(total_steps / max_visible_ticks)
        
        for i in range(total_steps + 1):
            if i % tick_interval != 0 and i != total_steps:
                continue

            val = self.minimum() + (i * step)
            
            ratio = (val - self.minimum()) / (self.maximum() - self.minimum())
            x_pos = self.LEFT_MARGIN + (ratio * usable_width)

            painter.drawLine(int(x_pos), int(track_y - self.TICK_HEIGHT // 2), 
                             int(x_pos), int(track_y + self.TICK_HEIGHT // 2))

            text_rect = QRectF(x_pos - max_label_width / 2, track_y + self.TICK_HEIGHT, max_label_width, 20)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, str(val))

        # 3. --- Calculate Handle Position ---
        current_ratio = 0.0
        if (self.maximum() - self.minimum()) > 0:
            current_ratio = (self.value() - self.minimum()) / (self.maximum() - self.minimum())
            
        handle_x_center = self.LEFT_MARGIN + (current_ratio * usable_width)
        
        # Define handle dimensions
        HANDLE_WIDTH = 20
        HANDLE_HEIGHT = 10  # Reduced from 25 to original size
        ARROW_HEIGHT = 8
        
        # Calculate the top-left point of the rectangle
        rect_x = handle_x_center - HANDLE_WIDTH / 2
        rect_y = track_y - HANDLE_HEIGHT - ARROW_HEIGHT
        
        # Create the rectangle
        handle_rect = QRectF(rect_x, rect_y, HANDLE_WIDTH, HANDLE_HEIGHT)

        # Create the arrow polygon
        arrow_points = [
            QPointF(handle_x_center - HANDLE_WIDTH / 2, track_y - ARROW_HEIGHT),
            QPointF(handle_x_center + HANDLE_WIDTH / 2, track_y - ARROW_HEIGHT),
            QPointF(handle_x_center, track_y + 2)
        ]
        
        # 4. --- Draw Floating Value Box FIRST (behind handle) ---
        value_text = str(self.value())
        value_font = QFont()
        value_font.setPointSize(11)
        value_font.setBold(True)
        painter.setFont(value_font)
        value_fm = painter.fontMetrics()
        
        # Calculate size of text
        text_width = value_fm.horizontalAdvance(value_text)
        text_height = value_fm.height()
        
        # Box padding
        box_padding = 6
        box_width = text_width + box_padding * 2
        box_height = text_height + box_padding * 2
        
        # Position box above the handle
        box_x = handle_x_center - box_width / 2
        box_y = rect_y - box_height - 5  # 5px gap above handle
        
        # Clamp box_x to prevent it from going off the edges
        box_x = max(5, min(box_x, width - box_width - 5))
        
        # Draw the box
        value_box = QRectF(box_x, box_y, box_width, box_height)
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.setPen(QPen(Qt.GlobalColor.darkCyan, 2))
        painter.drawRoundedRect(value_box, 4, 4)
        
        # Draw the text
        painter.setPen(QPen(Qt.GlobalColor.darkCyan))
        painter.drawText(value_box, Qt.AlignmentFlag.AlignCenter, value_text)
        
        # 5. --- Draw the Handle (on top) ---
        painter.setBrush(QBrush(Qt.GlobalColor.darkCyan))
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        
        # Draw the rectangle
        painter.drawRect(handle_rect)
        
        # Draw the arrow
        painter.drawPolygon(arrow_points)


    # --- Helper Function ---
    
    def _value_from_pos(self, pos):
        """Helper to convert a mouse X-coordinate to a snapped value."""
        
        width = self.width()
        usable_width = width - self.LEFT_MARGIN - self.RIGHT_MARGIN
        
        if usable_width <= 0:
            return self.minimum()

        x = max(self.LEFT_MARGIN, min(pos.x(), width - self.RIGHT_MARGIN))
        ratio = (x - self.LEFT_MARGIN) / usable_width
        raw_value = self.minimum() + ratio * (self.maximum() - self.minimum())
        
        step = self.singleStep()
        if step == 0:
            return int(raw_value)
            
        snapped_val = round((raw_value - self.minimum()) / step) * step + self.minimum()
        return max(self.minimum(), min(self.maximum(), int(snapped_val)))


# --- Main Application Window (to test the slider) ---

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom QAbstractSlider Test")
        self.setGeometry(100, 100, 600, 200)

        # The new custom slider
        self.slider = CustomValueSlider()
        
        # --- Configure the slider as requested ---
        self.slider.setRange(1000, 5000)
        self.slider.setSingleStep(25)
        self.slider.setPageStep(25)
        self.slider.setValue(1500)

        # A label to show the slider's current value
        self.label = QLabel(f"Current Value: {self.slider.value()}")
        self.label.setFont(QFont("Arial", 16))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Connect the slider's signal to the label's slot
        self.slider.valueChanged.connect(self.update_label)

        # Set up layout
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.slider)
        layout.addStretch()
        layout.addWidget(self.label)
        layout.addStretch()
        self.setLayout(layout)

    def update_label(self, value):
        self.label.setText(f"Current Value: {value}")


# --- Run the application ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
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
        self.TOP_MARGIN = 5
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

    # def paintEvent(self, event):
    #     painter = QPainter(self)
    #     painter.setRenderHint(QPainter.RenderHint.Antialiasing) # Makes circles smooth

    #     # Get widget dimensions
    #     width = self.width()
    #     height = self.height()
        
    #     # Calculate the usable "track" area
    #     usable_width = width - self.LEFT_MARGIN - self.RIGHT_MARGIN
    #     # Y-position for the center of the track and handle
    #     track_y = self.TOP_MARGIN + self.HANDLE_RADIUS


    #     # 1. --- Draw the Track ---
    #     track_pen = QPen(Qt.GlobalColor.gray, self.TRACK_HEIGHT)
    #     track_pen.setCapStyle(Qt.PenCapStyle.RoundCap) # This is the correct way
    #     painter.setPen(track_pen)
    #     painter.drawLine(self.LEFT_MARGIN, track_y, 
    #                      width - self.RIGHT_MARGIN, track_y)

    #     # 2. --- Draw Ticks and Numbers ---
    #     painter.setPen(QPen(Qt.GlobalColor.black, 2))
    #     font = QFont()
    #     font.setPointSize(10)
    #     painter.setFont(font)
        
    #     # Calculate how many steps we have
    #     step = self.singleStep()
    #     if step == 0:  # Avoid division by zero if step not set
    #         return
            
    #     num_steps = int((self.maximum() - self.minimum()) / step)
        
    #     for i in range(num_steps + 1):
    #         val = self.minimum() + (i * step)
            
    #         # Calculate the x-position for this value
    #         ratio = (val - self.minimum()) / (self.maximum() - self.minimum())
    #         x_pos = self.LEFT_MARGIN + (ratio * usable_width)

    #         # Draw the tick
    #         painter.drawLine(int(x_pos), int(track_y - self.TICK_HEIGHT // 2), 
    #                          int(x_pos), int(track_y + self.TICK_HEIGHT // 2))

    #         # Draw the number text
    #         text_rect = QRectF(x_pos - 40, track_y + self.TICK_HEIGHT, 80, 20)
    #         painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, str(val))

    #     # 3. --- Draw the Handle ---
        
    #     # Calculate the handle's x-position
    #     current_ratio = 0.0
    #     # Avoid division by zero if max == min
    #     if (self.maximum() - self.minimum()) > 0:
    #         current_ratio = (self.value() - self.minimum()) / (self.maximum() - self.minimum())
            
    #     handle_x = self.LEFT_MARGIN + (current_ratio * usable_width)
    #     handle_pos = QPointF(handle_x, track_y)

    #     # Set brush and pen for the handle
    #     painter.setBrush(QBrush(Qt.GlobalColor.darkCyan))
    #     painter.setPen(QPen(Qt.GlobalColor.black, 1))
        
    #     painter.drawEllipse(handle_pos, self.HANDLE_RADIUS, self.HANDLE_RADIUS)
    #     # ^^^ The stray line was here. It is now gone. ^^^

    # Draws a rectange with point as the slide element.
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        
        usable_width = width - self.LEFT_MARGIN - self.RIGHT_MARGIN
        track_y = self.TOP_MARGIN + self.HANDLE_RADIUS # This will now be the top of the handle/arrow base

        # 1. --- Draw the Track ---
        track_pen = QPen(Qt.GlobalColor.gray, self.TRACK_HEIGHT)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawLine(self.LEFT_MARGIN, track_y, 
                         width - self.RIGHT_MARGIN, track_y)

        # 2. --- Draw Ticks and Numbers ---
        # (This part remains unchanged)
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
        # Determine a reasonable interval for drawing ticks to avoid overlap.
        # We'll use the width of the largest number as a guide for spacing.
        max_label_width = fm.horizontalAdvance(str(self.maximum())) + 20 # Add padding
        
        # Calculate how many ticks can fit without crowding
        max_visible_ticks = max(1, usable_width // max_label_width)
        
        # Calculate the step interval to achieve this
        tick_interval = 1
        if total_steps > max_visible_ticks:
            tick_interval = round(total_steps / max_visible_ticks)
        
        for i in range(total_steps + 1):
            # Only draw a tick if it's on our calculated interval
            if i % tick_interval != 0 and i != total_steps:
                continue

            val = self.minimum() + (i * step)
            
            ratio = (val - self.minimum()) / (self.maximum() - self.minimum())
            x_pos = self.LEFT_MARGIN + (ratio * usable_width)

            painter.drawLine(int(x_pos), int(track_y - self.TICK_HEIGHT // 2), 
                             int(x_pos), int(track_y + self.TICK_HEIGHT // 2))

            text_rect = QRectF(x_pos - max_label_width / 2, track_y + self.TICK_HEIGHT, max_label_width, 20)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, str(val))

        # 3. --- Draw the Handle (Rectangle with Arrow) ---
        
        current_ratio = 0.0
        if (self.maximum() - self.minimum()) > 0:
            current_ratio = (self.value() - self.minimum()) / (self.maximum() - self.minimum())
            
        handle_x_center = self.LEFT_MARGIN + (current_ratio * usable_width)
        
        # Define handle dimensions
        HANDLE_WIDTH = 20
        HANDLE_HEIGHT = 25
        ARROW_HEIGHT = 8 # Height of the arrow triangle
        
        # Calculate the top-left point of the rectangle
        rect_x = handle_x_center - HANDLE_WIDTH / 2
        rect_y = track_y - HANDLE_HEIGHT - ARROW_HEIGHT # Move up from the track
        
        # Create the rectangle
        handle_rect = QRectF(rect_x, rect_y, HANDLE_WIDTH, HANDLE_HEIGHT)

        # Create the arrow polygon (3 points for a triangle)
        arrow_points = [
            QPointF(handle_x_center - HANDLE_WIDTH / 2, track_y - ARROW_HEIGHT), # Bottom-left of rect
            QPointF(handle_x_center + HANDLE_WIDTH / 2, track_y - ARROW_HEIGHT), # Bottom-right of rect
            QPointF(handle_x_center, track_y + 2) # Point of the arrow, a little below the track
        ]
        
        # Set brush and pen for the handle
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
        
        # Handle edge case where usable_width is zero to prevent division by zero
        if usable_width <= 0:
            return self.minimum()

        # Get mouse x, clamped within the usable area
        x = max(self.LEFT_MARGIN, min(pos.x(), width - self.RIGHT_MARGIN))
        
        # Calculate the ratio (0.0 to 1.0) of the click
        ratio = (x - self.LEFT_MARGIN) / usable_width
        
        # Convert ratio to a raw value
        raw_value = self.minimum() + ratio * (self.maximum() - self.minimum())
        
        # --- This is the "snapping" logic ---
        step = self.singleStep()
        if step == 0:
            return int(raw_value)
            
        # 1. Find nearest multiple of 'step' from the minimum
        snapped_val = round((raw_value - self.minimum()) / step) * step + self.minimum()
        
        # 2. Clamp to min/max
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
        self.slider.setSingleStep(25) # This is crucial for our drawing/snapping
        self.slider.setPageStep(25)
        self.slider.setValue(1500)     # Set initial value

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
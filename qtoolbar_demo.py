from PySide6.QtWidgets import (QMainWindow, QToolBar, QMenu, QApplication, 
                                QWidget, QVBoxLayout)
from PySide6.QtGui import QIcon, QAction, QFont
from PySide6.QtCore import Qt, Signal, QSize
import sys


class GuitarToolbar(QMainWindow):
    """Main window with toolbar for guitar learning application."""
    
    # Signals for toolbar actions
    play_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()
    speed_changed = Signal(float)
    previous_part_clicked = Signal()
    next_part_clicked = Signal()
    loop_toggled = Signal(bool)
    auto_play_toggled = Signal(bool)
    auto_advance_toggled = Signal(bool)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Guitar Learning Tool")
        self.setGeometry(100, 100, 1000, 600)
        
        # State variables
        self.is_playing = False
        self.is_looping = False
        self.auto_play = False
        self.auto_advance = False
        self.current_speed = 1.0
        
        # Setup UI
        self._create_toolbar()
        self._create_central_widget()
        
    def _create_toolbar(self):
        """Create and configure the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # === PLAYBACK CONTROLS ===
        
        # Play/Pause action (toggles between play and pause)
        self.play_pause_action = QAction(
            QIcon("icons/play.svg"), 
            "Play", 
            self
        )
        self.play_pause_action.triggered.connect(self._toggle_play_pause)
        self.play_pause_action.setShortcut("Space")
        toolbar.addAction(self.play_pause_action)
        
        # Stop action
        stop_action = QAction(QIcon("icons/stop.svg"), "Stop", self)
        stop_action.triggered.connect(self._on_stop)
        stop_action.setShortcut("S")
        toolbar.addAction(stop_action)
        
        # Speed control with dropdown menu (text only, no icon)
        speed_action = QAction("1.0x", self)
        speed_action.setFont(self._get_bold_font())
        speed_action.setToolTip("Playback Speed")
        speed_menu = QMenu(self)
        
        # Add speed options with checkable actions
        self.speed_actions = {}
        for speed in [0.25, 0.5, 0.75, 1.0]:
            speed_option = speed_menu.addAction(f"{speed}x")
            speed_option.setCheckable(True)
            speed_option.triggered.connect(
                lambda checked, s=speed: self._set_speed(s)
            )
            self.speed_actions[speed] = speed_option
        
        # Set default speed as checked
        self.speed_actions[1.0].setChecked(True)

        # Show menu when action is triggered (aligned to bottom of toolbar)
        # def show_speed_menu():
        #     widget = toolbar.widgetForAction(speed_action)
        #     pos = widget.mapToGlobal(widget.rect().bottomLeft())
        #     speed_menu.exec(pos)
        
        speed_action.setMenu(speed_menu)
        toolbar.addAction(speed_action)
        self.speed_action = speed_action  # Keep reference to update text

        # speed_action.triggered.connect(show_speed_menu)
        # toolbar.addAction(speed_action)
        # self.speed_action = speed_action  
        
        # Loop action (toggle button)
        self.loop_action = QAction(QIcon("icons/loop.svg"), "Loop", self)
        self.loop_action.setCheckable(True)
        self.loop_action.toggled.connect(self._on_loop_toggled)
        self.loop_action.setShortcut("L")
        toolbar.addAction(self.loop_action)
        
        # Separator between control groups
        toolbar.addSeparator()
        
        # === NAVIGATION CONTROLS ===
        
        # Previous part
        prev_action = QAction(QIcon("icons/back.svg"), "Previous Part", self)
        prev_action.triggered.connect(self._on_previous)
        prev_action.setShortcut(Qt.Key_Left)
        toolbar.addAction(prev_action)
        
        # Next part
        next_action = QAction(QIcon("icons/forward.svg"), "Next Part", self)
        next_action.triggered.connect(self._on_next)
        next_action.setShortcut(Qt.Key_Right)
        toolbar.addAction(next_action)
        
        # Separator before options
        toolbar.addSeparator()
        
        # === OPTIONS MENU ===
        
        options_action = QAction(QIcon("icons/options.svg"), "Options", self)
        options_menu = QMenu(self)
        
        # Auto-play option
        self.auto_play_action = options_menu.addAction("Auto-play on Part Select")
        self.auto_play_action.setCheckable(True)
        self.auto_play_action.toggled.connect(self._on_auto_play_toggled)
        
        # Auto-advance option
        self.auto_advance_action = options_menu.addAction("Auto-advance After Playback")
        self.auto_advance_action.setCheckable(True)
        self.auto_advance_action.toggled.connect(self._on_auto_advance_toggled)
        
        # options_action.setMenu(options_menu)
        # toolbar.addAction(options_action)

        # Show menu when action is triggered
        # options_action.triggered.connect(lambda: options_menu.exec(self.mapToGlobal(toolbar.widgetForAction(options_action).pos())))
        # toolbar.addAction(options_action)
        # self.options_menu = options_menu  # Keep reference

        # Show menu when action is triggered (aligned to bottom of toolbar)
        def show_options_menu():
            widget = toolbar.widgetForAction(options_action)
            pos = widget.mapToGlobal(widget.rect().bottomLeft())
            options_menu.exec(pos)

        options_action.triggered.connect(show_options_menu)
        toolbar.addAction(options_action)
        self.options_menu = options_menu  # Keep reference
        
    def _create_central_widget(self):
        """Create placeholder central widget (replace with your HTML fretboard)."""
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Here you would add your HTML/WebEngine widget for the fretboard
        # For now, just a placeholder
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    def _get_bold_font(self):
        """Create a bold font for the speed text."""
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)  # Slightly larger than default
        return font
        
    # === SLOT METHODS ===
    
    def _toggle_play_pause(self):
        """Toggle between play and pause states."""
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.play_pause_action.setIcon(QIcon("icons/pause.svg"))
            self.play_pause_action.setText("Pause")
            self.play_clicked.emit()
        else:
            self.play_pause_action.setIcon(QIcon("icons/play.svg"))
            self.play_pause_action.setText("Play")
            self.pause_clicked.emit()
    
    def _on_stop(self):
        """Handle stop button click."""
        self.is_playing = False
        self.play_pause_action.setIcon(QIcon("icons/play.svg"))
        self.play_pause_action.setText("Play")
        self.stop_clicked.emit()
    
    def _set_speed(self, speed):
        """Set playback speed."""
        # Uncheck all speed options
        for s, action in self.speed_actions.items():
            action.setChecked(s == speed)
        
        self.current_speed = speed
        self.speed_action.setText(f"{speed}x")
        self.speed_changed.emit(speed)
    
    def _on_loop_toggled(self, checked):
        """Handle loop toggle."""
        self.is_looping = checked
        self.loop_toggled.emit(checked)
    
    def _on_previous(self):
        """Navigate to previous part."""
        self.previous_part_clicked.emit()
    
    def _on_next(self):
        """Navigate to next part."""
        self.next_part_clicked.emit()
    
    def _on_auto_play_toggled(self, checked):
        """Handle auto-play toggle."""
        self.auto_play = checked
        self.auto_play_toggled.emit(checked)
    
    def _on_auto_advance_toggled(self, checked):
        """Handle auto-advance toggle."""
        self.auto_advance = checked
        self.auto_advance_toggled.emit(checked)
    
    # === PUBLIC METHODS ===
    
    def update_playback_state(self, is_playing):
        """Update UI to reflect playback state (called from external controller)."""
        self.is_playing = is_playing
        if is_playing:
            self.play_pause_action.setIcon(QIcon("icons/pause.svg"))
            self.play_pause_action.setText("Pause")
        else:
            self.play_pause_action.setIcon(QIcon("icons/play.svg"))
            self.play_pause_action.setText("Play")
    
    def enable_navigation_buttons(self, prev_enabled, next_enabled):
        """Enable/disable navigation buttons based on current part."""
        # You would store references to prev/next actions to enable/disable them
        pass


# Example usage
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = GuitarToolbar()
    
    # Connect signals to test functionality
    window.play_clicked.connect(lambda: print("Play clicked"))
    window.pause_clicked.connect(lambda: print("Pause clicked"))
    window.stop_clicked.connect(lambda: print("Stop clicked"))
    window.speed_changed.connect(lambda s: print(f"Speed changed to {s}x"))
    window.previous_part_clicked.connect(lambda: print("Previous part"))
    window.next_part_clicked.connect(lambda: print("Next part"))
    window.loop_toggled.connect(lambda checked: print(f"Loop: {checked}"))
    window.auto_play_toggled.connect(lambda checked: print(f"Auto-play: {checked}"))
    window.auto_advance_toggled.connect(lambda checked: print(f"Auto-advance: {checked}"))
    
    window.show()
    sys.exit(app.exec())
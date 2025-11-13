"""
Main application window with toolbar.
Based on qtoolbar_demo.py, adapted for fretboard player integration.
"""

from PySide6.QtWidgets import QMainWindow, QToolBar, QMenu, QWidget
from PySide6.QtGui import QIcon, QAction, QFont, QActionGroup
from PySide6.QtCore import Qt, Signal, QSize


class MainWindow(QMainWindow):
    """
    Main application window with toolbar for guitar learning.
    Provides signals for all user actions.
    """

    # Playback control signals
    play_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()

    # Speed and loop controls
    speed_changed = Signal(float)
    loop_toggled = Signal(bool)

    # Navigation signals
    previous_part_clicked = Signal()
    next_part_clicked = Signal()

    # Option signals
    auto_play_toggled = Signal(bool)
    auto_advance_toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guitar Learning Tool")
        self.setGeometry(100, 100, 1000, 600)

        # State variables
        self.is_playing = False
        self.is_looping = False
        self.auto_play = False
        self.auto_advance = False
        self.current_speed = 1.0

        # Create toolbar
        self._create_toolbar()

    def _create_toolbar(self):
        """Create and configure the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolButton {
                padding: 4px;
                border: none;
                min-height: 24px;
            }
            QToolButton:hover {
                background-color: palette(dark);
                border-radius: 4px;
            }
            QToolButton:pressed, QToolButton:checked {
                background-color: palette(mid);
                border-radius: 4px;
            }
            QToolButton::menu-indicator {
                subcontrol-origin: padding;
                subcontrol-position: right center;
            }
            QToolButton::menu-button {
                border: none;
            }
        """)
        self.addToolBar(toolbar)
        
        # Add a spacer to the left of the first icon
        left_spacer = QWidget()
        left_spacer.setFixedWidth(8)
        toolbar.addWidget(left_spacer)
        
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
        
        speed_action_group = QActionGroup(self)
        speed_action_group.setExclusive(True)
        
        # Add speed options with checkable actions
        self.speed_actions = {}
        for speed in [0.25, 0.5, 0.75, 1.0]:
            speed_option = speed_menu.addAction(f"{speed}x")
            speed_option.setCheckable(True)
            speed_action_group.addAction(speed_option)
            speed_option.triggered.connect(
                lambda checked, s=speed: self._set_speed(s)
            )
            self.speed_actions[speed] = speed_option
        
        # Set default speed as checked
        self.speed_actions[1.0].setChecked(True)
        
        speed_action.setMenu(speed_menu)
        
        # Connect triggered signal to show menu when clicking the text
        def show_speed_menu():
            widget = toolbar.widgetForAction(speed_action)
            pos = widget.mapToGlobal(widget.rect().bottomLeft())
            speed_menu.exec(pos)
        
        speed_action.triggered.connect(show_speed_menu)
        toolbar.addAction(speed_action)
        
        # Use DelayedPopup to show button press feedback
        speed_button = toolbar.widgetForAction(speed_action)
        speed_button.setPopupMode(speed_button.ToolButtonPopupMode.DelayedPopup)
        
        self.speed_action = speed_action  # Keep reference to update text

        # Loop action (toggle button)
        self.loop_action = QAction(QIcon("icons/loop.svg"), "Loop", self)
        self.loop_action.setCheckable(True)
        self.loop_action.toggled.connect(self._on_loop_toggled)
        self.loop_action.setShortcut("L")

        toolbar.addAction(self.loop_action)
        toolbar.addAction(speed_action)
        
        # === OPTIONS MENU (moved to first group) ===
        
        options_action = QAction(QIcon("icons/options.svg"), "Options", self)
        options_menu = QMenu(self)
        
        # Auto-play option with updated text
        self.auto_play_action = options_menu.addAction("Auto-play part")
        self.auto_play_action.setCheckable(True)
        self.auto_play_action.toggled.connect(self._on_auto_play_toggled)
        
        # Auto-advance option with updated text
        self.auto_advance_action = options_menu.addAction("Auto-advance part")
        self.auto_advance_action.setCheckable(True)
        self.auto_advance_action.toggled.connect(self._on_auto_advance_toggled)

        # Show menu when action is triggered (aligned to bottom of toolbar)
        def show_options_menu():
            widget = toolbar.widgetForAction(options_action)
            pos = widget.mapToGlobal(widget.rect().bottomLeft())
            options_menu.exec(pos)

        options_action.triggered.connect(show_options_menu)
        toolbar.addAction(options_action)
        self.options_menu = options_menu  # Keep reference
        
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

    def _get_bold_font(self):
        """Create a bold font for the speed text."""
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
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
        self.speed_actions[speed].setChecked(True)
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
        """
        Update UI to reflect playback state (called from external controller).

        Args:
            is_playing: Boolean indicating if playback is active
        """
        self.is_playing = is_playing
        if is_playing:
            self.play_pause_action.setIcon(QIcon("icons/pause.svg"))
            self.play_pause_action.setText("Pause")
        else:
            self.play_pause_action.setIcon(QIcon("icons/play.svg"))
            self.play_pause_action.setText("Play")

    def enable_navigation_buttons(self, prev_enabled, next_enabled):
        """
        Enable/disable navigation buttons based on current part.

        Args:
            prev_enabled: Boolean to enable/disable previous button
            next_enabled: Boolean to enable/disable next button
        """
        self.prev_action.setEnabled(prev_enabled)
        self.next_action.setEnabled(next_enabled)

    def set_central_content(self, widget):
        """
        Set the central widget of the window.

        Args:
            widget: QWidget to display in the central area
        """
        self.setCentralWidget(widget)

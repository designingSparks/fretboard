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

    # File menu signals
    open_lesson_clicked = Signal()
    recent_lesson_clicked = Signal(str)  # Emits lesson filename

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

        # Recent lessons state
        self.recent_lessons = []  # List of tuples: (filename, name)
        self.recent_menu = None
        self.recent_action = None
        self.separator_action = None

        # Create menu and toolbar
        self._create_menu()
        self._create_toolbar()

    def _create_menu(self):
        """Create the menu bar with File menu."""
        menubar = self.menuBar()

        # File menu
        self.file_menu = menubar.addMenu("File")

        # Open action
        open_action = QAction("Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open_lesson)
        self.file_menu.addAction(open_action)

        # Open Recent - initially a disabled action, becomes submenu when populated
        self.recent_action = QAction("Open Recent", self)
        self.recent_action.setEnabled(False)  # Initially disabled
        self.file_menu.addAction(self.recent_action)

        # Separator before Exit
        self.separator_action = self.file_menu.addSeparator()

        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)

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
        
        # Play/Stop toggle action
        self.play_stop_action = QAction(
            QIcon("icons/play.svg"),
            "Play",
            self
        )
        self.play_stop_action.triggered.connect(self._on_play_stop_toggle)
        self.play_stop_action.setShortcut("Space")
        toolbar.addAction(self.play_stop_action)
        
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
        self.prev_action = QAction(QIcon("icons/back.svg"), "Previous Part", self)
        self.prev_action.triggered.connect(self._on_previous)
        self.prev_action.setShortcut(Qt.Key_Left)
        self.prev_action.setEnabled(False)  # Disabled until lesson is loaded
        toolbar.addAction(self.prev_action)

        # Next part
        self.next_action = QAction(QIcon("icons/forward.svg"), "Next Part", self)
        self.next_action.triggered.connect(self._on_next)
        self.next_action.setShortcut(Qt.Key_Right)
        self.next_action.setEnabled(False)  # Disabled until lesson is loaded
        toolbar.addAction(self.next_action)

    def _get_bold_font(self):
        """Create a bold font for the speed text."""
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        return font

    # === SLOT METHODS ===

    def _on_play_stop_toggle(self):
        """Handle play/stop button toggle - switches between play and stop."""
        if self.is_playing:
            # Currently playing, so stop
            self.is_playing = False
            self.play_stop_action.setIcon(QIcon("icons/play.svg"))
            self.play_stop_action.setText("Play")
            self.stop_clicked.emit()
        else:
            # Currently stopped, so play
            self.is_playing = True
            self.play_stop_action.setIcon(QIcon("icons/stop.svg"))
            self.play_stop_action.setText("Stop")
            self.play_clicked.emit()

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

    def _on_open_lesson(self):
        """Handle File > Open menu action."""
        self.open_lesson_clicked.emit()

    # === PUBLIC METHODS ===

    def update_playback_state(self, is_playing):
        """
        Update UI to reflect playback state (called from external controller).
        This is used to reset the button to play state when playback finishes.

        Args:
            is_playing: Boolean indicating if playback is active
        """
        self.is_playing = is_playing
        if is_playing:
            self.play_stop_action.setIcon(QIcon("icons/stop.svg"))
            self.play_stop_action.setText("Stop")
        else:
            self.play_stop_action.setIcon(QIcon("icons/play.svg"))
            self.play_stop_action.setText("Play")

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

    def load_recent_lessons(self, recent_list):
        """
        Load recent lessons from settings.

        Args:
            recent_list: List of tuples (filename, name)
        """
        self.recent_lessons = recent_list[:10]  # Limit to 10
        self.update_recent_menu()

    def add_recent_lesson(self, filename, name):
        """
        Add a lesson to the recent lessons list.

        Args:
            filename: Lesson filename (without .py)
            name: Display name of the lesson
        """
        # Remove if already in list
        self.recent_lessons = [
            (fn, nm) for fn, nm in self.recent_lessons if fn != filename
        ]

        # Add to front
        self.recent_lessons.insert(0, (filename, name))

        # Limit to 10
        self.recent_lessons = self.recent_lessons[:10]

        # Update menu
        self.update_recent_menu()

    def get_recent_lessons(self):
        """
        Get the current recent lessons list.

        Returns:
            List of tuples (filename, name)
        """
        return self.recent_lessons

    def update_recent_menu(self):
        """Update the Open Recent menu - converts between action and submenu as needed."""
        if self.recent_lessons:
            # Convert to submenu if not already
            if self.recent_menu is None:
                # Remove the disabled action
                self.file_menu.removeAction(self.recent_action)

                # Create and add the submenu (before the separator)
                self.recent_menu = QMenu("Open Recent", self)
                self.file_menu.insertMenu(self.separator_action, self.recent_menu)

            # Clear and populate the menu
            self.recent_menu.clear()
            for filename, name in self.recent_lessons:
                # Format as "Name"
                display_text = name

                # Create action and connect
                action = self.recent_menu.addAction(display_text)
                action.triggered.connect(
                    lambda _, fn=filename: self.recent_lesson_clicked.emit(fn)
                )
        else:
            # Convert back to disabled action if needed
            if self.recent_menu is not None:
                # Remove the submenu
                self.file_menu.removeAction(self.recent_menu.menuAction())
                self.recent_menu = None

                # Re-add the disabled action (before the separator)
                self.file_menu.insertAction(self.separator_action, self.recent_action)

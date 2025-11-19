"""
Lesson Main Window - Test Application
Main window for testing the lesson browser dialog integration
Note: I couldn't find a way of disabling the open recent menu item, which itself has a menu.
To disable it (greyed out and non hoverable), I had to create a standard menu item.
When there are recent items, I remove the disabled action and created the submenu.
"""

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QMenu
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
import sys

from lesson_browser import LessonBrowser, LESSONS


class LessonMainWindow(QMainWindow):
    """Main window for lesson browser test application"""

    def __init__(self):
        super().__init__()
        self.recent_lessons = []  # Session-only recent lessons list

        self.setWindowTitle("Lesson Browser Test Application")
        self.resize(800, 400)

        self.setup_ui()
        self.create_menu()

    def setup_ui(self):
        """Initialize the user interface"""
        # Central widget with a simple label
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)

        # Test label
        self.label = QLabel("Test application for lesson_browser.py")
        self.label.setStyleSheet("font-size: 18px; padding: 20px;")
        layout.addWidget(self.label)

    def create_menu(self):
        """Create the menu bar with File menu"""
        menubar = self.menuBar()

        # File menu
        self.file_menu = menubar.addMenu("File")

        # Open action
        open_action = QAction("Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_lesson_browser)
        self.file_menu.addAction(open_action)

        # Open Recent - initially a disabled action, becomes submenu when populated
        # This is the only way to get a greyed out menu. Greying out
        self.recent_menu = None
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

    def open_lesson_browser(self):
        """Open the lesson browser dialog"""
        dialog = LessonBrowser(self)

        # Connect to lesson selected signal
        dialog.lessonSelected.connect(self.on_lesson_selected)

        # Show modal dialog
        result = dialog.exec()

        if result == LessonBrowser.Accepted:
            print("Dialog accepted")
        else:
            print("Dialog cancelled")

    def on_lesson_selected(self, lesson_data):
        """Handle lesson selection from the dialog"""
        # Print lesson details to terminal
        print(f"\n{'='*60}")
        print(f"Selected Lesson Details:")
        print(f"  Name:       {lesson_data['name']}")
        print(f"  Key:        {lesson_data['key']}")
        print(f"  Type:       {lesson_data['type']}")
        print(f"  Difficulty: {lesson_data['difficulty']}")
        print(f"{'='*60}\n")

        # Add to recent lessons (avoid duplicates, keep last 10)
        lesson_name = lesson_data['name']
        if lesson_name in self.recent_lessons:
            self.recent_lessons.remove(lesson_name)
        self.recent_lessons.insert(0, lesson_name)
        self.recent_lessons = self.recent_lessons[:10]

        # Update recent menu
        self.update_recent_menu()

    def update_recent_menu(self):
        """Update the Open Recent menu - converts between action and submenu as needed"""
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
            for lesson_name in self.recent_lessons:
                lesson_data = next((l for l in LESSONS if l["name"] == lesson_name), None)
                if lesson_data:
                    # Format as "Name | Key | Type"
                    display_text = f"{lesson_data['name']} • {lesson_data['key']} • {lesson_data['type']}"

                    # Create action and connect
                    action = self.recent_menu.addAction(display_text)
                    action.triggered.connect(
                        lambda _, data=lesson_data: self.open_recent_lesson(data)
                    )
        else:
            # Convert back to disabled action if needed
            if self.recent_menu is not None:
                # Remove the submenu
                self.file_menu.removeAction(self.recent_menu.menuAction())
                self.recent_menu = None

                # Re-add the disabled action (before the separator)
                self.file_menu.insertAction(self.separator_action, self.recent_action)

    def open_recent_lesson(self, lesson_data):
        """Open a lesson directly from the recent menu (bypass dialog)"""
        # Print lesson details to terminal
        print(f"\n{'='*60}")
        print(f"Opening Recent Lesson:")
        print(f"  Name:       {lesson_data['name']}")
        print(f"  Key:        {lesson_data['key']}")
        print(f"  Type:       {lesson_data['type']}")
        print(f"  Difficulty: {lesson_data['difficulty']}")
        print(f"{'='*60}\n")

        # Move to front of recent lessons list
        lesson_name = lesson_data['name']
        if lesson_name in self.recent_lessons:
            self.recent_lessons.remove(lesson_name)
        self.recent_lessons.insert(0, lesson_name)
        self.recent_lessons = self.recent_lessons[:10]

        # Update recent menu
        self.update_recent_menu()


def main():
    app = QApplication(sys.argv)
    window = LessonMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

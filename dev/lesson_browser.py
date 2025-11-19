"""
Guitar Lesson Browser - PySide6 Dialog
A dialog for browsing and selecting guitar lessons with filtering
"""

from PySide6.QtWidgets import (
    QApplication, QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QHeaderView, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal
import sys


# Sample lesson data
LESSONS = [
    {"name": "Major Triad Shapes", "key": "C", "type": "Triad", "difficulty": "Beginner"},
    {"name": "Minor Triad Inversions", "key": "Am", "type": "Triad", "difficulty": "Intermediate"},
    {"name": "Diminished Triad Exercise", "key": "Bdim", "type": "Triad", "difficulty": "Intermediate"},
    {"name": "Major Scale Patterns", "key": "G", "type": "Scale", "difficulty": "Beginner"},
    {"name": "Natural Minor Scale", "key": "Em", "type": "Scale", "difficulty": "Beginner"},
    {"name": "Pentatonic Scale Box Shapes", "key": "A", "type": "Scale", "difficulty": "Beginner"},
    {"name": "Dorian Mode Practice", "key": "D", "type": "Scale", "difficulty": "Advanced"},
    {"name": "Augmented Triad Study", "key": "Caug", "type": "Triad", "difficulty": "Advanced"},
    {"name": "Blues Scale Licks", "key": "E", "type": "Scale", "difficulty": "Intermediate"},
    {"name": "Classic Rock Riff", "key": "A", "type": "Riff", "difficulty": "Beginner"},
    {"name": "Blues Shuffle Pattern", "key": "E", "type": "Riff", "difficulty": "Intermediate"},
    {"name": "Metal Power Chord Riff", "key": "Dm", "type": "Riff", "difficulty": "Intermediate"},
    {"name": "Major 7th Arpeggios", "key": "Cmaj7", "type": "Triad", "difficulty": "Advanced"},
    {"name": "Harmonic Minor Scale", "key": "Am", "type": "Scale", "difficulty": "Advanced"},
    {"name": "Funk Rhythm Riff", "key": "G", "type": "Riff", "difficulty": "Intermediate"},
    {"name": "Chromatic Scale Exercise", "key": "C", "type": "Scale", "difficulty": "Beginner"},
    {"name": "Jazz Swing Riff", "key": "Bb", "type": "Riff", "difficulty": "Advanced"},
    {"name": "Suspended Triad Voicings", "key": "Dsus", "type": "Triad", "difficulty": "Intermediate"},
]


class LessonBrowser(QDialog):
    """Dialog for browsing and selecting guitar lessons"""

    # Signal emitted when a lesson is selected
    lessonSelected = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_lessons = LESSONS.copy()
        self.current_filter = "All"
        self.selected_lesson = None  # Store selected lesson data

        self.setWindowTitle("Guitar Lesson Browser")
        self.resize(900, 600)

        self.setup_ui()
        self.populate_table()
        
    def setup_ui(self):
        """Initialize the user interface"""
        # Main layout for dialog
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        # Category filter section
        category_widget = self.create_category_filter()
        main_layout.addWidget(category_widget)

        # Filters section
        filter_widget = self.create_filter_widget()
        main_layout.addWidget(filter_widget)

        # Table
        self.table = self.create_table()
        main_layout.addWidget(self.table)

        # Action buttons (Open/Cancel)
        action_widget = self.create_action_buttons()
        main_layout.addWidget(action_widget)
        
    def create_category_filter(self):
        """Create the category filter buttons"""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setMaximumHeight(60)

        layout = QHBoxLayout(frame)

        # Category label
        label = QLabel("Category:")
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)

        layout.addSpacing(10)

        # Category buttons
        self.btn_all = QPushButton("All")
        self.btn_all.setCheckable(True)
        self.btn_all.setChecked(True)
        self.btn_all.clicked.connect(lambda: self.filter_by_category("All"))
        layout.addWidget(self.btn_all)

        self.btn_triads = QPushButton("Triads")
        self.btn_triads.setCheckable(True)
        self.btn_triads.clicked.connect(lambda: self.filter_by_category("Triad"))
        layout.addWidget(self.btn_triads)

        self.btn_scales = QPushButton("Scales")
        self.btn_scales.setCheckable(True)
        self.btn_scales.clicked.connect(lambda: self.filter_by_category("Scale"))
        layout.addWidget(self.btn_scales)

        # Group buttons for mutual exclusivity
        self.category_buttons = [self.btn_all, self.btn_triads, self.btn_scales]

        # Add stretch to push everything to the left
        layout.addStretch()

        return frame
        
    def create_filter_widget(self):
        """Create the column filter dropdowns"""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setMaximumHeight(60)
        
        layout = QHBoxLayout(frame)
        
        # Filter label
        filter_label = QLabel("Filters:")
        filter_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(filter_label)
        
        layout.addSpacing(10)
        
        # Key filter
        layout.addWidget(QLabel("Key:"))
        self.key_filter = QComboBox()
        self.key_filter.addItem("All")
        keys = sorted(set(lesson["key"] for lesson in self.all_lessons))
        self.key_filter.addItems(keys)
        self.key_filter.currentTextChanged.connect(self.apply_filters)
        layout.addWidget(self.key_filter)
        
        layout.addSpacing(20)
        
        # Type filter
        layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItem("All")
        types = sorted(set(lesson["type"] for lesson in self.all_lessons))
        self.type_filter.addItems(types)
        self.type_filter.currentTextChanged.connect(self.apply_filters)
        layout.addWidget(self.type_filter)
        
        layout.addSpacing(20)
        
        # Difficulty filter
        layout.addWidget(QLabel("Difficulty:"))
        self.difficulty_filter = QComboBox()
        self.difficulty_filter.addItem("All")
        difficulties = ["Beginner", "Intermediate", "Advanced"]
        self.difficulty_filter.addItems(difficulties)
        self.difficulty_filter.currentTextChanged.connect(self.apply_filters)
        layout.addWidget(self.difficulty_filter)
        
        layout.addSpacing(20)
        
        # Reset button
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_filters)
        layout.addWidget(reset_btn)
        
        layout.addStretch()
        
        return frame
        
    def create_table(self):
        """Create the lessons table"""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Name", "Key", "Type", "Difficulty"])
        
        # Make table read-only and select full rows
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Resize columns
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        # Connect double-click to open lesson
        table.doubleClicked.connect(self.open_lesson)

        # Connect selection change to update action buttons
        table.itemSelectionChanged.connect(self.on_selection_changed)

        return table

    def create_action_buttons(self):
        """Create the Open and Cancel button bar"""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setMaximumHeight(60)

        layout = QHBoxLayout(frame)

        # Add stretch to push buttons to the right
        layout.addStretch()

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_selection)
        layout.addWidget(self.cancel_button)

        # Open button
        self.open_button = QPushButton("Open")
        self.open_button.setEnabled(False)
        self.open_button.clicked.connect(self.open_lesson)
        layout.addWidget(self.open_button)

        layout.addSpacing(10)

        return frame

    def filter_by_category(self, category):
        """Filter lessons by category button"""
        # Update button states (mutual exclusivity)
        for btn in self.category_buttons:
            btn.setChecked(False)
            
        if category == "All":
            self.btn_all.setChecked(True)
        elif category == "Triad":
            self.btn_triads.setChecked(True)
        elif category == "Scale":
            self.btn_scales.setChecked(True)
            
        self.current_filter = category
        self.apply_filters()
        
    def reset_filters(self):
        """Reset all filters to 'All'"""
        # Reset category filter
        self.filter_by_category("All")
        
        # Reset dropdown filters
        self.key_filter.setCurrentText("All")
        self.type_filter.setCurrentText("All")
        self.difficulty_filter.setCurrentText("All")
        
    def apply_filters(self):
        """Apply all active filters and update the table"""
        filtered_lessons = self.all_lessons.copy()
        
        # Category filter
        if self.current_filter != "All":
            filtered_lessons = [l for l in filtered_lessons if l["type"] == self.current_filter]
            
        # Key filter
        if self.key_filter.currentText() != "All":
            filtered_lessons = [l for l in filtered_lessons if l["key"] == self.key_filter.currentText()]
            
        # Type filter
        if self.type_filter.currentText() != "All":
            filtered_lessons = [l for l in filtered_lessons if l["type"] == self.type_filter.currentText()]
            
        # Difficulty filter
        if self.difficulty_filter.currentText() != "All":
            filtered_lessons = [l for l in filtered_lessons if l["difficulty"] == self.difficulty_filter.currentText()]
            
        self.populate_table(filtered_lessons)
        
    def populate_table(self, lessons=None):
        """Populate the table with lessons"""
        if lessons is None:
            lessons = self.all_lessons
            
        self.table.setRowCount(len(lessons))
        
        for row, lesson in enumerate(lessons):
            self.table.setItem(row, 0, QTableWidgetItem(lesson["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(lesson["key"]))
            self.table.setItem(row, 2, QTableWidgetItem(lesson["type"]))
            self.table.setItem(row, 3, QTableWidgetItem(lesson["difficulty"]))
            
    def open_lesson(self):
        """Open the selected lesson"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            lesson_name = self.table.item(current_row, 0).text()

            # Find the full lesson data
            lesson_data = next((l for l in self.all_lessons if l["name"] == lesson_name), None)

            if lesson_data:
                # Store selected lesson
                self.selected_lesson = lesson_data

                # Emit signal with lesson data
                self.lessonSelected.emit(lesson_data)

                # Accept the dialog (closes with success)
                self.accept()

    def on_selection_changed(self):
        """Handle table selection changes to enable/disable action buttons"""
        has_selection = self.table.currentRow() >= 0
        self.open_button.setEnabled(has_selection)
        self.cancel_button.setEnabled(has_selection)

    def cancel_selection(self):
        """Cancel the dialog without selecting a lesson"""
        # Reject the dialog (closes with cancel)
        self.reject()


def main():
    """Standalone test for the lesson browser dialog"""
    app = QApplication(sys.argv)
    dialog = LessonBrowser()

    # Connect signal for testing
    dialog.lessonSelected.connect(
        lambda lesson: print(f"Selected: {lesson['name']} | {lesson['key']} | {lesson['type']} | {lesson['difficulty']}")
    )

    result = dialog.exec()
    if result == QDialog.Accepted:
        print(f"Dialog accepted with lesson: {dialog.selected_lesson}")
    else:
        print("Dialog cancelled")

    sys.exit(0)


if __name__ == "__main__":
    main()
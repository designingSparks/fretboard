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


class LessonBrowser(QDialog):
    """Dialog for browsing and selecting guitar lessons"""

    # Signal emitted when a lesson is selected (emits filename)
    lessonSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_lessons = []  # Will be populated via set_lessons()
        self.current_filter = "All"
        self.selected_filename = None  # Store selected lesson filename

        self.setWindowTitle("Guitar Lesson Browser")
        self.resize(900, 600)

        self.setup_ui()

    def set_lessons(self, lessons_metadata):
        """
        Set the lessons to display in the browser.

        Args:
            lessons_metadata: List of lesson metadata dicts from lesson_scanner.scan_lessons()
        """
        self.all_lessons = lessons_metadata
        self.populate_filter_options()
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
        self.key_filter.currentTextChanged.connect(self.apply_filters)
        layout.addWidget(self.key_filter)

        layout.addSpacing(20)

        # Type filter
        layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItem("All")
        self.type_filter.currentTextChanged.connect(self.apply_filters)
        layout.addWidget(self.type_filter)

        layout.addSpacing(20)

        # Difficulty filter (kept for future use, but not populated)
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

        # Hide difficulty column as requested
        table.setColumnHidden(3, True)

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

    def populate_filter_options(self):
        """Populate filter dropdowns with available options from lessons"""
        if not self.all_lessons:
            return

        # Populate Key filter
        keys = sorted(set(
            lesson["key"] for lesson in self.all_lessons
            if lesson["key"] is not None
        ))
        self.key_filter.clear()
        self.key_filter.addItem("All")
        self.key_filter.addItems(keys)

        # Populate Type filter
        types = sorted(set(
            lesson["type"] for lesson in self.all_lessons
            if lesson["type"] is not None
        ))
        self.type_filter.clear()
        self.type_filter.addItem("All")
        self.type_filter.addItems(types)

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
            filtered_lessons = [
                l for l in filtered_lessons
                if l.get("type") == self.current_filter
            ]

        # Key filter
        if self.key_filter.currentText() != "All":
            filtered_lessons = [
                l for l in filtered_lessons
                if l.get("key") == self.key_filter.currentText()
            ]

        # Type filter
        if self.type_filter.currentText() != "All":
            filtered_lessons = [
                l for l in filtered_lessons
                if l.get("type") == self.type_filter.currentText()
            ]

        # Difficulty filter
        if self.difficulty_filter.currentText() != "All":
            filtered_lessons = [
                l for l in filtered_lessons
                if l.get("difficulty") == self.difficulty_filter.currentText()
            ]

        self.populate_table(filtered_lessons)

    def populate_table(self, lessons=None):
        """Populate the table with lessons"""
        if lessons is None:
            lessons = self.all_lessons

        self.table.setRowCount(len(lessons))

        for row, lesson in enumerate(lessons):
            name_item = QTableWidgetItem(lesson.get("name", "Unknown"))
            key_item = QTableWidgetItem(lesson.get("key", ""))
            type_item = QTableWidgetItem(lesson.get("type", ""))
            difficulty_item = QTableWidgetItem(lesson.get("difficulty", ""))

            # Store filename in the name item's data for retrieval
            name_item.setData(Qt.UserRole, lesson.get("filename"))

            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, key_item)
            self.table.setItem(row, 2, type_item)
            self.table.setItem(row, 3, difficulty_item)

    def open_lesson(self):
        """Open the selected lesson"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            # Get filename from the stored data
            name_item = self.table.item(current_row, 0)
            filename = name_item.data(Qt.UserRole)

            if filename:
                # Store selected filename
                self.selected_filename = filename

                # Emit signal with filename
                self.lessonSelected.emit(filename)

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

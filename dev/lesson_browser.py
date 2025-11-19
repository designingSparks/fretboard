"""
Guitar Lesson Browser - PySide6 Application
A GUI for browsing and selecting guitar lessons with filtering and recent lessons tracking
"""

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QHeaderView, QMenu, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
import sys
from datetime import datetime


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


class LessonBrowser(QMainWindow):
    """Main window for browsing guitar lessons"""
    
    def __init__(self):
        super().__init__()
        self.all_lessons = LESSONS.copy()
        self.recent_lessons = []
        self.current_filter = "All"
        
        self.setWindowTitle("Guitar Lesson Browser")
        self.setMinimumSize(900, 600)
        
        self.setup_ui()
        self.populate_table()
        
    def setup_ui(self):
        """Initialize the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Toolbar
        self.create_toolbar()
        
        # Recent lessons section
        self.recent_widget = self.create_recent_lessons_widget()
        main_layout.addWidget(self.recent_widget)
        
        # Filters section
        filter_widget = self.create_filter_widget()
        main_layout.addWidget(filter_widget)
        
        # Table
        self.table = self.create_table()
        main_layout.addWidget(self.table)
        
    def create_toolbar(self):
        """Create the toolbar with category filter buttons"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Add spacing
        spacer = QWidget()
        spacer.setFixedWidth(10)
        toolbar.addWidget(spacer)
        
        # Category label
        label = QLabel("Category:")
        toolbar.addWidget(label)
        
        # Category buttons
        self.btn_all = QPushButton("All")
        self.btn_all.setCheckable(True)
        self.btn_all.setChecked(True)
        self.btn_all.clicked.connect(lambda: self.filter_by_category("All"))
        toolbar.addWidget(self.btn_all)
        
        self.btn_triads = QPushButton("Triads")
        self.btn_triads.setCheckable(True)
        self.btn_triads.clicked.connect(lambda: self.filter_by_category("Triad"))
        toolbar.addWidget(self.btn_triads)
        
        self.btn_scales = QPushButton("Scales")
        self.btn_scales.setCheckable(True)
        self.btn_scales.clicked.connect(lambda: self.filter_by_category("Scale"))
        toolbar.addWidget(self.btn_scales)
        
        # Group buttons for mutual exclusivity
        self.category_buttons = [self.btn_all, self.btn_triads, self.btn_scales]
        
        # Add stretch to push everything to the left
        toolbar.addWidget(QWidget())
        
    def create_recent_lessons_widget(self):
        """Create the recent lessons section"""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setMaximumHeight(60)
        
        layout = QHBoxLayout(frame)
        
        label = QLabel("Recent:")
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)
        
        self.recent_label = QLabel("No recent lessons")
        self.recent_label.setStyleSheet("color: gray;")
        layout.addWidget(self.recent_label)
        
        layout.addStretch()
        
        return frame
        
    def create_filter_widget(self):
        """Create the column filter dropdowns"""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setMaximumHeight(60)
        
        layout = QHBoxLayout(frame)
        
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
        
        return table
        
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
        """Open the selected lesson and add to recent lessons"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            lesson_name = self.table.item(current_row, 0).text()
            
            # Add to recent lessons (keep last 5)
            if lesson_name in self.recent_lessons:
                self.recent_lessons.remove(lesson_name)
            self.recent_lessons.insert(0, lesson_name)
            self.recent_lessons = self.recent_lessons[:5]
            
            self.update_recent_display()
            
            # In a real app, this would load the lesson
            print(f"Opening lesson: {lesson_name}")
            
    def update_recent_display(self):
        """Update the recent lessons display"""
        if self.recent_lessons:
            recent_text = " • ".join(self.recent_lessons[:3])
            if len(self.recent_lessons) > 3:
                recent_text += f" (+{len(self.recent_lessons) - 3} more)"
            self.recent_label.setText(recent_text)
            self.recent_label.setStyleSheet("color: black;")
        else:
            self.recent_label.setText("No recent lessons")
            self.recent_label.setStyleSheet("color: gray;")


def main():
    app = QApplication(sys.argv)
    window = LessonBrowser()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
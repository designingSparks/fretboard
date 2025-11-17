"""
Fretboard display component using QWebEngineView.
Handles all JavaScript communication and fretboard visualization.
"""

import os
import json
from PySide6.QtCore import QUrl, Signal, Slot
from PySide6.QtWebEngineWidgets import QWebEngineView
from constants import FRETBOARD_NOTES_NAME, STRING_ID


class FretboardView(QWebEngineView):
    """
    Custom QWebEngineView for displaying and interacting with the fretboard.
    Provides a clean API for highlighting notes and updating the display.
    """

    # Signal emitted when the web view has finished loading
    view_loaded = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Load the fretboard HTML
        html_path = os.path.abspath("fretboard.html")
        self.load(QUrl.fromLocalFile(html_path))
        self.setZoomFactor(0.9)

        # Connect internal signal
        self.loadFinished.connect(self._on_load_finished)

    @Slot()
    def _on_load_finished(self):
        """Called when the web view finishes loading."""
        print("Fretboard view loaded successfully")
        self.view_loaded.emit()

    def display_notes(self, notes_to_highlight, highlight_classes=None):
        """
        Display notes on the fretboard in an inactive state.

        Args:
            notes_to_highlight: List of (string_name, fret) tuples
            highlight_classes: Dict mapping note names to CSS highlight classes
                             e.g., {'C': 'highlight1', 'E': 'highlight2'}
        """
        if highlight_classes is None:
            highlight_classes = {}

        scale_data = []
        for s, f in notes_to_highlight:
            string_num = STRING_ID.index(s)
            note_name = FRETBOARD_NOTES_NAME[string_num][f]
            highlight_class = highlight_classes.get(note_name)
            scale_data.append({
                'stringName': s,
                'fret': f,
                'highlight': highlight_class
            })

        json_data = json.dumps(scale_data)
        self.page().runJavaScript(f"displayNotes('{json_data}');")

    def highlight_notes(self, notes):
        """
        Highlight specific notes on the fretboard (active state).

        Args:
            notes: List of (string_name, fret) tuples to highlight
        """
        notes_data = []
        for note in notes:
            if isinstance(note, tuple):
                notes_data.append({
                    'stringName': note[0],
                    'fret': note[1]
                })

        json_data = json.dumps(notes_data)
        js_code = f"highlightNotes('{json_data}');"
        self.page().runJavaScript(js_code)

    def clear_note_highlights(self):
        """
        Clear all active note highlights on the fretboard.
        """
        self.page().runJavaScript("clearNoteHighlights();")

    def set_title(self, title):
        """
        Set the title text on the fretboard.

        Args:
            title: String to display as the main title
        """
        # Escape single quotes in the title for JavaScript
        escaped_title = title.replace("'", "\\'")
        js_code = f"document.querySelector('.fretboard-title').textContent = '{escaped_title}';"
        self.page().runJavaScript(js_code)

    def set_subtitle(self, subtitle):
        """
        Set the subtitle text on the fretboard.

        Args:
            subtitle: String to display as the subtitle
        """
        # Escape single quotes in the subtitle for JavaScript
        escaped_subtitle = subtitle.replace("'", "\\'")
        js_code = f"document.querySelector('.fretboard-subtitle').textContent = '{escaped_subtitle}';"
        self.page().runJavaScript(js_code)

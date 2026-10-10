"""
Fretboard display component using QWebEngineView.
Handles all JavaScript communication and fretboard visualization.
"""

import os
import json
from PySide6.QtCore import QUrl, QUrlQuery, Signal, Slot
from PySide6.QtWebEngineWidgets import QWebEngineView
from models.background_layer import resolve_background_notes
from ui.note_display import (calculate_hidden_notes, prepare_background_notes,
                             prepare_hidden_notes, prepare_sequence_steps)


class FretboardView(QWebEngineView):
    """
    Custom QWebEngineView for displaying and interacting with the fretboard.
    Provides a clean API for highlighting notes and updating the display.
    """

    # Signal emitted when the web view has finished loading
    view_loaded = Signal()

    def __init__(self, parent=None, *, fret_count=24):
        super().__init__(parent)

        if isinstance(fret_count, bool) or not isinstance(fret_count, int) or not 1 <= fret_count <= 24:
            raise ValueError('fret_count must be an integer from 1 to 24')
        self.fret_count = fret_count

        # Load the fretboard HTML
        html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fretboard.html")
        url = QUrl.fromLocalFile(html_path)
        query = QUrlQuery()
        query.addQueryItem('frets', str(fret_count))
        url.setQuery(query)
        self.load(url)
        self.setZoomFactor(0.9)

        # Connect internal signal
        self.loadFinished.connect(self._on_load_finished)

    @Slot()
    def _on_load_finished(self):
        """Called when the web view finishes loading."""
        print("Fretboard view loaded successfully")
        self.view_loaded.emit()

    def display_notes(self, part, *, use_sharp=True, chord_label_title="Triad playing"):
        """Initialize all notes for a part in one browser update.

        Resolve first-layer-wins backgrounds, calculate playback-only positions,
        then prepare markers and sequence metadata. The browser creates visible
        backgrounds and hidden playback markers before selecting the first chord.
        Later playback updates activate existing markers without rebuilding them.
        """
        backgrounds = resolve_background_notes(part.background_notes, part.background_layers)
        hidden = calculate_hidden_notes(part.play_sequence, backgrounds)
        steps = prepare_sequence_steps(part.play_sequence, part.highlight_chord_root)
        data = {
            'backgroundNotes': prepare_background_notes(backgrounds, part.highlight_classes, use_sharp),
            'hiddenNotes': prepare_hidden_notes(hidden, part.highlight_classes, use_sharp),
            'sequenceSteps': steps,
            'sequenceGroups': [step['notes'] for step in steps if step['notes']]
                              if part.circle_sequence_elements else [],
            'wrappingDistance': part.wrapping_distance,
            'filletCorners': part.fillet_corners,
            'filletRadius': part.fillet_radius,
            'chordLabelTitle': chord_label_title,
        }
        self.page().runJavaScript(f"displayNotes({json.dumps(data)});")

    def highlight_sequence_step(self, index):
        """Select the same row's chord label and notes in one browser update."""
        self.page().runJavaScript(f"highlightSequenceStep({json.dumps(index)});")

    def set_playback_state(self, state):
        """Update chord inspection availability and reset/restore selection."""
        self.page().runJavaScript(f"setChordPlaybackState({json.dumps(state)});")

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

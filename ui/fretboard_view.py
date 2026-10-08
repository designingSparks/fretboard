"""
Fretboard display component using QWebEngineView.
Handles all JavaScript communication and fretboard visualization.
"""

import os
import json
import re
from PySide6.QtCore import QUrl, Signal, Slot
from PySide6.QtWebEngineWidgets import QWebEngineView
from constants import FRETBOARD_NOTES_SHARP, FRETBOARD_NOTES_FLAT, STRING_ID
from models.sequence_step import parse_sequence_row


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
        html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fretboard.html")
        self.load(QUrl.fromLocalFile(html_path))
        self.setZoomFactor(0.9)

        # Connect internal signal
        self.loadFinished.connect(self._on_load_finished)

    @Slot()
    def _on_load_finished(self):
        """Called when the web view finishes loading."""
        print("Fretboard view loaded successfully")
        self.view_loaded.emit()

    def display_notes(self, notes_to_highlight, highlight_classes=None, use_sharp=True,
                      play_sequence=None, circle_sequence_elements=False,
                      wrapping_distance=8.0, fillet_corners=False, fillet_radius=24.0,
                      chord_label_title="Triad playing", highlight_chord_root=False):
        """
        Display notes on the fretboard in an inactive state.

        Args:
            notes_to_highlight: List of (string_name, fret) tuples
            highlight_classes: Dict mapping note names to CSS highlight classes
                             e.g., {'C': 'highlight1', 'E': 'highlight2'}
            use_sharp: If True, use sharp notation (C#, D#). If False, use flat notation (Db, Eb)
            play_sequence: Rows of notes, an optional chord name, and a duration
            circle_sequence_elements: Draw a separate rounded outline for each row
            wrapping_distance: Gap outside note markers, in CSS pixels
            fillet_corners: Round the enclosing polygon's corners
            fillet_radius: Requested corner radius, in CSS pixels
            chord_label_title: Lesson-defined caption above the chord buttons
            highlight_chord_root: Color the current labelled chord's root with highlight1
        """
        if highlight_classes is None:
            highlight_classes = {}

        groups = []
        sequence_steps = []
        display_positions = list(dict.fromkeys(notes_to_highlight))
        for row in play_sequence or []:
            step = parse_sequence_row(row)
            positions = list(dict.fromkeys(step.notes))
            notes = [{'stringName': s, 'fret': f} for s, f in positions]
            if highlight_chord_root and step.chord_name:
                root = re.match(r'^[A-G][#b]?', step.chord_name.replace('♯', '#').replace('♭', 'b'))
                if root:
                    for note, (s, f) in zip(notes, positions):
                        string_num = STRING_ID.index(s)
                        note['isRoot'] = root.group() in (
                            FRETBOARD_NOTES_SHARP[string_num][f],
                            FRETBOARD_NOTES_FLAT[string_num][f],
                        )
            sequence_steps.append({'notes': notes, 'chordName': step.chord_name})
            if circle_sequence_elements and positions:
                groups.append(notes)
            for position in positions:
                if position not in display_positions:
                    display_positions.append(position)

        # Select the appropriate note mapping based on sharp/flat preference
        fretboard_notes = FRETBOARD_NOTES_SHARP if use_sharp else FRETBOARD_NOTES_FLAT

        scale_data = []
        for s, f in display_positions:
            string_num = STRING_ID.index(s)
            note_name = fretboard_notes[string_num][f]

            # Look up highlight class BEFORE converting to musical symbols
            highlight_class = highlight_classes.get(note_name)

            # Convert # and b to HTML musical symbols
            note_name = note_name.replace('#', '♯').replace('b', '♭')

            # Check specifically for flat symbol (needs tighter spacing)
            has_flat = '♭' in note_name
            scale_data.append({
                'stringName': s,
                'fret': f,
                'highlight': highlight_class,
                'noteName': note_name,
                'hasFlat': has_flat
            })

        # Send notes and groups together so a redraw never retains an old part's outlines.
        json_data = json.dumps(json.dumps(scale_data))
        groups_data = json.dumps(groups)
        self.page().runJavaScript(
            f"displayNotes({json_data}, {groups_data}, {json.dumps(wrapping_distance)}, "
            f"{json.dumps(fillet_corners)}, {json.dumps(fillet_radius)}, "
            f"{json.dumps(sequence_steps)}, {json.dumps(chord_label_title)});"
        )

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

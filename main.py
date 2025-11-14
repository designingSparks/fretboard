'''
Guitar fretboard learning application.
Coordinates audio playback and fretboard visualization.
'''

import os
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QApplication
from scales import C_MAJOR_POS4_HIGHLIGHT, C_MAJOR_POS4_PLAY
from ui.main_window import MainWindow
from ui.fretboard_view import FretboardView
from audio_engine import AudioEngine

# Configuration
NOTE_FOLDER = 'clean'
SAMPLERATE = 44100
STRUM_DELAY_MS = 10
HIGHLIGHTS = {'C':'highlight1'}  # , 'E':'highlight2', 'G':'highlight3'


class FretboardPlayer(QObject):
    """
    Coordinator between audio engine and fretboard view.
    Handles the connection between audio playback and visual feedback.
    """

    def __init__(self, fretboard_view, audio_engine, parent=None):
        super().__init__(parent)

        # Store references
        self.fretboard_view = fretboard_view
        self.audio_engine = audio_engine

        # Current sequence data
        self.notes_to_highlight = C_MAJOR_POS4_HIGHLIGHT
        self.play_seq = C_MAJOR_POS4_PLAY

        # Load the sequence into the audio engine
        self.audio_engine.load_sequence(self.play_seq)

        # Connect signals
        self.fretboard_view.view_loaded.connect(self.on_fretboard_loaded)
        self.audio_engine.highlight_note_index.connect(self.on_highlight_note_index)
        self.audio_engine.playback_stopped.connect(self.on_playback_stopped)

    @Slot(int)
    def on_highlight_note_index(self, index):
        """
        Handle highlight signal from audio engine.
        Updates the fretboard to highlight notes at the given index.

        Args:
            index: The play sequence index to highlight
        """
        if index >= len(self.play_seq):
            return

        notes_to_highlight = []
        for item in self.play_seq[index]:
            if isinstance(item, tuple):
                notes_to_highlight.append(item)

        self.fretboard_view.highlight_notes(notes_to_highlight)
        print(f"Highlighting notes for index {index}: {notes_to_highlight}")

    @Slot()
    def on_playback_stopped(self):
        """
        Handle playback stopped signal from audio engine.
        Clears highlights on the fretboard.
        """
        self.fretboard_view.clear_note_highlights()

    @Slot()
    def on_fretboard_loaded(self):
        """
        Called when the fretboard view has finished loading.
        Sends initial scale data to display on the fretboard.
        """
        print("Fretboard loaded. Sending scale data to fretboard.")
        self.fretboard_view.display_notes(self.notes_to_highlight, HIGHLIGHTS)


# --- Application entry point ---
if __name__ == "__main__":
    import sys
    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "8080"
    app = QApplication(sys.argv)

    # Create main window with toolbar
    main_window = MainWindow()

    # Create fretboard view
    fretboard_view = FretboardView()

    # Create audio engine
    audio_engine = AudioEngine(
        audio_folder=NOTE_FOLDER,
        samplerate=SAMPLERATE,
        strum_delay_ms=STRUM_DELAY_MS
    )

    # Create coordinator that connects audio and visuals
    player = FretboardPlayer(fretboard_view, audio_engine)

    # Set fretboard view as central widget
    main_window.set_central_content(fretboard_view)

    # Connect toolbar signals to audio engine
    main_window.play_clicked.connect(audio_engine.start_playback)
    main_window.stop_clicked.connect(audio_engine.stop_playback)

    # Connect audio engine signals to main window
    audio_engine.playback_stopped.connect(lambda: main_window.update_playback_state(False))

    # Show the main window
    main_window.show()

    sys.exit(app.exec())
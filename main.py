'''
Guitar fretboard learning application.
Coordinates audio playback and fretboard visualization.
'''

import os
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.fretboard_view import FretboardView
from audio_engine import AudioEngine

# Configuration
NOTE_FOLDER = 'clean'
SAMPLERATE = 44100
STRUM_DELAY_MS = 10


class FretboardPlayer(QObject):
    """
    Coordinator between audio engine and fretboard view.
    Handles the connection between audio playback and visual feedback.
    Manages lesson and part loading.
    """

    def __init__(self, fretboard_view, audio_engine, parent=None):
        super().__init__(parent)

        # Store references
        self.fretboard_view = fretboard_view
        self.audio_engine = audio_engine

        # Lesson/Part state
        self.current_lesson = None
        self.current_part_index = 0
        self._current_part = None

        # Connect signals
        self.fretboard_view.view_loaded.connect(self.on_fretboard_loaded)
        self.audio_engine.highlight_note_index.connect(self.on_highlight_note_index)
        self.audio_engine.playback_stopped.connect(self.on_playback_stopped)

    def load_lesson(self, lesson, part_index=0):
        """
        Load a lesson and display the specified part.

        Args:
            lesson: Lesson object to load
            part_index: Index of the part to start with (default: 0)
        """
        if not lesson or not lesson.parts:
            print("Error: Cannot load empty lesson")
            return

        if part_index < 0 or part_index >= len(lesson.parts):
            print(f"Error: Part index {part_index} out of range for lesson with {len(lesson.parts)} parts")
            return

        self.current_lesson = lesson
        self.current_part_index = part_index

        print(f"Loading lesson: {lesson.name}")
        print(f"  Parts: {lesson.get_part_count()}")
        print(f"  Starting with part {part_index+1}: {lesson.parts[part_index].name}")

        # Load the specified part
        self.load_part(lesson.parts[part_index])

    def load_part(self, part):
        """
        Load and display a single part.

        Args:
            part: Part object to load
        """
        if not part:
            print("Error: Cannot load None part")
            return

        self._current_part = part

        # Load audio sequence
        self.audio_engine.load_part(part)

        # Update fretboard display if it's already loaded
        if self.fretboard_view.isVisible():
            self.fretboard_view.display_notes(
                part.notes_to_highlight,
                part.highlight_classes
            )

        print(f"Loaded part: {part.name}")
        print(f"  Notes to highlight: {len(part.notes_to_highlight)}")
        print(f"  Play sequence steps: {part.get_note_count()}")
        print(f"  Duration: {part.get_duration_ms()}ms")

    @Slot(int)
    def on_highlight_note_index(self, index):
        """
        Handle highlight signal from audio engine.
        Updates the fretboard to highlight notes at the given index.

        Args:
            index: The play sequence index to highlight
        """
        if not self._current_part:
            return

        if index >= len(self._current_part.play_sequence):
            return

        notes_to_highlight = []
        for item in self._current_part.play_sequence[index]:
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
        Sends initial data to display on the fretboard.
        """
        print("Fretboard loaded.")
        if self._current_part:
            print(f"Displaying part: {self._current_part.name}")
            self.fretboard_view.display_notes(
                self._current_part.notes_to_highlight,
                self._current_part.highlight_classes
            )


# --- Application entry point ---
if __name__ == "__main__":
    import sys
    from models.lesson_loader import LessonLoader

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

    # Load default lesson
    loader = LessonLoader()
    print("\n" + "="*70)
    print("LOADING DEFAULT LESSON")
    print("="*70)

    default_lesson = loader.load_lesson("beginner_c_major")
    if default_lesson:
        player.load_lesson(default_lesson)
        print(f"✓ Successfully loaded: {default_lesson.name}")
    else:
        print("⚠️  Warning: Could not load default lesson")
        print("   The application will start but no lesson will be loaded.")
        print("   You can load a lesson later using File > Load Lesson")

    print("="*70 + "\n")

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
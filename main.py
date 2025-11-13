'''
Playback multiple notes using a QAudioSink.
Refactored to separate audio logic from UI.
'''

import os
import sys

from PySide6.QtCore import QObject, QTimer, Qt, Slot, Signal
from PySide6.QtWidgets import QApplication
from PySide6.QtMultimedia import QAudioSink, QAudioFormat, QMediaDevices
from scipy.io import wavfile
import numpy as np
from scales import C_MAJOR_POS4_HIGHLIGHT, C_MAJOR_POS4_PLAY
from triads import C_MAJOR_TRIAD_HIGHLIGHT
from triads import C_MAJOR_TRIAD_SEQ
from ui.main_window import MainWindow
from ui.fretboard_view import FretboardView

NOTE_FOLDER = 'clean'
SAMPLERATE = 44100
STRUM_DELAY_MS = 10
HIGHLIGHTS = {'C':'highlight1'} #, 'E':'highlight2', 'G':'highlight3'

class FretboardPlayer(QObject):
    """
    Audio engine for fretboard playback.
    Handles all audio processing, loading, mixing, and playback timing.
    """

    # Signal emitted when playback stops (either naturally or via stop button)
    playback_stopped = Signal()

    def __init__(self, fretboard_view, parent=None):
        super().__init__(parent)

        # Store reference to the fretboard view
        self.fretboard_view = fretboard_view

        self.audio_folder = NOTE_FOLDER

        self.notes_to_highlight = C_MAJOR_POS4_HIGHLIGHT
        self.play_seq = C_MAJOR_POS4_PLAY

        self.midi = None
        self.note_duration = None
        self.sound_list = None  # holds the numpy arrays of the sounds played at each step
        self.init_midi()
        self.create_sound_list()

        self.play_index = 0
        self.is_playing = False

        # --- Audio Playback Components ---
        self.audio_format = None
        self.audio_sink = None
        self.output_device = None
        self.push_timer = QTimer(self)
        self.push_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.push_timer.timeout.connect(self.push_audio_data)

        # Audio streaming state
        self.current_sample_position = 0
        self.sequence_start_time = 0  # Track when sequence started for timing calculations

        # Initialize audio system
        self.init_audio_system()

        # Connect to fretboard view loaded signal
        self.fretboard_view.view_loaded.connect(self.on_fretboard_loaded)

    def init_audio_system(self):
        """Initialize the QAudioSink with the correct audio format."""
        self.audio_format = QAudioFormat()
        self.audio_format.setSampleRate(SAMPLERATE)
        self.audio_format.setChannelCount(1)  # Mono
        self.audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)
        
        device_info = QMediaDevices.defaultAudioOutput()
        if not device_info.isFormatSupported(self.audio_format):
            print("Warning: Audio format not supported by default output device")
            return
        
        self.audio_sink = QAudioSink(device_info, self.audio_format)
        # Set buffer size to about 250ms for responsive playback
        buffer_duration_us = 250 * 1000
        buffer_size = self.audio_format.bytesForDuration(buffer_duration_us)
        self.audio_sink.setBufferSize(buffer_size)
        print("QAudioSink initialized successfully")

    @Slot()
    def start_playback(self):
        """Start audio playback."""
        if self.is_playing or not self.audio_sink:
            return

        print("Starting playback...")
        self.is_playing = True
        self.play_index = 0
        self.current_sample_position = 0

        # Start the audio sink
        self.output_device = self.audio_sink.start()
        print("Audio sink started")

        # Start timer to push audio data
        self.push_timer.start(50)  # Check every 50ms

    @Slot()
    def stop_playback(self):
        """Stop audio playback."""
        if not self.is_playing:
            return

        print("Stopping playback...")
        self.is_playing = False

        # Stop the timer and audio sink
        self.push_timer.stop()
        if self.audio_sink:
            self.audio_sink.stop()
            self.output_device = None

        self.play_index = 0
        self.current_sample_position = 0

        self.fretboard_view.clear_note_highlights()

        # Notify that playback has stopped
        self.playback_stopped.emit()

    @Slot()
    def push_audio_data(self):
        """
        Called by timer to push audio data to the sink's buffer.
        Also handles UI updates with latency compensation.
        """
        if not self.output_device or not self.is_playing:
            return
        
        # Check if we've finished all samples
        if self.play_index >= len(self.sound_list):
            # Wait for buffer to empty before stopping
            if self.audio_sink.bytesFree() == self.audio_sink.bufferSize():
                print("Playback finished.")
                self.stop_playback()
            return
        
        # Check how much space is available
        bytes_free = self.audio_sink.bytesFree()
        if bytes_free <= 0:
            return
        
        # --- Handle UI update for new sample with latency compensation ---
        if self.current_sample_position == 0:
            # Calculate dynamic latency based on buffer fullness
            bytes_in_buffer = self.audio_sink.bufferSize() - self.audio_sink.bytesFree()
            latency_us = self.audio_format.durationForBytes(bytes_in_buffer)
            latency_ms = latency_us / 1000.0
            
            # Schedule the UI update to sync with actual audio
            index = self.play_index
            QTimer.singleShot(int(latency_ms), lambda: self.update_highlights_for_index(index))
        
        # Get current buffer
        current_buffer = self.sound_list[self.play_index]
        bytes_remaining = len(current_buffer) - self.current_sample_position
        
        # Write as much as we can
        bytes_to_write = min(bytes_free, bytes_remaining)
        data_chunk = current_buffer[self.current_sample_position : self.current_sample_position + bytes_to_write]
        bytes_written = self.output_device.write(data_chunk)
        
        if bytes_written > 0:
            self.current_sample_position += bytes_written
        
        # Move to next sample if current one is finished
        if self.current_sample_position >= len(current_buffer):
            self.play_index += 1
            self.current_sample_position = 0

    def update_highlights_for_index(self, index):
        """
        Updates the fretboard highlights for the given play index.
        Called with latency compensation to sync with actual audio.
        """
        if not self.is_playing or index >= len(self.play_seq):
            return

        notes_to_highlight = []
        for item in self.play_seq[index]:
            if isinstance(item, tuple):
                notes_to_highlight.append(item)

        self.fretboard_view.highlight_notes(notes_to_highlight)
        print(f"Highlighting notes for index {index}: {notes_to_highlight}")

    @Slot()
    def on_fretboard_loaded(self):
        """
        Called when the fretboard view has finished loading.
        Sends initial scale data to display on the fretboard.
        """
        print("Fretboard loaded. Sending scale data to fretboard.")
        self.fretboard_view.display_notes(self.notes_to_highlight, HIGHLIGHTS)

    def init_midi(self):
        """
        Creates a list of MIDI notes and durations from the play sequence.
        """
        open_string_midi = {
            'E': 40, 'A': 45, 'D': 50, 'G': 55, 'B': 59, 'e': 64
        }

        self.midi = []
        self.note_duration = []

        for sublist in self.play_seq:
            pluck_list = [] 
            for item in sublist:
                if isinstance(item, tuple):
                    string_name, fret = item
                    if string_name in open_string_midi:
                        midi_note = open_string_midi[string_name] + fret
                        pluck_list.append(midi_note)
                elif isinstance(item, int):
                    self.note_duration.append(item)
            self.midi.append(pluck_list)

        print(f"Initialized MIDI notes: {self.midi}")

    def create_sound_list(self):
        '''
        Loads audio files, mixes them with strum delay, truncates to note_duration, and stores as byte arrays.
        '''
        self.sound_list = []

        for idx, item in enumerate(self.midi):
            note_data_list = []
            for note_id in item:
                data = self._load_audio_file(note_id)
                note_data_list.append(data)
            note_mix = self._mix_notes(note_data_list)
            
            # Truncate to the specified duration
            duration_ms = self.note_duration[idx]
            num_samples = int(SAMPLERATE * (duration_ms / 1000.0))
            truncated_mix = note_mix[:num_samples]
            
            # Convert to bytes for QAudioSink
            self.sound_list.append(truncated_mix.tobytes())

        print(f"Sound list created with {len(self.sound_list)} items.")

    def _load_audio_file(self, midi_note):
        """Loads a WAV file and returns the numpy array."""
        filename = f"clean_{midi_note}.wav"
        file_path = os.path.abspath(os.path.join(self.audio_folder, filename))
        try:
            samplerate, data = wavfile.read(file_path)
            return data
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return np.array([], dtype=np.int16)

    def _mix_notes(self, sound_data_list):
        """
        Mixes multiple notes with strumming delay.
        """
        delay_samples = int(SAMPLERATE * STRUM_DELAY_MS / 1000)
        strummed_arrays = []
        
        for i, data in enumerate(sound_data_list):
            initial_padding = np.zeros(i * delay_samples, dtype=data.dtype)
            strummed_arr = np.concatenate((initial_padding, data))
            strummed_arrays.append(strummed_arr)

        max_len = max(len(arr) for arr in strummed_arrays)
        padded_arrays = []
        for arr in strummed_arrays:
            padding = max_len - len(arr)
            padded_arr = np.pad(arr, (0, padding), 'constant')
            padded_arrays.append(padded_arr)

        mixed_arr = np.sum([arr.astype(np.float32) for arr in padded_arrays], axis=0)
        
        max_amp = np.max(np.abs(mixed_arr))
        if max_amp > 0:
            mixed_arr = mixed_arr / max_amp * 0.95

        mixed_arr_int16 = (mixed_arr * np.iinfo(np.int16).max).astype(np.int16)
        return mixed_arr_int16

# --- Application entry point ---
if __name__ == "__main__":
    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "8080"
    app = QApplication(sys.argv)

    # Create main window with toolbar
    main_window = MainWindow()

    # Create fretboard view
    fretboard_view = FretboardView()

    # Create audio engine with fretboard view reference
    player = FretboardPlayer(fretboard_view)

    # Set fretboard view as central widget
    main_window.set_central_content(fretboard_view)

    # Connect toolbar signals to player methods
    main_window.play_clicked.connect(player.start_playback)
    main_window.stop_clicked.connect(player.stop_playback)

    # Connect player signals to main window
    player.playback_stopped.connect(lambda: main_window.update_playback_state(False))

    # Show the main window
    main_window.show()

    sys.exit(app.exec())
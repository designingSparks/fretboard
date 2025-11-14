"""
Audio engine for guitar fretboard playback.
Handles all audio processing, loading, mixing, and playback timing.
"""

import os
import numpy as np
from PySide6.QtCore import QObject, QTimer, Qt, Slot, Signal
from PySide6.QtMultimedia import QAudioSink, QAudioFormat, QMediaDevices
import wavfile


class AudioEngine(QObject):
    """
    Manages all audio-related functionality for fretboard playback.
    Handles WAV file loading, mixing, QAudioSink management, and playback timing.
    """

    # Signals
    playback_stopped = Signal()  # Emitted when playback stops
    highlight_note_index = Signal(int)  # Emitted when a note index should be highlighted

    def __init__(self, audio_folder='clean', samplerate=44100, strum_delay_ms=10, parent=None):
        super().__init__(parent)

        # Configuration
        self.audio_folder = audio_folder
        self.samplerate = samplerate
        self.strum_delay_ms = strum_delay_ms

        # Playback state
        self.midi = None  # List of MIDI note lists for each step
        self.note_duration = None  # Duration in ms for each step
        self.sound_list = None  # Pre-mixed audio buffers as byte arrays
        self.play_index = 0
        self.is_playing = False
        self.current_sample_position = 0

        # Audio components
        self.audio_format = None
        self.audio_sink = None
        self.output_device = None

        # Timer for pushing audio data
        self.push_timer = QTimer(self)
        self.push_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.push_timer.timeout.connect(self.push_audio_data)

        # Initialize audio system
        self.init_audio_system()

    def init_audio_system(self):
        """Initialize the QAudioSink with the correct audio format."""
        self.audio_format = QAudioFormat()
        self.audio_format.setSampleRate(self.samplerate)
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

    def load_sequence(self, play_seq):
        """
        Load and prepare a playback sequence.

        Args:
            play_seq: List of note sequences, where each sequence contains
                     tuples of (string_name, fret) and an integer duration in ms
        """
        self.init_midi(play_seq)
        self.create_sound_list()

    def load_part(self, part):
        """
        Load and prepare a Part object for playback.

        Convenience method that extracts the play_sequence from a Part
        and calls load_sequence().

        Args:
            part: Part object from models.lesson_model

        Example:
            >>> from models.lesson_model import Part
            >>> part = Part(name="Scale", notes_to_highlight=[...], play_sequence=[...])
            >>> audio_engine.load_part(part)
        """
        self.load_sequence(part.play_sequence)
        print(f"Loaded part: {part.name}")

    def init_midi(self, play_seq):
        """
        Convert the play sequence into MIDI note numbers and durations.

        Args:
            play_seq: List of note sequences with (string, fret) tuples and durations
        """
        # MIDI note numbers for open strings from low E to high e
        open_string_midi = {
            'E': 40, 'A': 45, 'D': 50, 'G': 55, 'B': 59, 'e': 64
        }

        self.midi = []
        self.note_duration = []

        for sublist in play_seq:
            pluck_list = []
            for item in sublist:
                if isinstance(item, tuple):
                    string_name, fret = item
                    if string_name in open_string_midi:
                        midi_note = open_string_midi[string_name] + fret
                        pluck_list.append(midi_note)
                elif isinstance(item, int):  # Duration value
                    self.note_duration.append(item)
            self.midi.append(pluck_list)

        print(f"Initialized MIDI notes: {self.midi}")

    def create_sound_list(self):
        """
        Load audio files, mix them with strum delay, and prepare byte arrays for playback.
        """
        self.sound_list = []

        for idx, item in enumerate(self.midi):
            note_data_list = []
            for note_id in item:
                data = self._load_audio_file(note_id)
                note_data_list.append(data)
            note_mix = self._mix_notes(note_data_list)

            # Truncate to the specified duration
            duration_ms = self.note_duration[idx]
            num_samples = int(self.samplerate * (duration_ms / 1000.0))
            truncated_mix = note_mix[:num_samples]

            # Convert to bytes for QAudioSink
            self.sound_list.append(truncated_mix.tobytes())

        print(f"Sound list created with {len(self.sound_list)} items.")

    def _load_audio_file(self, midi_note):
        """
        Load a WAV file and return the numpy array.

        Args:
            midi_note: MIDI note number (used to construct filename)

        Returns:
            numpy array of audio samples (int16)
        """
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
        Mix multiple notes with strumming delay.

        Args:
            sound_data_list: List of numpy arrays containing audio samples

        Returns:
            numpy array of mixed audio samples (int16)
        """
        delay_samples = int(self.samplerate * self.strum_delay_ms / 1000)
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

    @Slot()
    def start_playback(self):
        """Start audio playback."""
        if self.is_playing or not self.audio_sink:
            return

        if not self.sound_list:
            print("Warning: No sound list loaded. Call load_sequence() first.")
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

        # Notify that playback has stopped
        self.playback_stopped.emit()

    @Slot()
    def push_audio_data(self):
        """
        Called by timer to push audio data to the sink's buffer.
        Also schedules UI updates with latency compensation.
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
            QTimer.singleShot(int(latency_ms), lambda: self._emit_highlight_signal(index))

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

    def _emit_highlight_signal(self, index):
        """
        Emit signal to highlight a note index.
        Called with latency compensation to sync with actual audio.

        Args:
            index: The play sequence index to highlight
        """
        if self.is_playing:
            self.highlight_note_index.emit(index)

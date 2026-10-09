"""
Audio engine for guitar fretboard playback.
Streams prepared audio and synchronizes playback progress with the UI.
"""

import os
from PySide6.QtCore import QObject, QTimer, Qt, Slot, Signal
from PySide6.QtMultimedia import QAudioSink, QAudioFormat, QMediaDevices
from audio_rendering import render_sequence


class AudioEngine(QObject):
    """
    Manages QAudioSink streaming, playback state, and progress timing.
    Sequence preparation is delegated to audio_rendering.
    """

    # Signals
    playback_stopped = Signal()  # Emitted when playback stops
    playback_started = Signal()
    highlight_note_index = Signal(int)  # Emitted when a note index should be highlighted

    def __init__(self, audio_folder='clean', samplerate=44100, strum_delay_ms=10, parent=None):
        super().__init__(parent)

        # Configuration — resolve relative to this file so the path is correct
        # regardless of the working directory the process was launched from.
        if not os.path.isabs(audio_folder):
            audio_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), audio_folder)
        self.audio_folder = audio_folder
        self.samplerate = samplerate
        self.strum_delay_ms = strum_delay_ms

        # Playback state
        self.sound_list = None  # Pre-mixed audio buffers as byte arrays
        self.play_index = 0
        self.is_playing = False
        self._playback_generation = 0
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
            play_seq: SequenceStep objects with named notes and duration_ms fields.
                      Legacy lists of note tuples followed by a duration are also accepted.
        """
        self.sound_list = render_sequence(
            play_seq, self.audio_folder, self.samplerate, self.strum_delay_ms
        )

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
        self._playback_generation += 1
        self.play_index = 0
        self.current_sample_position = 0

        # Start the audio sink
        self.output_device = self.audio_sink.start()
        print("Audio sink started")
        self.playback_started.emit()

        # Pre-fill the buffer to eliminate startup lag
        self.push_audio_data()

        # Start timer to push audio data
        self.push_timer.start(50)  # Check every 50ms

    @Slot()
    def stop_playback(self):
        """Stop audio playback."""
        if not self.is_playing:
            return

        print("Stopping playback...")
        self.is_playing = False
        self._playback_generation += 1

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
            generation = self._playback_generation
            QTimer.singleShot(int(latency_ms), lambda: self._emit_highlight_signal(index, generation))

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

    def _emit_highlight_signal(self, index, generation):
        """
        Emit signal to highlight a note index.
        Called with latency compensation to sync with actual audio.

        Args:
            index: The play sequence index to highlight
        """
        if self.is_playing and generation == self._playback_generation:
            self.highlight_note_index.emit(index)

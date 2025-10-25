import sys
import os
import io
from scipy.io import wavfile
import librosa  # Using librosa as requested

# --- PySide6 Imports ---
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
)
from PySide6.QtCore import QBuffer, QIODevice, Slot
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
# ---

class SingleSoundPlayer(QWidget):
    """
    A simple GUI to play and stop a single pre-loaded audio file
    from memory using QMediaPlayer and QBuffer.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Memory Sound Player")

        # --- Audio Data ---
        self.audio_bytes = None
        self.load_audio_file()

        # --- Qt Multimedia Setup ---
        self.player = QMediaPlayer()
        self.player.playbackStateChanged.connect(self.handle_state_changed)

        # These references are critical to prevent crashes.
        self._audio_output = None
        self.current_buffer = None

        # --- UI Setup ---
        self.init_ui()

    def load_audio_file(self):
        """Loads the target .wav file into an in-memory bytes object."""
        filename = os.path.abspath(os.path.join("clean", "clean_40.wav"))
        if not os.path.exists(filename):
            print(f"Error: File not found at '{filename}'")
            return

        print(f"Loading {filename} into memory...")
        try:
            # 1. Load with librosa into a numpy array (float)
            data, sample_rate = librosa.load(filename, sr=None)

            # 2. Create an in-memory byte buffer
            byte_io = io.BytesIO()

            # 3. Write the numpy array into the buffer in .wav format
            #    Note: librosa loads as float, so this creates a 32-bit float WAV
            wavfile.write(byte_io, sample_rate, data)

            # 4. Get the raw bytes of the complete .wav file
            self.audio_bytes = byte_io.getvalue()

        except Exception as e:
            print(f"Error reading audio file: {e}")

    def init_ui(self):
        """Sets up the user interface widgets and layout."""
        self.status_label = QLabel("Ready to play 'clean_40.wav'.")
        self.start_button = QPushButton("Start Playback")
        self.stop_button = QPushButton("Stop Playback")

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.start_button)
        main_layout.addWidget(self.stop_button)

        self.start_button.clicked.connect(self.start_playback)
        self.stop_button.clicked.connect(self.stop_playback)

        # Initial button states
        self.stop_button.setEnabled(False)
        if not self.audio_bytes:
            self.start_button.setEnabled(False)
            self.status_label.setText("Error: Audio file could not be loaded.")

    @Slot()
    def start_playback(self):
        """Plays the pre-loaded sound from memory."""
        if not self.audio_bytes:
            self.status_label.setText("Cannot play: Audio data not loaded.")
            return

        self.status_label.setText("Playing...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # Use the robust pattern to set the source and play
        self.player.stop()
        self._audio_output = QAudioOutput()
        self.player.setAudioOutput(self._audio_output)
        self.player.setSourceDevice(None)
        self.current_buffer = QBuffer()
        self.current_buffer.setData(self.audio_bytes)
        self.current_buffer.open(QIODevice.OpenModeFlag.ReadOnly)
        self.player.setSourceDevice(self.current_buffer)
        self.player.play()

    @Slot()
    def stop_playback(self):
        """Stops the currently playing sound."""
        self.player.stop()
        self.status_label.setText("Playback stopped.")

    @Slot(QMediaPlayer.PlaybackState)
    def handle_state_changed(self, state):
        """Resets button states when playback stops naturally."""
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            if "Playing" in self.status_label.text():
                self.status_label.setText("Playback finished.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SingleSoundPlayer()
    window.show()
    sys.exit(app.exec())
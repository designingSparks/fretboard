#This works well. It loads the .wav files into RAM to avoid IO latency. 
#With this approach, you can also preprocess bends etc.
import sys
import os
import io
from scipy.io import wavfile
import numpy as np
import librosa  # Using librosa as requested
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

LOAD_FORMAT = '.npy' #'.npy or .wav'
SAMPLERATE = 44100

class AudioSequencePlayer(QWidget):
    """
    A GUI to play a sequence of pre-loaded audio files from memory
    using a QTimer to control the interval.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Audio Sequencer")

        # --- State: Preload audio files into memory as bytes ---
        self.audio_data_list = []
        self.file_names = []
        self.current_index = 0
        self.preload_media()

        # --- Qt Multimedia Setup ---
        self.player = QMediaPlayer()

        # These references are critical to prevent crashes.
        self._audio_output = None
        self.current_buffer = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_next_sound)

        # --- UI Setup ---
        self.init_ui()

    # def load_audio_file(self):
    #     """Loads the target .wav file into an in-memory bytes object."""
    #     filename = os.path.abspath(os.path.join("clean", "clean_40.wav"))

    def preload_media(self):
        """Loads .wav files from clean_40 to clean_50 into memory."""
        base_dir = "clean"
        print("Preloading media...")
        for i in range(40, 51):  # 40 to 50 inclusive
            file_name = f"clean_{i}" + LOAD_FORMAT
            abs_path = os.path.abspath(os.path.join(base_dir, file_name))
            if not os.path.exists(abs_path):
                print(f"Warning: File not found, skipping: {abs_path}")
                continue

            try:
                # Using librosa as requested
                # data, sample_rate = librosa.load(abs_path, sr=None)

                if LOAD_FORMAT == '.wav':
                    samplerate, data = wavfile.read(abs_path)
                    byte_io = io.BytesIO()
                    wavfile.write(byte_io, samplerate, data)
                elif LOAD_FORMAT == '.npy':
                    data = np.load(abs_path)
                    # The .npy file is just raw audio data. We need to wrap it in a
                    # WAV format in-memory so QMediaPlayer can understand it.
                    byte_io = io.BytesIO()
                    wavfile.write(byte_io, SAMPLERATE, data)

                self.audio_data_list.append(byte_io.getvalue())
                self.file_names.append(file_name)
            except Exception as e:
                print(f"Error processing {abs_path}: {e}")
        print(f"Successfully loaded {len(self.audio_data_list)} audio files.")

    def play_current_sound(self):
        """Core logic for playing a sound from a bytes object."""
        if not (0 <= self.current_index < len(self.audio_data_list)):
            return

        data_bytes = self.audio_data_list[self.current_index]

        # --- The Robust Hot-Swap Pattern ---
        self.player.stop()
        self._audio_output = QAudioOutput() #You need to do this for each new sound
        self.player.setAudioOutput(self._audio_output)
        self.player.setSourceDevice(None)
        self.current_buffer = QBuffer()
        self.current_buffer.setData(data_bytes)
        self.current_buffer.open(QIODevice.OpenModeFlag.ReadOnly)
        self.player.setSourceDevice(self.current_buffer)
        self.player.play()
        self.status_label.setText(f"Playing: {self.file_names[self.current_index]}")

    @Slot()
    def stop_playback(self):
        """Stops the currently playing sound."""
        self.player.stop()
        self.status_label.setText("Playback stopped.")

    def init_ui(self):
        """Sets up the user interface widgets and layout."""
        self.status_label = QLabel("Click 'Start' to play the sequence.")
        self.start_button = QPushButton("Start Sequence")
        self.stop_button = QPushButton("Stop Sequence")

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.start_button)
        main_layout.addWidget(self.stop_button)

        self.start_button.clicked.connect(self.start_test)
        self.stop_button.clicked.connect(self.stop_playback)

        # Initial button states
        self.stop_button.setEnabled(False)
        if not self.audio_data_list:
            self.start_button.setEnabled(False)
            self.status_label.setText("Error: No audio files could be loaded.")

    @Slot()
    def start_test(self):
        """Starts the playback sequence."""
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.current_index = 0
        self.play_current_sound()
        self.timer.start(500)  # 500 ms interval

    @Slot()
    def stop_playback(self):
        """Stops the playback sequence."""
        self.timer.stop()
        self.player.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Sequence stopped.")
        self.current_index = 0

    @Slot()
    def play_next_sound(self):
        """Plays the next sound in the sequence, called by the QTimer."""
        self.current_index += 1
        if self.current_index >= len(self.audio_data_list):
            self.stop_playback()
            self.status_label.setText("Sequence complete.")
        else:
            print(f"Playing: {self.file_names[self.current_index]}")
            self.play_current_sound()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioSequencePlayer()
    window.show()
    sys.exit(app.exec())
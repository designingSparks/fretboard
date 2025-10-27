# There are .wav files in the ./clean directory. They are labelled clean_n.wav, where n is the midi note.Warning
# I want to play MIDI notes 60	64	67 simultaneously for 1 sec to form a C triad.
# Create a PySide6 GUI to play a C and G triad. There should be two buttons, Play C, Play G
import sys
import os
import numpy as np
from scipy.io import wavfile
import io
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QTimer, QUrl, QBuffer, QIODevice, Slot
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

CLEAN_DIR = 'clean'
SAMPLERATE = 44100
NOTE_DURATION_MS = 1000 # 1 second
STRUM_DELAY_MS = 10

class TriadPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Triad Player")

        self.c_triad_notes = [60, 64, 67] # C, E, G
        self.g_triad_notes = [67, 71, 74] # G, B, D (octave higher G)

        # We will store the raw numpy arrays, not the WAV bytes.
        self.audio_data = {}
        self.preload_audio_files()

        # We only need one player now
        self.player = QMediaPlayer()
        self._audio_output = None
        self.current_buffer = None

        self.init_ui()


    def preload_audio_files(self):
        """Loads necessary .wav files into memory as byte arrays."""
        print("Preloading audio files...")
        all_notes_needed = sorted(list(set(self.c_triad_notes + self.g_triad_notes)))

        for note_id in all_notes_needed:
            filename = f"clean_{note_id}.wav"
            filepath = os.path.join(CLEAN_DIR, filename)

            if not os.path.exists(filepath):
                print(f"Warning: Audio file not found for note {note_id}: {filepath}")
                continue

            try:
                samplerate, data = wavfile.read(filepath)
                if samplerate != SAMPLERATE:
                    print(f"Warning: Samplerate mismatch for {filename}. Expected {SAMPLERATE}, got {samplerate}.")

                self.audio_data[note_id] = data

            except Exception as e:
                print(f"Error processing {filename}: {e}")
        
        print(f"Finished preloading. {len(self.audio_data)} files loaded.")

    def init_ui(self):
        """Initializes the user interface."""
        layout = QVBoxLayout(self)
        self.status_label = QLabel("Ready to play triads.")
        self.play_c_button = QPushButton("Play C Triad (C-E-G)")
        self.play_g_button = QPushButton("Play G Triad (G-B-D)")
        self.stop_button = QPushButton("Stop")

        layout.addWidget(self.status_label)
        layout.addWidget(self.play_c_button)
        layout.addWidget(self.play_g_button)
        layout.addWidget(self.stop_button)

        self.play_c_button.clicked.connect(self.play_c_triad)
        self.play_g_button.clicked.connect(self.play_g_triad)
        self.stop_button.clicked.connect(self.stop_playback)

        # Initial button states
        if not self.audio_data:
            self.stop_button.setEnabled(False)
            self.status_label.setText("Error: No audio files were loaded. Buttons disabled.")
            self.play_c_button.setEnabled(False)
            self.play_g_button.setEnabled(False)

    def play_triad(self, notes_to_play):
        """
        Mixes a list of notes into a single buffer and plays it.
        """
        print(f"Mixing and playing notes: {notes_to_play}")

        # 1. Get the raw audio data for the notes in the triad
        note_arrays = [self.audio_data[nid] for nid in notes_to_play if nid in self.audio_data]
        if not note_arrays:
            print("No valid audio data for the selected triad.")
            return

        # 2. Implement strumming by adding a delay to the start of each note
        delay_samples = int(SAMPLERATE * STRUM_DELAY_MS / 1000)
        strummed_arrays = []
        for i, arr in enumerate(note_arrays):
            # The first note has no delay, the second has 1x delay, the third has 2x, etc.
            initial_padding = np.zeros(i * delay_samples, dtype=arr.dtype)
            strummed_arr = np.concatenate((initial_padding, arr))
            strummed_arrays.append(strummed_arr)

        # 3. Find the length of the longest strummed array and pad the others to match
        max_len = max(len(arr) for arr in strummed_arrays)
        padded_arrays = []
        for arr in strummed_arrays:
            padding = max_len - len(arr)
            padded_arr = np.pad(arr, (0, padding), 'constant')
            padded_arrays.append(padded_arr)

        # 4. Mix the arrays by summing them up (astype float to prevent overflow)
        mixed_arr = np.sum([arr.astype(np.float32) for arr in padded_arrays], axis=0)
        # 5. Normalize the mixed audio to prevent clipping
        max_amp = np.max(np.abs(mixed_arr))
        if max_amp > 0:
            # Normalize to 95% of max volume to be safe
            mixed_arr = mixed_arr / max_amp * 0.95

        # Convert back to int16 for WAV format
        mixed_arr_int16 = (mixed_arr * np.iinfo(np.int16).max).astype(np.int16)

        # 6. Convert the final numpy array to bytes in WAV format
        byte_io = io.BytesIO()
        wavfile.write(byte_io, SAMPLERATE, mixed_arr_int16)
        data_bytes = byte_io.getvalue()

        # 7. Play the single mixed buffer using the robust pattern
        self.player.stop()
        self._audio_output = QAudioOutput()
        self.player.setAudioOutput(self._audio_output)
        self.player.setSourceDevice(None)
        self.current_buffer = QBuffer()
        self.current_buffer.setData(data_bytes)
        self.current_buffer.open(QIODevice.OpenModeFlag.ReadOnly)
        self.player.setSourceDevice(self.current_buffer)
        self.player.play()

        self.stop_button.setEnabled(True)
        self.status_label.setText(f"Playing notes: {notes_to_play}")

    @Slot()
    def play_c_triad(self):
        """Slot to play the C major triad."""
        self.play_triad(self.c_triad_notes)

    @Slot()
    def play_g_triad(self):
        """Slot to play the G major triad."""
        self.play_triad(self.g_triad_notes)

    @Slot()
    def stop_playback(self):
        """Stops the currently playing sound."""
        self.player.stop()
        self.stop_button.setEnabled(False)
        self.status_label.setText("Playback stopped.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TriadPlayer()
    window.show()
    sys.exit(app.exec())
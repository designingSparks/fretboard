# ref: https://stackoverflow.com/questions/56086862/how-to-play-a-simulated-signal-continuously-with-qaudiooutput
import sys
import os
import wavfile
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget
)
from PySide6.QtCore import QTimer, Slot, QIODevice, Qt
from PySide6.QtMultimedia import QAudioSink, QAudioFormat, QMediaDevices
# import numpy as np

# --- Configuration ---
TONE_MS = 500  # The length of each note in milliseconds

class LowLevelAudioPlayer(QWidget):
    """
    A widget that plays a sequence of pre-loaded WAV files using the low-level QAudioSink.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QAudioSink Sequencer")

        # --- Audio Data ---
        self.audio_buffers = []  # List to hold individual raw audio data as byte arrays
        self.current_sample_index = 0 # Index of the sample we are playing from audio_buffers
        self.current_sample_position = 0 # Position within the current sample's byte array
        self.file_names = []
        self.audio_format = None

        # --- Audio Playback Components ---
        self.audio_sink = None
        self.output_device = None  # The QIODevice we write to

        # --- Playback State ---
        self.push_timer = QTimer(self)
        self.push_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.push_timer.timeout.connect(self.push_audio_data)

        # --- UI ---
        self.list_widget = QListWidget() # Must be created before preload_audio
        self.init_ui()

        # --- Preload Audio ---
        self.preload_audio()

        # --- Initialize Audio System ---
        if self.audio_buffers:
            self.init_audio_system()
        else:
            self.status_label.setText("Error: No audio files loaded. Playback disabled.")
            self.start_button.setEnabled(False)
            
    def preload_audio(self):
        """
        Loads WAV files (clean_40.wav to clean_50.wav) into memory as raw byte buffers.
        It also determines the audio format from the first successfully loaded file.
        """
        base_dir = "clean"
        print("Preloading audio files...")
        for i in range(40, 51):
            file_name = f"clean_{i}.wav"
            abs_path = os.path.abspath(os.path.join(base_dir, file_name))
            if not os.path.exists(abs_path):
                print(f"Warning: File not found, skipping: {abs_path}")
                continue

            try:
                samplerate, data = wavfile.read(abs_path)

                # If this is the first file, set up the QAudioFormat
                if self.audio_format is None:
                    self.audio_format = QAudioFormat()
                    self.audio_format.setSampleRate(samplerate)
                    # Assuming mono based on context, wavfile.read would give a 2D array for stereo
                    self.audio_format.setChannelCount(1 if data.ndim == 1 else data.shape[1])
                    # Assuming standard 16-bit PCM from wavfile
                    self.audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)
                    self.audio_format.setCodec("audio/pcm")
                    print(f"Audio format detected: {samplerate}Hz, {self.audio_format.channelCount()} channels, 16-bit PCM")

                # --- Truncate the audio data to 500ms ---
                num_samples = int(samplerate * (TONE_MS / 1000.0))
                truncated_data = data[:num_samples]

                # Add a short silence (e.g., 250ms) between clips for separation
                # silence_samples = int(samplerate * 0.25)
                # silence = np.zeros(silence_samples, dtype=np.int16)
                
                # Convert numpy array to raw bytes and store it with silence
                # buffer_with_silence = np.concatenate((truncated_data, silence)).tobytes()
                # self.audio_buffers.append(buffer_with_silence)

                self.audio_buffers.append(truncated_data.tobytes())
                self.file_names.append(file_name)
                self.list_widget.addItem(file_name)

            except Exception as e:
                print(f"Error processing {abs_path}: {e}")
        print(f"Successfully loaded {len(self.audio_buffers)} audio files.")

    def init_audio_system(self):
        """
        Initializes the QAudioSink with the format detected from the loaded files.
        """
        device_info = QMediaDevices.defaultAudioOutput()
        if not device_info.isFormatSupported(self.audio_format):
            print("Default output device does not support the audio format.")
            self.status_label.setText("Error: Audio format not supported by output device.")
            self.start_button.setEnabled(False)
            return

        self.audio_sink = QAudioSink(device_info, self.audio_format)
        # Calculate a buffer size that is responsive but safe from underruns.
        # 40% of the tone duration is a good starting point.
        buffer_duration_us = (TONE_MS * 0.4) * 1000
        buffer_size = self.audio_format.bytesForDuration(int(buffer_duration_us))
        self.audio_sink.setBufferSize(buffer_size)
        print("QAudioSink initialized.")

    def init_ui(self):
        """Sets up the user interface."""
        self.status_label = QLabel("Click 'Start' to play the sequence.")
        self.start_button = QPushButton("Start Sequence")
        self.stop_button = QPushButton("Stop Sequence")

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        main_layout.addLayout(button_layout)

        self.start_button.clicked.connect(self.start_playback)
        self.stop_button.clicked.connect(self.stop_playback)

        self.stop_button.setEnabled(False)

    @Slot()
    def start_playback(self):
        """Starts the playback sequence."""
        if not self.audio_sink:
            return

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.current_sample_index = 0
        self.current_sample_position = 0

        # Start the sink, which returns the QIODevice for writing.
        self.output_device = self.audio_sink.start()
        print("Audio sink started. Output device is ready.")

        # Start a high-frequency timer to push data to the audio buffer
        self.push_timer.start(10) # Check every 10ms

    @Slot()
    def stop_playback(self):
        """Stops the playback sequence."""
        self.push_timer.stop()
        if self.audio_sink:
            self.audio_sink.stop()
            self.output_device = None

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Sequence stopped.")
        self.current_sample_index = 0
        self.current_sample_position = 0
        self.list_widget.setCurrentRow(-1)
        print("Audio sink stopped.")

    @Slot()
    def push_audio_data(self):
        """
        Called by a timer to push data into the audio sink's buffer.
        This creates a continuous stream.
        """
        # Stop if we have no device or have played all samples
        if not self.output_device or self.current_sample_index >= len(self.audio_buffers):
            # Check if the internal buffer is empty before stopping, to avoid cutting off the last sound
            if self.audio_sink and self.audio_sink.bytesFree() == self.audio_sink.bufferSize():
                if self.current_sample_index >= len(self.audio_buffers):
                    self.status_label.setText("Sequence complete.")
                self.stop_playback()
            return

        # Check how much space is available in the device's buffer
        bytes_free = self.audio_sink.bytesFree()
        if bytes_free <= 0:
            return

        # --- This is the moment we know a new sample is starting ---
        if self.current_sample_position == 0:
            # Dynamically calculate the latency based on how much data is currently in the buffer.
            # This ensures the UI update syncs with the audible sound.
            bytes_in_buffer = self.audio_sink.bufferSize() - self.audio_sink.bytesFree()
            latency_us = self.audio_format.durationForBytes(bytes_in_buffer)
            latency_compensation_ms = latency_us / 1000.0
            
            print(f"Dynamic latency compensation: {latency_compensation_ms:.2f} ms")
            QTimer.singleShot(latency_compensation_ms, lambda index=self.current_sample_index: self.update_ui_for_sample(index))

        current_buffer = self.audio_buffers[self.current_sample_index]
        bytes_remaining_in_sample = len(current_buffer) - self.current_sample_position

        # Determine how much data to write in this chunk
        bytes_to_write = min(bytes_free, bytes_remaining_in_sample)

        # Get the chunk and write it to the audio device
        data_chunk = current_buffer[self.current_sample_position : self.current_sample_position + bytes_to_write]
        bytes_written = self.output_device.write(data_chunk)

        if bytes_written > 0:
            self.current_sample_position += bytes_written

        # If we've finished writing the current sample, move to the next one
        if self.current_sample_position >= len(current_buffer):
            self.current_sample_index += 1
            self.current_sample_position = 0

    def update_ui_for_sample(self, index):
        """
        Updates the UI to reflect the currently playing sample.
        This is called by a delayed QTimer to compensate for audio latency.
        """
        if index < len(self.file_names):
            current_file = self.file_names[index]
            print(f"--- UI Update for sample: {current_file} ---")
            self.status_label.setText(f"Playing: {current_file}")
            self.list_widget.setCurrentRow(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LowLevelAudioPlayer()
    window.show()
    sys.exit(app.exec())

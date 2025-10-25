import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel
)
from PySide6.QtCore import QTimer, QUrl, Slot
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

class AudioHotSwapTester(QWidget):
    """
    A simple PySide6 application to test the "hot-swap" latency of
    QMediaPlayer by rapidly changing sounds using a QTimer.
    """
    def __init__(self):
        super().__init__()
        
        # --- State ---
        self.media_url_list = []
        self.file_names = []
        self.current_index = 0
        
        # --- Media Components ---
        # The player itself
        self.player = QMediaPlayer()
        # You MUST hold a reference to the QAudioOutput, or it will be
        # garbage-collected and no sound will play.
        self._audio_output = QAudioOutput()
        self.player.setAudioOutput(self._audio_output)
        
        # The timer for swapping sounds
        self.timer = QTimer(self)

        # --- Init ---
        self.preload_media() # Find and load media files first
        self.init_ui()       # Setup the GUI
        
    def preload_media(self):
        """Finds and preloads media files into QMediaContent objects."""
        base_dir = "clean"
        
        # Note: 40 to 50 inclusive is 11 files.
        # If you meant 10 files, change 51 to 50.
        print("Preloading media...")
        for i in range(40, 51): 
            file_name = f"clean_{i}.wav"
            file_path = os.path.join(base_dir, file_name)
            
            # QUrl requires an absolute path to work reliably
            abs_path = os.path.abspath(file_path)
            
            if os.path.exists(abs_path):
                url = QUrl.fromLocalFile(abs_path)
                self.media_url_list.append(url)
                self.file_names.append(file_name)
            else:
                print(f"Warning: File not found, skipping: {abs_path}")
        
        print(f"Successfully loaded {len(self.media_url_list)} audio files.")

    def init_ui(self):
        """Initializes the User Interface widgets and layout."""
        self.setWindowTitle("Audio Hot-Swap Latency Tester")
        
        # --- Widgets ---
        self.status_label = QLabel("Click 'Start' to begin test.")
        self.status_label.setWordWrap(True)
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")

        # --- Layout ---
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.status_label)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        main_layout.addLayout(button_layout)
        
        # --- Connections ---
        self.start_button.clicked.connect(self.start_test)
        self.stop_button.clicked.connect(self.stop_test)
        self.timer.timeout.connect(self.play_next_sound)

        # --- Initial State ---
        self.stop_button.setEnabled(False)
        
        # If no files were loaded, disable the start button
        if not self.media_url_list:
            self.start_button.setEnabled(False)
            self.status_label.setText(
                "Error: No .wav files found in './clean' directory. "
                "(Expected clean_40.wav to clean_50.wav)"
            )
        
        self.resize(350, 120)

    def play_current_sound(self):
        """
        Stops the player, sets the new media from the current index,
        and starts playing. This is the core "hot-swap" action.
        """
        if 0 <= self.current_index < len(self.media_url_list):
            url = self.media_url_list[self.current_index]
            file_name = self.file_names[self.current_index]
            
            # --- The "Hot-Swap" ---
            # 1. Stop any currently playing sound
            self.player.stop()             
            # 2. Load the new sound
            self.player.setSource(url)  
            # 3. Play the new sound
            self.player.play()             
            # ---
            
            # Update the label
            self.status_label.setText(f"Playing: {file_name}")

    @Slot()
    def start_test(self):
        """Slot for the 'Start' button. Begins the test cycle."""
        if not self.media_url_list:
            return
        
        print("Starting test...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # Start from the first sound
        self.current_index = 0
        self.play_current_sound() # Play the first sound immediately
        
        # Start the timer to trigger the next sounds
        self.timer.start(500) # 500 msec interval

    @Slot()
    def stop_test(self):
        """Slot for the 'Stop' button. Halts the test cycle."""
        print("Stopping test...")
        self.timer.stop()
        self.player.stop()
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Test stopped. Click 'Start' to begin.")
        self.current_index = 0

    @Slot()
    def play_next_sound(self):
        """Slot for the timer's timeout. Plays the next sound in the list."""
        # The timer ticked, so increment the index to play the *next* sound
        self.current_index += 1
        
        # Check if we've played all sounds
        if self.current_index >= len(self.media_url_list):
            print("Test complete.")
            self.stop_test() # We're done, stop everything
            self.status_label.setText("Test complete. All sounds played.")
            return
            
        # If not done, play the sound at the new index
        self.play_current_sound()

if __name__ == "__main__":
    # Ensure the 'clean' directory exists before starting
    if not os.path.isdir("clean"):
        print("Error: The './clean' directory was not found.")
        print("Please create it and place your .wav files inside.")
        # We can still run the app; it will show the error in the GUI.

    app = QApplication(sys.argv)
    window = AudioHotSwapTester()
    window.show()
    sys.exit(app.exec())
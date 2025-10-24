# Demo function for using QMediaPlayer to playback some of the notes in ./notes, using the QTimer.

import os
import json
from PySide6.QtCore import Slot, QTimer, QUrl
# from PySide6.QtSoundEffects import QSoundEffect
from PySide6.QtMultimedia import QSoundEffect

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

from scales import C_MAJOR

NOTE_FOLDER = 'clean'

class FretboardPlayer(QWidget):
    def __init__(self):
        super().__init__()
        
        self.audio_folder = NOTE_FOLDER
        self.scale = C_MAJOR #TODO: Allow scale to be selectable in the GUI
        self.init_midi()
        self.init_sound()

        self.play_index = 0
        self.is_playing = False

        
        # --- GUI Setup ---
        self.web_view = QWebEngineView()
        self.web_view.load(QUrl.fromLocalFile(os.path.abspath("fretboard.html")))
        
        self.play_button = QPushButton("Play")
        self.stop_button = QPushButton("Stop")

        layout = QVBoxLayout(self)
        layout.addWidget(self.web_view)
        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)
        
        # --- Connections ---
        self.play_button.clicked.connect(self.start_playback)
        self.stop_button.clicked.connect(self.stop_playback)
        self.web_view.loadFinished.connect(self.on_load_finished)

    @Slot()
    def start_playback(self):
        if self.is_playing:
            return
            
        print("Starting playback...")
        self.is_playing = True
        self.play_index = 0
        self.play_next_note() # Start the chain

    @Slot()
    def stop_playback(self):
        if not self.is_playing:
            return
            
        print("Stopping playback...")
        self.is_playing = False
        # Stop any sound that might be playing from the list
        for sound in self.sound_list:
            sound.stop()
        # Clear the note display on the web page
        # self.clear_fretboard_highlight()

    def play_next_note(self):
        # Stop condition: flag is false or playlist is finished
        if not self.is_playing or self.play_index >= len(self.midi):
            self.stop_playback() # Clean up
            print("Playback finished.")
            return

        # 1. Get current note details
        note_id = self.midi[self.play_index]
        duration_ms = self.note_duration[self.play_index]
        # note_name = self.note_names[self.play_index]
        string = self.scale[self.play_index][0]
        fret = self.scale[self.play_index][1]
        note_name = f"{string}{fret}" #debug only
        
        print(f"Playing: {note_name} (MIDI: {note_id}) for {duration_ms}ms")

        # 2. Play the sound
        self.play_audio()
        
        # 3. Update the web page display
        self.highlight_note(string, fret)

        # 4. Advance the play_index
        self.play_index += 1
        
        # 5. Schedule the *next* call
        QTimer.singleShot(duration_ms, self.play_next_note)

    def play_audio(self):
        """Plays the sound effect corresponding to the current playback play_index."""
        if 0 <= self.play_index < len(self.sound_list):
            sound_to_play = self.sound_list[self.play_index]
            sound_to_play.play()


    def init_fretboard(self):
        '''
        Initialize the fretboard with the notes in a greyed out state.
        '''
        pass
        


    def highlight_note(self, string, fret):
        # This function runs JavaScript on your HTML page.
        # Calls the setPlayingNote function in playback_view.html
        js_code = f"highlightNote('{string}', {fret});"
        self.web_view.page().runJavaScript(js_code)

    #TO DELETE
    # def clear_fretboard_highlight(self):
    #     # Calls the clearDisplay function in playback_view.html
    #     self.web_view.page().runJavaScript("clearDisplay();")


    @Slot()
    def on_load_finished(self):
        """
        Called when the QWebEngineView has finished loading the HTML.
        This is the perfect time to send initial data to the JavaScript side.
        """
        print("Web view finished loading. Sending scale data to fretboard.")
        self.send_scale_to_fretboard()


    def send_scale_to_fretboard(self):
        """
        Called automatically once the webview has loaded.
        Converts the Python scale pattern to a JSON string and sends it to
        a JavaScript function in the web view.
        """
        # Convert the list of tuples into a list of dictionaries for easier JSON conversion.
        # Using camelCase for keys is a common convention when passing data to JavaScript.
        scale_data = [
            {'stringName': s, 'fret': f, 'duration': d} for s, f, d in self.scale
        ]
        json_data = json.dumps(scale_data)
        self.web_view.page().runJavaScript(f"loadScalePattern('{json_data}');")


    def init_midi(self):
        """
        Initializes self.midi and self.note_duration lists from self.scale.
        Converts (string, fret) tuples into MIDI note numbers.
        """
        # MIDI note numbers for open strings from low E to high e
        open_string_midi = {
            'E': 40, 'A': 45, 'D': 50, 'G': 55, 'B': 59, 'e': 64
        }

        self.midi = []
        self.note_duration = []
        self.note_names = [] #for debugging only


        for string_name, fret, duration in self.scale:
            if string_name in open_string_midi:
                midi_note = open_string_midi[string_name] + fret
                self.midi.append(midi_note)
                self.note_duration.append(duration)
                self.note_names.append(string_name+str(fret)) #why do we need this??
            else:
                print(f"Warning: Unknown string name '{string_name}' in scale. Skipping.")
        print(f"Initialized MIDI notes: {self.midi}")


    def init_sound(self):
        '''
        Pre-loads all audio files for the scale into a list of QSoundEffect
        objects. This ensures minimal latency when a note needs to be played.
        '''
        self.sound_list = list()
        for note_id in self.midi:
            sound_effect = QSoundEffect()
            filename = f"clean_{note_id}.wav"
            file_path = os.path.abspath(os.path.join(self.audio_folder, filename))
            # TODO: Check if file_path exists and handle error if not.
            sound_effect.setSource(QUrl.fromLocalFile(file_path))
            self.sound_list.append(sound_effect)



# --- To run the application (example) ---
if __name__ == "__main__":
    import sys
    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "8080"

    app = QApplication(sys.argv)

    window = FretboardPlayer()

    window.show()
    sys.exit(app.exec())
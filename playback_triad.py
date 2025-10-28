# Demo function for using QMediaPlayer to playback some of the notes in ./notes, using the QTimer.

import os
import json
from PySide6.QtCore import Slot, QTimer, QUrl
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from triads import C_MAJOR_TRIAD_HIGHLIGHT #This will be highlighted in grey by default
from triads import C_MAJOR_TRIAD_SEQ #These are the notes that are played
from scipy.io import wavfile
import io
import numpy as np


NOTE_FOLDER = 'clean'
SAMPLERATE = 44100
STRUM_DELAY_MS = 10

class FretboardPlayer(QWidget):
    def __init__(self):
        super().__init__()
        
        self.audio_folder = NOTE_FOLDER
        self.notes_to_highlight = C_MAJOR_TRIAD_HIGHLIGHT #TODO: Allow scale to be selectable in the GUI
        self.play_seq = C_MAJOR_TRIAD_SEQ

        self.midi = None
        self.note_duration = None
        self.sound_list = None
        self.init_midi() #e.g. self.midi = [[64, 60, 55], [67, 64, 60], [72, 67, 64], [76, 72, 67]]
        self.create_sound_list()

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
        # Clear any note highlights
        self.clear_note_highlights()

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
        string = self.play_seq[self.play_index][0]
        fret = self.play_seq[self.play_index][1]
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



    def clear_note_highlights(self):
        '''
        Called when play is manually stopped or has come to an end.
        '''
        # Calls the clearDisplay function in playback_view.html
        self.web_view.page().runJavaScript("clearNoteHighlights();")


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
        Highlights the potential notes in grey. Called automatically once the webview has loaded.
        Note all these notes are necessarily played
        Converts the Python scale pattern to a JSON string and sends it to
        a JavaScript function in the web view.
        """
        # Convert the list of tuples into a list of dictionaries for easier JSON conversion.
        # Using camelCase for keys is a common convention when passing data to JavaScript.
        scale_data = [
            {'stringName': s, 'fret': f} for s, f in self.notes_to_highlight
        ]
        json_data = json.dumps(scale_data)
        self.web_view.page().runJavaScript(f"loadScalePattern('{json_data}');")


    def init_midi(self):
        """
        From self.play_seq, creates a list of all midi notes, self.midi, that will be played in the sequence.
        This is necessary to know which audio files to preload into memory, since the files
        have the midi note in their filename.
        Also saves the note duration.
        """
        # MIDI note numbers for open strings from low E to high e
        open_string_midi = {
            'E': 40, 'A': 45, 'D': 50, 'G': 55, 'B': 59, 'e': 64
        }

        self.midi = []
        self.note_duration = []

        #Cycle through each sublist in C_MAJOR_TRIAD_SEQ
        for sublist in self.play_seq:
            pluck_list = [] 
            for item in sublist:
                if isinstance(item, tuple):
                    string_name, fret = item
                    if string_name in open_string_midi:
                        midi_note = open_string_midi[string_name] + fret
                        pluck_list.append(midi_note)
                    # self.midi.extend(pluck_list)
                elif isinstance(item, int):  #TON value
                    self.note_duration.append(item)
            self.midi.append(pluck_list)

        print(f"Initialized MIDI notes: {self.midi}")


    def create_sound_list(self):
        '''
        Cycles through each item in the sequence. An item may be one or more notes.
        Items are stored in self.midi
        Loads the correct .wav files first.
        Then converts them into numpy arrays.
        Finally if there are more than one notes in the item, it 'mixes' them, applying a strum delay.
        '''
        self.sound_list = list() #list of numpy arrays?

        for item in self.midi:
            note_data_list = []
            for note_id in item:
                data = self._load_audio_file(note_id)
                note_data_list.append(data)
            note_mix = self._mix_notes(note_data_list)
            self.sound_list.append(note_mix)
    

    def _load_audio_file(self, midi_note):
        """Loads the target .wav file into an in-memory bytes object."""
        filename = f"clean_{midi_note}.wav"
        file_path = os.path.abspath(os.path.join(self.audio_folder, filename))
        try:
            samplerate, data = wavfile.read(file_path)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
        return data

    
    def _mix_notes(self, sound_data_list):
        """
        Pre-mixes a triad into a single numpy array and stores it.
        This is an optimization to avoid mixing every time a triad is played.
        """

        # Create strumming effect
        delay_samples = int(SAMPLERATE * STRUM_DELAY_MS / 1000)
        strummed_arrays = []
        for data in sound_data_list):
            initial_padding = np.zeros(data * delay_samples, dtype=arr.dtype)
            strummed_arr = np.concatenate((initial_padding, arr))
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

        # Convert back to int16 for WAV format
        mixed_arr_int16 = (mixed_arr * np.iinfo(np.int16).max).astype(np.int16)
        return mixed_arr_int16
    

# --- To run the application (example) ---
if __name__ == "__main__":
    import sys
    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "8080"
    app = QApplication(sys.argv)
    window = FretboardPlayer()
    window.show()
    sys.exit(app.exec())
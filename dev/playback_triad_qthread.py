'''
For reference only.
It shows how a QMediaPlayer can be run in a separate QThread.
This approach is defunct, as I no longer need to use a QMediaPlayer.
'''


import os
import json
from PySide6.QtCore import *
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import *
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from scipy.io import wavfile
import io
import numpy as np
from triads import C_MAJOR_TRIAD_HIGHLIGHT #This will be highlighted in grey by default
from triads import C_MAJOR_TRIAD_SEQ #These are the notes that are played
from constants import FRETBOARD_NOTES_NAME, STRING_ID
from scales import C_MAJOR_POS4_HIGHLIGHT, C_MAJOR_POS4_PLAY, C_MAJOR_POS5_HIGHLIGHT, C_MAJOR_POS5_PLAY



NOTE_FOLDER = 'clean'
SAMPLERATE = 44100
STRUM_DELAY_MS = 10
HIGHLIGHTS = {'C':'highlight1'} #, 'E':'highlight2', 'G':'highlight3'


class AudioPlayerWorker(QObject):
    """
    A QObject worker that handles audio playback in a separate thread.
    It owns the QMediaPlayer instance.
    """
    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self.player.setAudioOutput(self._audio_output)
        self.current_buffer = None

    @Slot(bytes)
    def play_sound(self, data_bytes):
        """
        Plays a sound from a byte array. This slot will be executed in the worker thread.
        """
        self.player.stop()
        self.current_buffer = QBuffer()
        self.current_buffer.setData(data_bytes)
        self.current_buffer.open(QIODevice.OpenModeFlag.ReadOnly)
        self.player.setSourceDevice(self.current_buffer)
        self.player.play()

    @Slot()
    def stop_sound(self):
        """Stops playback. This slot will be executed in the worker thread."""
        self.player.stop()

    @Slot()
    def prime_audio(self):
        """Plays a short silent clip to warm up the audio backend."""
        silent_samples = np.zeros(int(SAMPLERATE * 0.01), dtype=np.int16)
        byte_io = io.BytesIO()
        wavfile.write(byte_io, SAMPLERATE, silent_samples)
        self.play_sound(byte_io.getvalue())
        # Immediately stop it, we just need to initialize the pipeline
        QTimer.singleShot(10, self.stop_sound)
        

class FretboardPlayer(QWidget):
    # Define signals as class attributes
    play_sound_signal = Signal(bytes)
    prime_audio_signal = Signal() # New signal for priming
    stop_sound_signal = Signal()

    def __init__(self):
        super().__init__()
        
        self.audio_folder = NOTE_FOLDER

        
        # self.notes_to_highlight = C_MAJOR_TRIAD_HIGHLIGHT
        # self.play_seq = C_MAJOR_TRIAD_SEQ

        self.notes_to_highlight = C_MAJOR_POS4_HIGHLIGHT
        self.play_seq = C_MAJOR_POS4_PLAY

        self.midi = None #e.g. self.midi = [[64, 60, 55], [67, 64, 60], [72, 67, 64], [76, 72, 67]]
        self.note_duration = None
        self.sound_list = None #holds the numpy arrays of the sounds played at each step of the sequence
        self.init_midi() 
        self.create_sound_list()

        self.play_index = 0
        self.is_playing = False

        self.web_view = QWebEngineView()
        self.web_view.load(QUrl.fromLocalFile(os.path.abspath("fretboard.html")))
        self.web_view.setZoomFactor(0.9) # Set zoom factor
        
        self.play_button = QPushButton("Play")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        #Don't need to disable the play button as the prime sound only plays for 10ms

        layout = QVBoxLayout(self)
        layout.addWidget(self.web_view)
        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)
        
        # --- Connections ---
        self.play_button.clicked.connect(self.start_playback)
        self.stop_button.clicked.connect(self.stop_playback)
        self.web_view.loadFinished.connect(self.on_load_finished)

        # --- Threading Setup for Audio ---
        self.audio_thread = QThread()
        self.audio_worker = AudioPlayerWorker()
        self.audio_worker.moveToThread(self.audio_thread)

        # Connect signals from the main thread to slots in the worker thread
        self.play_sound_signal.connect(self.audio_worker.play_sound)
        self.stop_sound_signal.connect(self.audio_worker.stop_sound)

        # Connect the new priming signal
        self.prime_audio_signal.connect(self.audio_worker.prime_audio)
        self.audio_thread.start() # Start the worker thread
        self.prime_audio_signal.emit() # Trigger priming in the worker thread

        # --- Playback Timer ---
        # Use a persistent QTimer for the playback sequence
        self.playback_timer = QTimer(self)
        self.playback_timer.timeout.connect(self.play_next_note)

    def closeEvent(self, event):
        self.audio_thread.quit()
        self.audio_thread.wait()
        super().closeEvent(event)

    @Slot()
    def start_playback(self):
        if self.is_playing:
            return
            
        print("Starting playback...")
        self.stop_button.setEnabled(True) # Enable stop button when playback starts
        self.play_button.setEnabled(False)
        self.is_playing = True
        self.play_index = 0
        self.play_next_note() # Play the first note immediately and start the timer chain

    @Slot()
    def stop_playback(self):
        if not self.is_playing:
            return
            
        print("Stopping playback...")
        self.is_playing = False

        self.playback_timer.stop() # Stop the timer
        # Stop the QMediaPlayer instance that is playing the sound
        self.stop_sound_signal.emit()
        self.stop_button.setEnabled(False)
        self.play_button.setEnabled(True)

        self.clear_note_highlights()


    def play_next_note(self):
        # Stop condition: flag is false or playlist is finished
        if not self.is_playing or self.play_index >= len(self.sound_list):
            self.stop_playback() # Clean up
            print("Playback finished.")
            return

        # Create a list of tuples to be send to fretboard.js        
        notes_to_highlight = []
        for item in self.play_seq[self.play_index]:
            notes_to_highlight.append(item)
        self.highlight_notes(notes_to_highlight)

        # --- Play Sound ---
        data_bytes = self.sound_list[self.play_index]
        self.play_sound_signal.emit(data_bytes) #TODO: Check if this makes a difference on slower platforms
        
        # --- Schedule the *next* note ---
        duration_ms = self.note_duration[self.play_index]
        self.play_index += 1
        self.playback_timer.start(duration_ms)


    def highlight_notes(self, notes):
        '''
        Calls highlightNotes() in main.js with the list of notes to be highlighted in the current step.
        '''
        # Convert the list of tuples into a list of dictionaries for easier JSON conversion.
        notes_data = []
        for note in notes:
            if isinstance(note, tuple): #Don't want to process note duration
                notes_data.append({'stringName': note[0], 'fret': note[1]})

        json_data = json.dumps(notes_data)
        js_code = f"highlightNotes('{json_data}');" #highlights multiple notes
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
        self.send_notes_to_fretboard()


    def send_notes_to_fretboard(self):
        """
        Called automatically once the webview has loaded.
        Basically preloads the notes, which are then displayed in an inactive CSS class.
        The notes also belong to either the default, highlight1,2,3 CSS classes.
        Not all notes send must be played. But a note must 
        Converts the Python scale pattern to a JSON string and sends it to a JavaScript function in the web view.
        """
        scale_data = []
        for s, f in self.notes_to_highlight:
            string_num = STRING_ID.index(s)
            note_name = FRETBOARD_NOTES_NAME[string_num][f]
            # Use .get() to safely get the highlight class.
            # If note_name is not in HIGHLIGHTS, it will return None.
            highlight_class = HIGHLIGHTS.get(note_name)
            scale_data.append({'stringName': s, 'fret': f, 'highlight': highlight_class})
        json_data = json.dumps(scale_data)
        self.web_view.page().runJavaScript(f"displayNotes('{json_data}');")


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
            note_mix = self._mix_notes(note_data_list) #numpy array
            
            byte_io = io.BytesIO()
            wavfile.write(byte_io, SAMPLERATE, note_mix)
            data_bytes = byte_io.getvalue()
            self.sound_list.append(data_bytes)

        print("Sound list created.")

    def _load_audio_file(self, midi_note):
        """Loads the target .wav file into an in-memory bytes object."""
        filename = f"clean_{midi_note}.wav"
        file_path = os.path.abspath(os.path.join(self.audio_folder, filename))
        try:
            samplerate, data = wavfile.read(file_path) #data is a numpy array
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

        # Convert back to int16 for WAV format
        mixed_arr_int16 = (mixed_arr * np.iinfo(np.int16).max).astype(np.int16)
        return mixed_arr_int16
    
    def closeEvent(self, event):
        """Ensure the audio thread is properly shut down when the window closes."""
        self.audio_thread.quit()
        self.audio_thread.wait()
        super().closeEvent(event)


if __name__ == "__main__":
    import sys
    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "8080" #for debugging in the browser
    app = QApplication(sys.argv)
    window = FretboardPlayer()
    window.show()
    sys.exit(app.exec())
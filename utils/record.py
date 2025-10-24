# Note that you need to use pitch shifting to get notes above 80.

# A fretboard is defined by a fretnumber from 0 to 24, with 0 being the nut, and string number from 
# 1 to 6, with 1 being the top e string and 6 the bottom (low) E string.
# This file cycles through each note on the fretboard and creates a dictionary that stores the 
# midi note for each fret of each string. It also contains utilities to play MIDI sequences.
import sys
import sounddevice as sd
from scipy.io.wavfile import write as write_wav
import numpy as np
import mido
import time

# Constants
# MIDI_PORT_NAME = 'IAC Driver Bus 1' # macOS default
MIDI_PORT_NAME = 'IAC Driver midi bus__'
MIDI_PORT_NAME = 'Kontakt 8 Virtual Input'

# Audio recording constants
SAMPLE_RATE = 44100  # Standard CD-quality audio
# RECORDING_CHANNELS = 2 # Stereo
RECORDING_CHANNELS = 1 # Mono
INPUT_DEVICE = 'BlackHole 2ch' # The name of your virtual audio driver

NOTE_DURATION_S = 0.4 # How long each note plays in seconds
NUM_FRETS = 24
NUM_STRINGS = 6
TUNING = ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']
MIDI_OFFSET = 12 #accounts for the Kontakt VST offset

def generate_fretboard_midi_data(num_frets, tuning):
    """
    Generates MIDI note data for each fret on each string of a fretboard.

    Args:
        num_frets (int): The total number of frets on the fretboard (including the nut as fret 0).
        tuning (list): A list of MIDI note names for the open strings, from low E to high e.

    Returns:
        dict: A dictionary mapping string numbers to a list of MIDI notes for each fret.
              {string_num: [midi_fret_0, midi_fret_1, ...]}
    """

    # MIDI note numbers for common notes (C4 = 60)
    midi_notes_map = {
        'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
        'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
    }

    def note_to_midi(note_name):
        """Converts a note name (e.g., 'A4', 'G#3') to its MIDI note number."""
        # Extract pitch class (e.g., 'E', 'A', 'D', 'G', 'B')
        pitch_class_str = note_name.rstrip('0123456789')
        # Extract octave (e.g., '2', '3', '4')
        octave_str = note_name[len(pitch_class_str):]
        octave = int(octave_str)

        midi_val = midi_notes_map[pitch_class_str]
        midi_val += (octave + 1) * 12 # C-1 is MIDI 0, C0 is MIDI 12, etc.
        return midi_val

    fret_midi_notes = {}

    # The tuning array is ordered from low E to high e.
    # We need to map this to string numbers 1 (high e) to 6 (low E).
    # tuning_index 0 (E2) -> string_num 6
    # tuning_index 5 (E4) -> string_num 1
    for tuning_index, open_note_name in enumerate(tuning):
        string_num = NUM_STRINGS - tuning_index # Map 0-indexed tuning to 1-6 string numbers

        fret_midi_notes[string_num] = []

        open_midi_note = note_to_midi(open_note_name)

        for fret in range(num_frets + 1): # Include fret 0 (open string) up to num_frets
            current_midi_note = open_midi_note + fret #+ MIDI_OFFSET
            
            fret_midi_notes[string_num].append(current_midi_note)
            
    return fret_midi_notes

#TO DELETE. Not needed
# def get_note_locations(fret_midi_notes): # This function is commented out and not used.
#     """
#     Inverts the fret_midi_notes dictionary to map MIDI notes to their locations.

#     Args:
#         fret_midi_notes (dict): The dictionary from generate_fretboard_data.
#                                 {string_num: [midi_fret_0, midi_fret_1, ...]}

#     Returns:
#         dict: A dictionary mapping each MIDI note to a list of its possible locations.
#               {midi_note_number: [(string_num, fret_num), ...]}
#     """
#     note_locations = {}
#     for string_num, midi_notes_on_string in fret_midi_notes.items():
#         for fret_num, midi_note in enumerate(midi_notes_on_string):
#             if midi_note not in note_locations:
#                 note_locations[midi_note] = []
#             note_locations[midi_note].append((string_num, fret_num))
#     return note_locations

def play_midi_sequence(midi_notes_to_play, port_name=MIDI_PORT_NAME, note_duration=NOTE_DURATION_S, prime=False):
    """
    Plays a sequence of MIDI notes through a specified MIDI output port.

    Args:
        midi_notes_to_play (list): A list of MIDI note numbers to play.
        port_name (str): The name of the virtual MIDI output port to use.
        note_duration (float): The duration to hold each note in seconds.
    """
    try:
        # Open the virtual MIDI port for output.
        # Mido will raise a PortNotOpenError if the port is not found.
        with mido.open_output(port_name) as outport:
            print(f"Successfully opened MIDI port: '{port_name}'")
            print(f"Playing sequence: {midi_notes_to_play}")

            # --- Priming the VST with a dummy note ---
            # VSTs often need to receive a MIDI message to fully initialize or load samples.
            # Sending a very short, low-velocity note ensures the VST is active before
            # the actual sequence begins, preventing silent initial notes.
            if prime:
                primer_note = 60 # C4, a common middle note
                primer_velocity = 1 # Very low velocity, almost silent
                primer_duration = 0.05 # Very short duration
                outport.send(mido.Message('note_on', note=primer_note, velocity=primer_velocity))
                time.sleep(primer_duration)
                outport.send(mido.Message('note_off', note=primer_note, velocity=0))
                time.sleep(1) # Give the VST a moment to process the primer
                print("VST primed with a dummy note.")
                
            print(f"Playing sequence: {midi_notes_to_play}")
            # time.sleep(2) #give it time to open, doesn't help

            for note in midi_notes_to_play:
                # A MIDI message is created with 'note_on', channel, note, and velocity (64 is medium)
                msg_on = mido.Message('note_on', note=note, velocity=80)
                outport.send(msg_on)
                print(f"  Note On: {note}")

                # Wait for the duration of the note
                time.sleep(note_duration)

                # Send the 'note_off' message to stop the note
                msg_off = mido.Message('note_off', note=note, velocity=0)
                outport.send(msg_off)
                print(f"  Note Off: {note}")

    except IOError as e:
        print(f"Error: Could not open MIDI port '{port_name}'.")
        print("Please ensure your virtual MIDI driver (e.g., IAC Driver on macOS, loopMIDI on Windows) is running and the port name is correct.")
        print(f"Available ports are: {mido.get_output_names()}")

def _find_audio_device_index(device_name):
    """Helper to find the index of an audio device by name."""
    try:
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device_name in device['name'] and device['max_input_channels'] > 0:
                return i
        return None
    except Exception as e:
        print(f"Error querying audio devices: {e}")
        return None

def _preflight_checks():
    """Check for MIDI and Audio devices before starting."""
    if MIDI_PORT_NAME not in mido.get_output_names():
        print(f"Error: MIDI port '{MIDI_PORT_NAME}' not found. Available ports: {mido.get_output_names()}", file=sys.stderr)
        return False
    if _find_audio_device_index(INPUT_DEVICE) is None:
        print(f"Error: Audio input device '{INPUT_DEVICE}' not found. Available devices:\n{sd.query_devices()}", file=sys.stderr)
        return False
    return True

def play_and_record(midi_note, duration, saveas='wav', filename='output'):
    """
    Plays a single MIDI note and records the resulting audio output.

    This function sends a MIDI note, records audio from a specified input device
    (like BlackHole) for the note's duration, and then saves the recording.

    Args:
        midi_note (int): The MIDI note number to play.
        duration (float): The duration in seconds to play and record.
        saveas (str): The format to save the recording. 'wav' or 'numpy'.
        filename (str): The base filename for the saved file (without extension).

    Returns:
        numpy.ndarray or None: The recorded audio as a NumPy array if saveas is 'numpy',
                               otherwise None.
    """
    # print(f"Recording note {midi_note} for {duration}s...")
    try:
        input_device_index = _find_audio_device_index(INPUT_DEVICE)
        if input_device_index is None:
            raise ValueError(f"Audio input device '{INPUT_DEVICE}' not found.")

        # Set the default input device and sample rate for sounddevice
        sd.default.device[0] = input_device_index
        sd.default.samplerate = SAMPLE_RATE

        # Add a small buffer to the recording duration to capture the note's tail
        recording_buffer = 0.1
        total_record_time = duration + recording_buffer

        # Start recording in the background. `sd.rec` is non-blocking.
        recording = sd.rec(int(total_record_time * SAMPLE_RATE), channels=RECORDING_CHANNELS)
        
        # IMPORTANT: Wait a moment for the recording to initialize before playing the note
        # This prevents the note's attack from being cut off.
        time.sleep(0.05)

        # Play the MIDI note
        with mido.open_output(MIDI_PORT_NAME) as outport:
            outport.send(mido.Message('note_on', note=midi_note, velocity=90))
            time.sleep(duration)
            outport.send(mido.Message('note_off', note=midi_note, velocity=0))
            # The rest of the recording time is handled by sd.wait()

        # `sd.wait()` will block until the recording initiated by `sd.rec` is finished.
        sd.wait()

        if np.max(np.abs(recording)) < 0.001:
            print(f"  -> Warning: Recording for note {midi_note} is silent.")

        if saveas == 'wav':
            output_filename = f"{filename}.wav"
            # The recording is float, convert to 16-bit integer for standard WAV
            int_recording = np.int16(recording * 32767)
            write_wav(output_filename, SAMPLE_RATE, int_recording)
            print(f"Audio successfully saved to '{output_filename}'")
            return None
        elif saveas == 'numpy':
            return recording
        else:
            print(f"Warning: Unknown saveas format '{saveas}'. Recording not saved.")
            return recording

    except Exception as e:
        print(f"An error occurred during play/record for note {midi_note}: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if not _preflight_checks():
        sys.exit("Exiting due to configuration errors.")

    fret_midi_notes = generate_fretboard_midi_data(NUM_FRETS, TUNING)
    # The MIDI_OFFSET is now applied within generate_fretboard_midi_data, so this line is removed.
    # pprint(fret_midi_notes) # This prints the full dictionary, which can be long.

    # --- Create a sorted list of unique notes from the fretboard ---
    # 1. Flatten the list of lists from the dictionary's values into a single list.
    all_notes_on_fretboard = [note for string_notes in fret_midi_notes.values() for note in string_notes]

    # 2. Use a set to get only the unique notes, then convert back to a list and sort it.
    notes_to_record = sorted(list(set(all_notes_on_fretboard)))

    print("--- Unique MIDI Notes on Fretboard (Sorted) ---")
    print(notes_to_record)
    print(f"Found {len(notes_to_record)} unique notes.")

    # --- Priming Step ---
    print("\n--- Priming audio system ---")
    time.sleep(1) # Give the system a second to settle after priming.

    # Test to check the interface
    # play_midi_sequence(notes_to_record[:12], note_duration=0.5)

    # --- Batch Recording Loop ---
    print("\n--- Starting batch recording ---")
    # INTER_NOTE_DELAY_S = 1 # A short delay between each recording
    for midi_note in notes_to_record:
        fname = f"note_{midi_note}"
        play_and_record(midi_note + MIDI_OFFSET, duration=1.2, saveas='wav', filename=fname)
        # time.sleep(0.1)

    print("\nBatch recording complete.")
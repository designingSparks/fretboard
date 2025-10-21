# A fretboard is defined by a fretnumber from 0 to 24, with 0 being the nut, and string number from 
# 1 to 6, with 1 being the top e string and 6 the bottom (low) E string.
# This file cycles through each note on the fretboard and creates a dictionary that stores the 
# frequency of each fret of each string. It also creates a dictionary that stores the midi note for
# each fret of each string.
from pprint import pprint

# Constants
NUM_FRETS = 24
NUM_STRINGS = 6
TUNING = ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']


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
            current_midi_note = open_midi_note + fret
            
            fret_midi_notes[string_num].append(current_midi_note)
            
    return fret_midi_notes

#TO DELETE. Not needed
# def get_note_locations(fret_midi_notes):
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

if __name__ == "__main__":
    fret_midi_notes = generate_fretboard_midi_data(NUM_FRETS, TUNING)
    pprint(fret_midi_notes)
    # note_locations = get_note_locations(fret_midi_notes)

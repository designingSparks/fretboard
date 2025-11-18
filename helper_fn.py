from constants import FRETBOARD_NOTES_SHARP, FRETBOARD_NOTES_FLAT
from scales import C_MAJOR_POS4_HIGHLIGHT


def scale_to_note(scale, use_sharp=True):
    '''
    Helper function that converts a scale (list of string/fret tuples) to a nested list of note names.
    The outer list is 0-indexed for strings (e.g., index 0 is the high 'e' string).

    Args:
        scale: List of (string_name, fret_number) tuples
        use_sharp: If True, use sharp notation (C#, D#). If False, use flat notation (Db, Eb)
    '''
    # Select the appropriate note mapping based on sharp/flat preference
    fretboard_notes = FRETBOARD_NOTES_SHARP if use_sharp else FRETBOARD_NOTES_FLAT

    # Initialize a list of 6 empty lists for the 6 strings.
    notes = [[] for _ in range(6)]
    for string_name, fret_number in scale:
        # Map string name to its 0-based index.
        string_map = {'e': 0, 'B': 1, 'G': 2, 'D': 3, 'A': 4, 'E': 5}
        string_index = string_map.get(string_name) # Returns None if string_name is not in map

        if string_index is not None and 0 <= fret_number < len(fretboard_notes[string_index]):
            note_name = fretboard_notes[string_index][fret_number]
            notes[string_index].append(note_name)
        else:
            print(f"Warning: Invalid string name '{string_name}' or fret number '{fret_number}'. Skipping.")
    return notes


if __name__ == "__main__":
    from pprint import pprint
    from helper_fn import scale_to_note
    scale = C_MAJOR_POS4_HIGHLIGHT
    notes = scale_to_note(scale)
    pprint(notes)
from constants import FRETBOARD_NOTES_NAME
from scales import C_MAJOR_POS4_HIGHLIGHT


def scale_to_note(scale):
    '''
    Helper function that converts a scale (list of string/fret tuples) to a nested list of note names.
    The outer list is 0-indexed for strings (e.g., index 0 is the high 'e' string).
    '''
    # Initialize a list of 6 empty lists for the 6 strings.
    notes = [[] for _ in range(6)]
    for string_name, fret_number in scale:
        # Map string name to its 0-based index.
        string_map = {'e': 0, 'B': 1, 'G': 2, 'D': 3, 'A': 4, 'E': 5}
        string_index = string_map.get(string_name) # Returns None if string_name is not in map

        if string_index is not None and 0 <= fret_number < len(FRETBOARD_NOTES_NAME[string_index]):
            note_name = FRETBOARD_NOTES_NAME[string_index][fret_number]
            notes[string_index].append(note_name)
        else:
            print(f"Warning: Invalid string name '{string_name}' or fret number '{fret_number}'. Skipping.")
    return notes


if __name__ == "__main__":
    from constants import FRETBOARD_NOTES_NAME
    from pprint import pprint
    from helper_fn import scale_to_note
    scale = C_MAJOR_POS4_HIGHLIGHT
    notes = scale_to_note(scale)
    pprint(notes)
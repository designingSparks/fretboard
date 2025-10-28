#Default play time for the note
T_NOTE = 500

#This is the scale that will be played
C_MAJOR_POS4_HIGHLIGHT = [
    ('e', 3),('e', 5), # High e string
    ('B', 3),('B', 5),('B', 6),
    ('G', 2),('G', 4),('G', 5),
    ('D', 2),('D', 3),('D', 5),
    ('A', 2),('A', 3),('A', 5),
    ('E', 3), ('E', 5), # Low E string
]


C_MAJOR_POS4_PLAY = [
    # Low E string
    # ('E', 3, T_NOTE),
    # ('E', 5, T_NOTE),
    # A string
    # ('A', 2, T_NOTE),
    ('A', 3, T_NOTE),
    ('A', 5, T_NOTE),
    # D string
    ('D', 2, T_NOTE),
    ('D', 3, T_NOTE),
    ('D', 5, T_NOTE),
    # G string
    ('G', 2, T_NOTE),
    ('G', 4, T_NOTE),
    ('G', 5, T_NOTE),
    # B string
    # ('B', 3, T_NOTE),
    # ('B', 5, T_NOTE),
    # ('B', 6, T_NOTE),
    # High e string
    # ('e', 3, T_NOTE),
    # ('e', 5, T_NOTE)
]


def scale_to_note(scale):
    '''
    Converts a scale (list of string/fret tuples) to a nested list of note names.
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
    scale = C_MAJOR_POS4_HIGHLIGHT
    notes = scale_to_note(scale)
    pprint(notes)
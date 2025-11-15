"""
Triad generation utilities for the fretboard learning application.
This file is not used by the program. It is just used to help generate the triad data when creating lessons.
"""
try:
    # This works when imported as part of the package
    from ..constants import (
        create_tuple, CHROMATIC_SCALE, STRING_MAP, FLAT_TO_SHARP
    )
except ImportError:
    # This allows the script to be run directly, resolving the relative import
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from constants import (
        create_tuple, CHROMATIC_SCALE, STRING_MAP, FLAT_TO_SHARP
    )


def normalize_note(note):
    """
    Normalize note name to sharp notation.

    Args:
        note: Note name like 'C', 'F#', 'Bb', etc.

    Returns:
        Note name in sharp notation (e.g., 'Bb' -> 'A#')
    """
    if note in FLAT_TO_SHARP:
        return FLAT_TO_SHARP[note]
    return note


def get_note_at_interval(root, semitones):
    """
    Get the note that is a given number of semitones above the root.

    Args:
        root: Root note name (e.g., 'C', 'F#')
        semitones: Number of semitones above root

    Returns:
        Note name at the specified interval
    """
    root = normalize_note(root)

    if root not in CHROMATIC_SCALE:
        raise ValueError(f"Invalid root note: {root}")

    root_index = CHROMATIC_SCALE.index(root)
    target_index = (root_index + semitones) % 12
    return CHROMATIC_SCALE[target_index]


def parse_key(key):
    """
    Parse a key string to extract root note and triad type.

    Args:
        key: String like 'Cmaj', 'Amin', 'F#major', 'Bbminor'

    Returns:
        Tuple of (root_note, triad_type) where triad_type is 'major' or 'minor'

    Raises:
        ValueError: If key format is invalid
    """
    key = key.strip()
    
    suffix_map = {
        'minor': 'minor', 'min': 'minor',
        'major': 'major', 'maj': 'major'
    }
    
    for suffix, triad_type in suffix_map.items():
        if key.endswith(suffix):
            root = key[:-len(suffix)]
            return (root, triad_type)
            
    raise ValueError(
        f"Invalid key format: {key}. Must end with 'maj', 'major', 'min', or 'minor'"
    )


def generate_triad_notes(key, strings=None, fret_range=(0, 24)):
    """
    Generate all possible positions of a triad on the fretboard.

    This function finds all occurrences of the triad notes (root, third, fifth)
    on the specified strings within the given fret range.

    Args:
        key: Key string like 'Cmaj', 'Amin', 'F#major', 'Bbminor', etc.
            - Ending with 'maj' or 'major' creates a major triad
            - Ending with 'min' or 'minor' creates a minor triad
        strings: List of string indices [0-5] where 0 is high 'e' and 5 is low 'E'.
                 If None, defaults to ['e', 'B', 'G'] (the top 3 strings).
        fret_range: Tuple of (min_fret, max_fret) to limit search area. 
                    Notes on min_fret, max_fret will be included.
                    Default is (0, 24) for entire fretboard.

    Returns:
        Sorted list of (string_name, fret) tuples representing all positions
        where triad notes appear on the specified strings.
        Example: [('e', 0), ('e', 3), ('B', 1), ('G', 0), ...]

    Raises:
        ValueError: If key format is invalid or root note is unrecognized

    Examples:
        >>> generate_triad_notes('Cmaj')  # C major on top 3 strings
        [('e', 0), ('e', 3), ('e', 8), ... ('B', 1), ('B', 5), ... ('G', 0), ('G', 5), ...]

        >>> generate_triad_notes('Amin', strings=[0, 1, 2], fret_range=(0, 12))
        # A minor on top 3 strings, frets 0-12 only

        >>> generate_triad_notes('F#major', strings=[0, 1, 2, 3, 4, 5])
        # F# major on all 6 strings
    """
    # Set default strings if not provided
    #TODO: Better error checking. I don't like strings None by default.
    if strings is None:
        strings = ['e', 'B', 'G']  # Default to top 3 strings

    # Convert string names to indices for create_tuple
    try:
        string_indices = [STRING_MAP[s] for s in strings]
    except KeyError as e:
        raise ValueError(
            f"Invalid string name {e}. Valid names are: {list(STRING_MAP.keys())}"
        ) from e
        
    # Parse the key to get root note and triad type
    root, triad_type = parse_key(key)

    # Calculate intervals based on triad type
    if triad_type == 'major':
        # Major triad: Root, Major 3rd (4 semitones), Perfect 5th (7 semitones)
        intervals = [0, 4, 7]
    else:  # minor
        # Minor triad: Root, Minor 3rd (3 semitones), Perfect 5th (7 semitones)
        intervals = [0, 3, 7]

    # Get the three notes of the triad
    triad_notes = [get_note_at_interval(root, interval) for interval in intervals]

    # Use create_tuple to find all positions of these notes on specified strings
    all_positions = create_tuple(string_indices, triad_notes)

    # Filter by fret range
    min_fret, max_fret = fret_range
    filtered_positions = [
        (string_name, fret) for string_name, fret in all_positions
        if min_fret <= fret <= max_fret
    ]

    return filtered_positions


def get_note_names(notes):
    '''
    '''
    pass

if __name__ == "__main__":
    # This block is for testing purposes.
    # The import logic at the top of the file handles path adjustments,
    # so we only need to import test-specific utilities here.
    from constants import print_tuple

    # Test examples
    print("Testing generate_triad_notes():\n")

    # Test C major
    print("C major triad (top 3 strings):")
    c_maj = generate_triad_notes('Cmaj', strings=['B', 'G', 'D'], fret_range=(0, 15))
    print_tuple(c_maj)
    print_tuple(c_maj, note_names=True)
    print()

    # # Test A minor
    # print("A minor triad (top 3 strings):")
    # a_min = generate_triad_notes('Amin')
    # print_tuple(a_min)
    # print()

    # # Test F# major
    # print("F# major triad (top 3 strings):")
    # fs_maj = generate_triad_notes('F#maj')
    # print_tuple(fs_maj)
    # print()

    # # Test with different strings and fret range
    # print("G major triad (all 6 strings, frets 0-12):")
    # g_maj_all = generate_triad_notes('Gmajor', strings=['e', 'B', 'G', 'D', 'A', 'E'], fret_range=(0, 12))
    # print_tuple(g_maj_all)

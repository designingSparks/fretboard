"""
Guitar Pentatonic Pattern Generator
Generates all 5 CAGED pentatonic patterns for any major or minor scale.
Usage:
generate_pattern()
"""

try:
    # This works when imported as part of the package
    from ..constants import (
        FRETBOARD_NOTES, STRING_MAP, STRING_NAMES
    )
except ImportError:
    # This allows the script to be run directly, resolving the relative import
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from constants import (
        FRETBOARD_NOTES, STRING_MAP, STRING_NAMES
    )

# Base patterns using E minor / G major as reference
# Each pattern stores: root anchor points and note positions
PATTERNS = {
    1: {
        'major_root': ('E', 3),   # G on low E string, fret 3
        'minor_root': ('E', 0),   # E on low E string, open
        'notes': [
            ('e', 0), ('e', 3),
            ('B', 0), ('B', 3),
            ('G', 0), ('G', 2),
            ('D', 0), ('D', 2),
            ('A', 0), ('A', 2),
            ('E', 0), ('E', 3),
        ]
    },
    2: {
        'major_root': ('E', 3),   # G on low E string, fret 3
        'minor_root': ('D', 2),   # E on D string, fret 2
        'notes': [
            ('e', 3), ('e', 5),
            ('B', 3), ('B', 5),
            ('G', 2), ('G', 4),
            ('D', 2), ('D', 5),
            ('A', 2), ('A', 5),
            ('E', 3), ('E', 5),
        ]
    },
    3: {
        'major_root': ('D', 5),   # G on D string, fret 5
        'minor_root': ('A', 7),   # E on A string, fret 7
        'notes': [
            ('e', 5), ('e', 7),
            ('B', 5), ('B', 8),   # Note: 3-fret span due to B string tuning
            ('G', 4), ('G', 7),
            ('D', 5), ('D', 7),
            ('A', 5), ('A', 7),
            ('E', 5), ('E', 7),
        ]
    },
    4: {
        'major_root': ('A', 10),  # G on A string, fret 10
        'minor_root': ('A', 7),   # E on A string, fret 7
        'notes': [
            ('e', 7), ('e', 10),
            ('B', 8), ('B', 10),
            ('G', 7), ('G', 9),
            ('D', 7), ('D', 9),
            ('A', 7), ('A', 10),
            ('E', 7), ('E', 10),
        ]
    },
    5: {
        'major_root': ('A', 10),  # G on A string, fret 10
        'minor_root': ('E', 12),  # E on low E string, fret 12
        'notes': [
            ('e', 10), ('e', 12),
            ('B', 10), ('B', 12),
            ('G', 9), ('G', 12),
            ('D', 9), ('D', 12),
            ('A', 10), ('A', 12),
            ('E', 10), ('E', 12),
        ]
    }
}


def parse_scale_name(scale_name):
    """
    Parse scale name into root note and type.

    Args:
        scale_name: String like 'Gmaj', 'Emin', 'F#maj', 'C#min'

    Returns:
        tuple: (root_note, scale_type) e.g., ('G', 'major')

    Raises:
        ValueError: If scale format is invalid
    """
    scale_name = scale_name.strip()

    # Handle sharp notes
    if len(scale_name) >= 4 and scale_name[1] == '#':
        root = scale_name[:2]
        scale_type = scale_name[2:].lower()
    else:
        root = scale_name[0]
        scale_type = scale_name[1:].lower()

    # Normalize scale type
    if scale_type in ['maj', 'major']:
        return root, 'major'
    elif scale_type in ['min', 'minor']:
        return root, 'minor'
    else:
        raise ValueError(f"Invalid scale type '{scale_type}'. Use 'maj'/'major' or 'min'/'minor'")


def find_note_on_string(note, string_name, start_fret=0):
    """
    Find the first occurrence of a note on a specific string.

    Args:
        note: Note name (e.g., 'E', 'F#')
        string_name: String identifier ('e', 'B', 'G', 'D', 'A', 'E')
        start_fret: Starting fret for search (default: 0)

    Returns:
        int: Fret number, or None if not found
    """
    string_idx = STRING_MAP[string_name]
    for fret in range(start_fret, len(FRETBOARD_NOTES[string_idx])):
        if FRETBOARD_NOTES[string_idx][fret] == note:
            return fret
    return None


def calculate_fret_shift(target_root, scale_type, pattern_num):
    """
    Calculate how many frets to shift a base pattern to reach the target scale.

    Args:
        target_root: Target root note (e.g., 'A', 'F#')
        scale_type: 'major' or 'minor'
        pattern_num: Pattern number (1-5)

    Returns:
        int: Number of frets to shift

    Raises:
        ValueError: If target note cannot be found or pattern is invalid
    """
    if pattern_num not in PATTERNS:
        raise ValueError(f"Pattern {pattern_num} not found. Valid patterns: 1-5")

    pattern = PATTERNS[pattern_num]

    # Select appropriate root reference
    if scale_type == 'major':
        root_string, base_fret = pattern['major_root']
    else:
        root_string, base_fret = pattern['minor_root']

    # Find target root on the same string
    target_fret = find_note_on_string(target_root, root_string)

    if target_fret is None:
        raise ValueError(f"Could not find {target_root} on {root_string} string")

    return target_fret - base_fret


def generate_pattern(scale_name, pattern_num, start_fret=0):
    """
    Generate pentatonic pattern for a given scale and position.

    Args:
        scale_name: Scale name (e.g., 'Gmaj', 'Amin', 'F#min')
        pattern_num: Pattern number (1-5)
        start_fret: Preferred fret range - 0 for frets 0-11, 12 for frets 12-24 (default: 0)

    Returns:
        list: List of (string, fret) tuples representing the pattern.
              Notes are ordered from low E string to high e string, low fret to high fret.

    Raises:
        ValueError: If scale name, pattern, or start_fret is invalid
    """
    # Validate start_fret parameter
    if start_fret not in [0, 12]:
        raise ValueError(f"start_fret must be 0 or 12, got {start_fret}")

    root, scale_type = parse_scale_name(scale_name)

    if pattern_num not in PATTERNS:
        raise ValueError(f"Pattern {pattern_num} not implemented. Valid patterns: 1-5")

    # Calculate shift needed
    shift = calculate_fret_shift(root, scale_type, pattern_num)

    # Apply shift to base pattern
    pattern = PATTERNS[pattern_num]
    shifted_notes = []

    for string, fret in pattern['notes']:
        new_fret = fret + shift
        # Keep notes within fretboard bounds
        if 0 <= new_fret < 25:
            shifted_notes.append((string, new_fret))

    if not shifted_notes:
        return shifted_notes

    # Find the current range of the pattern
    min_fret = min(fret for _, fret in shifted_notes)
    max_fret = max(fret for _, fret in shifted_notes)

    # Determine if octave adjustment is needed based on start_fret preference
    if start_fret == 0:
        # User wants pattern in lower octave (frets 0-11)
        # If the leftmost note is at fret 12 or higher, shift down by 12
        if min_fret >= 12:
            # Attempt to shift down one octave
            wrapped_notes = []
            for string, fret in shifted_notes:
                wrapped_fret = fret - 12
                if 0 <= wrapped_fret < 25:
                    wrapped_notes.append((string, wrapped_fret))

            # Only apply wrap if all notes fit successfully
            if len(wrapped_notes) == len(shifted_notes):
                shifted_notes = wrapped_notes

    elif start_fret == 12:
        # User wants pattern in higher octave (frets 12-24)
        # If the pattern is at or below fret 12, try to shift up by 12
        if max_fret <= 12:
            # Attempt to shift up one octave
            octave_up_notes = []
            for string, fret in shifted_notes:
                octave_fret = fret + 12
                # Must stay within fretboard bounds (< 25)
                if 0 <= octave_fret < 25:
                    octave_up_notes.append((string, octave_fret))

            # Only apply octave shift if ALL notes fit within bounds
            if len(octave_up_notes) == len(shifted_notes):
                shifted_notes = octave_up_notes
            # If not all notes fit, keep the original (don't shift)
            # This prevents partial patterns

    # Reverse the order to start with low E string and end with high e string
    # Group notes by string (preserving fret order within each string),
    # then iterate strings in reverse order (E, A, D, G, B, e)
    # e.g. result = [('E', 0), ('E', 3), ('A', 0), ('A', 2)...
    result = []
    for string in reversed(STRING_NAMES):
        string_notes = [(s, f) for s, f in shifted_notes if s == string]
        result.extend(string_notes)

    return result


def format_pattern_output(scale_name, pattern_num, start_fret=0):
    """
    Format pattern as a Python list for copy-paste.

    Args:
        scale_name: Scale name (e.g., 'Gmaj', 'Amin')
        pattern_num: Pattern number (1-5)
        start_fret: Preferred fret range - 0 for frets 0-11, 12 for frets 12-24 (default: 0)

    Returns:
        str: Formatted Python code string
    """
    pattern = generate_pattern(scale_name, pattern_num, start_fret)
    root, scale_type = parse_scale_name(scale_name)

    # Create clean variable name
    root_clean = root.replace('#', 'SHARP')
    type_suffix = 'MAJ' if scale_type == 'major' else 'MIN'
    var_name = f"{root_clean}_{type_suffix}_PENT_POS{pattern_num}"

    # Group notes by string
    lines = [f"{var_name} = ["]

    for string in STRING_NAMES:
        string_notes = [(s, f) for s, f in pattern if s == string]
        if string_notes:
            notes_str = ', '.join([f"('{s}', {f})" for s, f in string_notes])
            comment = f"  # {string} string"
            lines.append(f"    {notes_str},{comment}")

    lines.append("]")
    return '\n'.join(lines)


def print_pattern(scale_name, pattern_num, start_fret=0):
    """
    Print formatted pattern to console.

    Args:
        scale_name: Scale name (e.g., 'Gmaj', 'Amin')
        pattern_num: Pattern number (1-5)
        start_fret: Preferred fret range - 0 for frets 0-11, 12 for frets 12-24 (default: 0)
    """
    print(format_pattern_output(scale_name, pattern_num, start_fret))


# Example usage
if __name__ == "__main__":
    print("=== PENTATONIC PATTERN GENERATOR ===\n")

    # Pattern 1 examples
    print("PATTERN 1 (Lower Octave):")
    print_pattern('Emin', 1)
    print()
    print_pattern('Amin', 1)
    print("\n" + "="*50 + "\n")

    # Pattern 3 examples
    print("PATTERN 3 (Lower Octave):")
    print_pattern('Emin', 3)
    print()
    print_pattern('Cmaj', 3)
    print("\n" + "="*50 + "\n")

    # Demonstrate start_fret parameter
    print("OCTAVE SELECTION DEMO:")
    print("Same pattern, different octaves using start_fret parameter\n")

    print("E minor Pattern 1 - Lower octave (start_fret=0):")
    print_pattern('Emin', 1, start_fret=0)
    print()

    print("E minor Pattern 1 - Higher octave (start_fret=12):")
    print_pattern('Emin', 1, start_fret=12)
    print("\n" + "="*50 + "\n")

    # Another example with different scale
    print("A minor Pattern 3 - Lower octave (start_fret=0):")
    print_pattern('Amin', 3, start_fret=0)
    print()

    print("A minor Pattern 3 - Higher octave (start_fret=12):")
    print_pattern('Amin', 3, start_fret=12)
    print("\n" + "="*50 + "\n")

    # Example where higher octave won't fit
    print("BOUNDARY CHECK DEMO:")
    print("G major Pattern 5 already extends high on fretboard")
    print("Requesting higher octave will keep it in lower range if it doesn't fit:\n")

    print("G major Pattern 5 - Lower octave (start_fret=0):")
    print_pattern('Gmaj', 5, start_fret=0)
    print()

    print("G major Pattern 5 - Request higher octave (start_fret=12):")
    print("(Will only shift if all notes fit within fret 24)")
    print_pattern('Gmaj', 5, start_fret=12)

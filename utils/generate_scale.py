"""
Guitar Pentatonic Pattern Generator
Generates all 5 CAGED pentatonic patterns for any major or minor scale.
"""

# Fretboard note mapping (25 frets, 6 strings)
FRETBOARD_NOTES = [
    ['E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E'],  # High e
    ['B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],  # B
    ['G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G'],  # G
    ['D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D'],  # D
    ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A'],  # A
    ['E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E']   # Low E
]

STRING_MAP = {'e': 0, 'B': 1, 'G': 2, 'D': 3, 'A': 4, 'E': 5}
STRING_NAMES = ['e', 'B', 'G', 'D', 'A', 'E']

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
        'minor_root': ('e', 7),   # E on high e string, fret 7
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
        'major_root': ('e', 10),  # G on high e string, fret 10
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


def generate_pattern(scale_name, pattern_num):
    """
    Generate pentatonic pattern for a given scale and position.
    
    Args:
        scale_name: Scale name (e.g., 'Gmaj', 'Amin', 'F#min')
        pattern_num: Pattern number (1-5)
    
    Returns:
        list: List of (string, fret) tuples representing the pattern
    
    Raises:
        ValueError: If scale name or pattern is invalid
    """
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
    
    return shifted_notes


def format_pattern_output(scale_name, pattern_num):
    """
    Format pattern as a Python list for copy-paste.
    
    Args:
        scale_name: Scale name (e.g., 'Gmaj', 'Amin')
        pattern_num: Pattern number (1-5)
    
    Returns:
        str: Formatted Python code string
    """
    pattern = generate_pattern(scale_name, pattern_num)
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


def print_pattern(scale_name, pattern_num):
    """Print formatted pattern to console."""
    print(format_pattern_output(scale_name, pattern_num))


# Example usage
if __name__ == "__main__":
    print("=== PENTATONIC PATTERN GENERATOR ===\n")
    
    # Pattern 1 examples
    print("PATTERN 1:")
    print_pattern('Emin', 1)
    print()
    print_pattern('Amin', 1)
    print("\n" + "="*50 + "\n")
    
    # Pattern 3 examples
    print("PATTERN 3:")
    print_pattern('Emin', 3)
    print()
    print_pattern('Cmaj', 3)
    print("\n" + "="*50 + "\n")
    
    # Pattern 5 examples
    print("PATTERN 5:")
    print_pattern('Gmaj', 5)
    print()
    print_pattern('F#min', 5)
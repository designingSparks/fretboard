FRETBOARD_NOTES = [
    # 0: High 'e' string
    ['E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E'],
    # 1: 'B' string
    ['B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],
    # 2: 'G' string
    ['G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G'],
    # 3: 'D' string
    ['D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D'],
    # 4: 'A' string
    ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A'],
    # 5: Low 'E' string
    ['E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E']
]

# String name to index mapping
STRING_MAP = {'e': 0, 'B': 1, 'G': 2, 'D': 3, 'A': 4, 'E': 5}
STRING_NAMES = ['e', 'B', 'G', 'D', 'A', 'E']

# Base Pattern 1 - relative to root positions
# For the base pattern shown: E minor pentatonic / G major pentatonic
# Major root (G) is on E string at fret 3 (rightmost on E string)
# Minor root (E) is on E string at fret 0 (leftmost on E string)
PATTERN_1_BASE = {
    'major_root_string': 'E',
    'major_root_fret': 3,  # G on low E string
    'minor_root_string': 'E', 
    'minor_root_fret': 0,  # E on low E string (open)
    # Pattern positions relative to minor root (E at fret 0)
    'notes': [
        ('e', 0), ('e', 3),  # High e string
        ('B', 0), ('B', 3),
        ('G', 0), ('G', 2),
        ('D', 0), ('D', 2),
        ('A', 0), ('A', 2),
        ('E', 0), ('E', 3),  # Low E string
    ]
}

PATTERN_2_BASE = {
    'major_root_string': 'E', # Corrected
    'major_root_fret': 3,  # G on low E string, which is the root of G major for this pattern shape
    'minor_root_string': 'D', 
    'minor_root_fret': 2,  # E on D string, which is the root of E minor for this pattern shape
    # Pattern positions relative to minor root (E at fret 0)
    'notes': [
        ('e', 3), ('e', 5), # High e string
        ('B', 3), ('B', 5),
        ('G', 2), ('G', 4),
        ('D', 2), ('D', 5),
        ('A', 2), ('A', 5),
        ('E', 3), ('E', 5),  # Low E string
    ]
}

PATTERN_3_BASE = {
    'major_root_string': 'D', # G on D string
    'major_root_fret': 5,  
    'minor_root_string': 'A', # E on A string
    'minor_root_fret': 7,
    # Pattern notes for Gmaj / Emin (from image)
    'notes': [
        ('e', 5), ('e', 7),  # High e string
        ('B', 5), ('B', 8),
        ('G', 4), ('G', 7),
        ('D', 5), ('D', 7),
        ('A', 5), ('A', 7),
        ('E', 5), ('E', 7),  # Low E string
    ]
}

PATTERN_4_BASE = {
    'major_root_string': 'A', # G 
    'major_root_fret': 10,
    'minor_root_string': 'e', # E on high e string
    'minor_root_fret': 7,
    # Pattern notes for Gmaj / Emin
    'notes': [
        ('e', 7), ('e', 10), # High e string
        ('B', 8), ('B', 10),
        ('G', 7), ('G', 9),
        ('D', 7), ('D', 9),
        ('A', 7), ('A', 10),
        ('E', 7), ('E', 10), # Low E string
    ]
}

PATTERN_5_BASE = {
    'major_root_string': 'e', # G on high e string
    'major_root_fret': 10,
    'minor_root_string': 'E', # E on low E string
    'minor_root_fret': 12,
    # Pattern notes for Gmaj / Emin
    'notes': [
        ('e', 10), ('e', 12), # High e string
        ('B', 10), ('B', 12),
        ('G', 9), ('G', 12),
        ('D', 9), ('D', 12),
        ('A', 10), ('A', 12),
        ('E', 10), ('E', 12), # Low E string
    ]
}


ALL_PATTERNS = {1: PATTERN_1_BASE, 2: PATTERN_2_BASE, 3: PATTERN_3_BASE, 4: PATTERN_4_BASE, 5: PATTERN_5_BASE}

def parse_scale_name(scale_name):
    """
    Parse scale name into root note and type.
    Examples: 'Gmaj' -> ('G', 'major'), 'Emin' -> ('E', 'minor')
    """
    scale_name = scale_name.strip()
    
    # Handle sharp notes (e.g., 'F#maj', 'C#min')
    if len(scale_name) >= 4 and scale_name[1] == '#':
        root = scale_name[:2]
        scale_type = scale_name[2:].lower()
    else:
        root = scale_name[0]
        scale_type = scale_name[1:].lower()
    
    if scale_type in ['maj', 'major']:
        return root, 'major'
    elif scale_type in ['min', 'minor']:
        return root, 'minor'
    else:
        raise ValueError(f"Invalid scale type in '{scale_name}'. Use 'maj' or 'min'")

def find_note_fret(note, string_name, start_fret=0):
    """Find the fret number of a note on a specific string."""
    string_idx = STRING_MAP[string_name]
    for fret in range(start_fret, 25):
        if FRETBOARD_NOTES[string_idx][fret] == note:
            return fret
    return None


def calculate_shift(target_root, target_type, pattern_num):
    """Calculate how many frets to shift the base pattern."""
    
    pattern = ALL_PATTERNS.get(pattern_num)
    if not pattern:
        raise NotImplementedError(f"Pattern {pattern_num} not yet implemented")
    
    # Find the fret of the target root on the pattern's designated root string
    if target_type == 'major':
        base_root_fret = pattern['major_root_fret']
        root_string = pattern['major_root_string']
        target_root_fret = find_note_fret(target_root, root_string)
    else:  # minor
        base_root_fret = pattern['minor_root_fret']
        root_string = pattern['minor_root_string']
        target_root_fret = find_note_fret(target_root, root_string)
    
    if target_root_fret is None:
        raise ValueError(f"Could not find {target_root} on {root_string} string")
    
    # The shift is the difference between where the root *should* be
    # and where it is in the base pattern.
    return target_root_fret - base_root_fret

def generate_pattern(scale_name, pos_num):
    """Generate the pattern for a given scale and position."""
    root, scale_type = parse_scale_name(scale_name)
    
    if pos_num not in ALL_PATTERNS:
        raise NotImplementedError(f"Only positions {', '.join(map(str, ALL_PATTERNS.keys()))} are currently implemented")
    
    # Calculate the shift needed
    shift = calculate_shift(root, scale_type, pos_num)
    
    # Select the correct base pattern to apply the shift to
    pattern = ALL_PATTERNS[pos_num]

    shifted_notes = []
    
    for string, fret in pattern['notes']:
        new_fret = fret + shift
        if 0 <= new_fret < 25:  # Stay within fretboard bounds
            shifted_notes.append((string, new_fret))
    
    return shifted_notes


def print_scale(scale_name, pos_num):
    """
    Print the scale pattern for copy-paste.
    
    Args:
        scale_name: e.g., 'Gmaj', 'Emin', 'C#maj', 'F#min'
        pos_num: Pattern number (1-5)
    """
    scale = generate_pattern(scale_name, pos_num)
    
    # Create a clean variable name
    root, scale_type = parse_scale_name(scale_name)
    root_clean = root.replace('#', 'SHARP')
    type_str = 'MAJ' if scale_type == 'major' else 'MIN'
    var_name = f"{root_clean}_{type_str}_PENT_POS{pos_num}_HIGHLIGHT"
    
    print(f"\n{var_name} = [")
    for string in STRING_NAMES:
        string_notes = [note for note in scale if note[0] == string]
        if string_notes:
            notes_str = ', '.join([f"('{s}', {f})" for s, f in string_notes])
            comment = f"  # {string} string" if string in ['e', 'E'] else ""
            print(f"    {notes_str},{comment}")
    print("]")

# Example usage
if __name__ == "__main__":
    print("=== PATTERN 1 EXAMPLES ===")
    
    # Base patterns from the diagram
    # print_scale('Emin', 1)  # E minor pentatonic
    # print_scale('Gmaj', 1)  # G major pentatonic
    
    # # Shifted examples
    # print_scale('Amin', 1)  # A minor pentatonic (shifted up 5 frets)
    # print_scale('Cmaj', 1)  # C major pentatonic (shifted up 5 frets)
    
    # print_scale('F#min', 1)  # F# minor pentatonic (shifted up 2 frets)
    # print_scale('Amaj', 1)   # A major pentatonic (shifted up 2 frets)

    # print("\n=== PATTERN 2 EXAMPLES ===")
    # print_scale('Emin', 2)   # E minor pentatonic (base pattern, no shift)
    # print_scale('Gmaj', 2)   # G major pentatonic (base pattern, no shift)
    # print_scale('Amin', 2)   # A minor pentatonic (shifted up 5 frets)
    # print_scale('Cmaj', 2)   # C major pentatonic (shifted up 5 frets)

    print("\n=== PATTERN 3 EXAMPLES ===")
    print_scale('Emin', 3)   # E minor pentatonic (base pattern, no shift)
    print_scale('Gmaj', 3)   # G major pentatonic (base pattern, no shift)
    print_scale('Amin', 3)   # A minor pentatonic (shifted up 5 frets)
    print_scale('Cmaj', 3)   # C major pentatonic (shifted up 5 frets)

    print("\n=== PATTERN 4 EXAMPLES ===")
    print_scale('Emin', 4)
    print_scale('Gmaj', 4)
    print_scale('Cmaj', 4)

    print("\n=== PATTERN 5 EXAMPLES ===")
    print_scale('Emin', 5)
    print_scale('Gmaj', 5)
    print_scale('Cmaj', 5)
    
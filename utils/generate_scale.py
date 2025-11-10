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
    'major_root_string': 'E',
    'major_root_fret': 3,  # G on low E string
    'minor_root_string': 'D', 
    'minor_root_fret': 2,  # E on D sting, i.e. Emin
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
    if pattern_num == 1:
        pattern = PATTERN_1_BASE
        
        if target_type == 'major':
            # Find where the target root appears on the major root string
            base_root_fret = pattern['major_root_fret']
            target_root_fret = find_note_fret(target_root, pattern['major_root_string'])
        else:  # minor
            # Find where the target root appears on the minor root string
            base_root_fret = pattern['minor_root_fret']
            target_root_fret = find_note_fret(target_root, pattern['minor_root_string'])
        
        if target_root_fret is None:
            raise ValueError(f"Could not find {target_root} on {pattern['major_root_string']} string")
        
        return target_root_fret - base_root_fret
    
    raise NotImplementedError(f"Pattern {pattern_num} not yet implemented")

def generate_pattern(scale_name, pos_num):
    """Generate the pattern for a given scale and position."""
    root, scale_type = parse_scale_name(scale_name)
    
    if pos_num != 1:
        raise NotImplementedError(f"Only position 1 is currently implemented")
    
    # Calculate the shift needed
    shift = calculate_shift(root, scale_type, pos_num)
    
    # Apply shift to base pattern
    pattern = PATTERN_1_BASE
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
        pos_num: Pattern number (1-5, currently only 1 implemented)
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
    print_scale('Emin', 1)  # E minor pentatonic
    print_scale('Gmaj', 1)  # G major pentatonic
    
    # Shifted examples
    print_scale('Amin', 1)  # A minor pentatonic (shifted up 5 frets)
    print_scale('Cmaj', 1)  # C major pentatonic (shifted up 5 frets)
    
    print_scale('F#min', 1)  # F# minor pentatonic (shifted up 2 frets)
    print_scale('Amaj', 1)   # A major pentatonic (shifted up 2 frets)
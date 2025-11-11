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

# Scale interval patterns (in semitones from root)
SCALE_PATTERNS = {
    'major': [2, 2, 1, 2, 2, 2, 1],  # W-W-H-W-W-W-H
    'minor': [2, 1, 2, 2, 1, 2, 2],  # W-H-W-W-H-W-W
    'major_pentatonic': [2, 2, 3, 2, 3],  # W-W-m3-W-m3
    'minor_pentatonic': [3, 2, 2, 3, 2]   # m3-W-W-m3-W
}

# String name to index mapping
STRING_MAP = {'e': 0, 'B': 1, 'G': 2, 'D': 3, 'A': 4, 'E': 5}
STRING_NAMES = ['e', 'B', 'G', 'D', 'A', 'E']

# CAGED position definitions based on actual C Major scale diagrams:
# Position 1 (C shape): Spans frets 7-10, roots at E-8, D-10, e-8
# Position 2 (A shape): Spans frets 9-13, roots at D-10, B-13
# Position 3 (G shape): Spans frets 12-15, roots at B-13, D-15
# Position 4 (E shape): Spans frets 15-18, roots at A-15, G-17
# Position 5 (D shape): Spans frets 17-21, roots at G-17, E-20, e-20

# Reference: For C Major, root C appears on low E string at fret 8
# Each position offset is relative to that fret 8 reference point

CAGED_POSITION_OFFSETS = {
    1: {'reference_string': 'E', 'offset': 0, 'range': (-1, 2)},    # C shape: frets 7-10 (8-1 to 8+2)
    2: {'reference_string': 'E', 'offset': 2, 'range': (1, 5)},     # A shape: frets 9-13 (8+1 to 8+5)
    3: {'reference_string': 'E', 'offset': 7, 'range': (4, 7)},     # G shape: frets 12-15 (8+4 to 8+7)
    4: {'reference_string': 'E', 'offset': 7, 'range': (7, 10)},    # E shape: frets 15-18 (8+7 to 8+10)
    5: {'reference_string': 'E', 'offset': 12, 'range': (9, 13)},   # D shape: frets 17-21 (8+9 to 8+13)
}

def get_scale_notes(root_note, scale_type):
    """Generate all notes in a given scale."""
    chromatic = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    if root_note not in chromatic:
        raise ValueError(f"Invalid root note: {root_note}")
    
    if scale_type not in SCALE_PATTERNS:
        raise ValueError(f"Invalid scale type: {scale_type}")
    
    root_idx = chromatic.index(root_note)
    intervals = SCALE_PATTERNS[scale_type]
    
    scale_notes = [root_note]
    current_idx = root_idx
    
    for interval in intervals[:-1]:  # Don't include the last interval (returns to root)
        current_idx = (current_idx + interval) % 12
        scale_notes.append(chromatic[current_idx])
    
    return scale_notes

def find_note_on_string(note, string_name, start_fret=0):
    """Find the fret number of a note on a specific string, starting from start_fret."""
    string_idx = STRING_MAP[string_name]
    for fret in range(start_fret, 25):
        if FRETBOARD_NOTES[string_idx][fret] == note:
            return fret
    return None

def generate_scale(root_note, scale_type, position, shift_left=False):
    """
    Generate a scale for any root note, scale type, and CAGED position.
    
    Args:
        root_note: Root note (e.g., 'C', 'D', 'F#')
        scale_type: One of 'major', 'minor', 'major_pentatonic', 'minor_pentatonic'
        position: CAGED position (1-5)
        shift_left: If True, shift positions starting at fret 12+ down by 12 frets (one octave)
    
    Returns:
        List of (string, fret) tuples for the scale
    """
    if position not in range(1, 6):
        raise ValueError(f"Position must be 1-5, got {position}")
    
    # Get valid notes for this scale
    valid_notes = get_scale_notes(root_note, scale_type)
    
    # Get position configuration
    pos_config = CAGED_POSITION_OFFSETS[position]
    
    # Find the root note on the low E string first (as reference)
    root_on_e = find_note_on_string(root_note, 'E', 0)
    if root_on_e is None:
        raise ValueError(f"Could not find {root_note} on low E string")
    
    # Calculate the center fret for this position
    center_fret = root_on_e + pos_config['offset']
    
    # Apply octave shift if requested and position starts at or above fret 12
    if shift_left and center_fret >= 12:
        center_fret -= 12
    
    # Define the fret range for this position
    fret_min = center_fret + pos_config['range'][0]
    fret_max = center_fret + pos_config['range'][1]
    
    scale = []
    
    # For each string, find 2-3 notes within the fret range
    for string in STRING_NAMES:
        string_idx = STRING_MAP[string]
        string_notes = []
        
        # Search in the fret range for valid scale notes
        for fret in range(max(0, fret_min), min(25, fret_max + 1)):
            note = FRETBOARD_NOTES[string_idx][fret]
            if note in valid_notes:
                string_notes.append((string, fret))
        
        # Take 2-3 notes per string
        if len(string_notes) >= 2:
            scale.extend(string_notes[:3])
        elif len(string_notes) == 1:
            # For some positions/strings, we might only have 1 note in range
            # Try to extend the range slightly to find more notes
            for fret in range(max(0, fret_min - 1), max(0, fret_min)):
                note = FRETBOARD_NOTES[string_idx][fret]
                if note in valid_notes and (string, fret) not in string_notes:
                    string_notes.insert(0, (string, fret))
                    break
            for fret in range(min(25, fret_max + 1), min(25, fret_max + 2)):
                note = FRETBOARD_NOTES[string_idx][fret]
                if note in valid_notes and (string, fret) not in string_notes:
                    string_notes.append((string, fret))
                    if len(string_notes) >= 2:
                        break
            
            if len(string_notes) >= 2:
                scale.extend(string_notes[:3])
    
    return scale

def print_scale_for_copy(scale, name):
    """Print scale in a format ready to copy-paste."""
    print(f"\n{name} = [")
    for string in STRING_NAMES:
        string_notes = [note for note in scale if note[0] == string]
        if string_notes:
            notes_str = ','.join([f"('{s}', {f})" for s, f in string_notes])
            comment = f"  # {string} string" if string in ['e', 'E'] else ""
            print(f"    {notes_str},{comment}")
    print("]")

# Example usage
if __name__ == "__main__":
    # Generate C Major in all 5 positions
    print("=== C MAJOR SCALE - ALL 5 POSITIONS ===")
    for pos in range(1, 6):
        scale = generate_scale('C', 'major', pos)
        print_scale_for_copy(scale, f"C_MAJOR_POS{pos}_HIGHLIGHT")
    
    # Generate positions with shift_left for lower fret positions
    print("\n=== C MAJOR SCALE - POSITIONS WITH SHIFT_LEFT ===")
    for pos in [3, 4, 5]:
        scale = generate_scale('C', 'major', pos, shift_left=True)
        print_scale_for_copy(scale, f"C_MAJOR_POS{pos}_SHIFTED_HIGHLIGHT")
    
    # Generate other examples
    print("\n=== OTHER EXAMPLES ===")
    
    # D Minor Pentatonic in position 3
    scale = generate_scale('D', 'minor_pentatonic', 3)
    print_scale_for_copy(scale, "D_MINOR_PENT_POS3_HIGHLIGHT")
    
    # F# Major in position 2
    scale = generate_scale('F#', 'major', 2)
    print_scale_for_copy(scale, "FSHARP_MAJOR_POS2_HIGHLIGHT")
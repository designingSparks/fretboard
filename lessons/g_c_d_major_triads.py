"""G-C-D major triads in three positions on each adjacent three-string set."""

from models.lesson_model import Part, Lesson

TON = 1000  # Duration of each triad in milliseconds


def _display_notes(sequence):
    """Collect unique positions; each row ends with its chord name and duration."""
    return list(dict.fromkeys(note for row in sequence for note in row[:-2]))


# Part 1: High e, B, G. Three successive G voicings with nearby C and D triads.
PART1_SEQUENCE = [
    [('e', 3), ('B', 3), ('G', 4), 'G', TON],  # E shape
    [('e', 3), ('B', 5), ('G', 5), 'C', TON],  # A shape
    [('e', 5), ('B', 7), ('G', 7), 'D', TON],  # A shape

    [('e', 7), ('B', 8), ('G', 7), 'G', TON],  # C/D shape on these strings
    [('e', 8), ('B', 8), ('G', 9), 'C', TON],  # E shape
    [('e', 10), ('B', 10), ('G', 11), 'D', TON],  # E shape

    [('e', 10), ('B', 12), ('G', 12), 'G', TON],  # A shape: next higher G voicing
    [('e', 12), ('B', 13), ('G', 12), 'C', TON],  # C/D shape on these strings
    [('e', 14), ('B', 15), ('G', 14), 'D', TON],  # C/D shape on these strings
]
PART1_NOTES = _display_notes(PART1_SEQUENCE)

part1 = Part(
    name="G - C - D on strings G, B, e",
    notes_to_highlight=PART1_NOTES,
    play_sequence=PART1_SEQUENCE,
    highlight_chord_root=True,
    circle_sequence_elements=False,
    wrapping_distance=8,
    fillet_corners=True,
    fillet_radius=24,
    description=(
        "Play G-C-D in three ascending positions on the top three strings. "
        "The G triads use E, C/D, and A shapes; C and D use nearby inversions."
    ),
)

# Part 2: B, G, D. Start with open-position G, then move up through its inversions.
PART2_SEQUENCE = [
    [('B', 0), ('G', 0), ('D', 0), 'G', TON],
    [('B', 1), ('G', 0), ('D', 2), 'C', TON],
    [('B', 3), ('G', 2), ('D', 4), 'D', TON],

    [('B', 3), ('G', 4), ('D', 5), 'G', TON],
    [('B', 5), ('G', 5), ('D', 5), 'C', TON],
    [('B', 7), ('G', 7), ('D', 7), 'D', TON],

    [('B', 8), ('G', 7), ('D', 9), 'G', TON],
    [('B', 8), ('G', 9), ('D', 10), 'C', TON],
    [('B', 10), ('G', 11), ('D', 12), 'D', TON],
]
PART2_NOTES = _display_notes(PART2_SEQUENCE)

part2 = Part(
    name="G - C - D on strings D, G, B",
    notes_to_highlight=PART2_NOTES,
    play_sequence=PART2_SEQUENCE,
    highlight_chord_root=True,
    circle_sequence_elements=False,
    wrapping_distance=8,
    fillet_corners=True,
    fillet_radius=24,
    description="Play G-C-D in three ascending positions on the D, G, and B strings.",
)

# Part 3: G, D, A. Each group contains the root, third, and fifth of its chord.
PART3_SEQUENCE = [
    [('G', 0), ('D', 0), ('A', 2), 'G', TON],
    [('G', 0), ('D', 2), ('A', 3), 'C', TON],
    [('G', 2), ('D', 4), ('A', 5), 'D', TON],

    [('G', 4), ('D', 5), ('A', 5), 'G', TON],
    [('G', 5), ('D', 5), ('A', 7), 'C', TON],
    [('G', 7), ('D', 7), ('A', 9), 'D', TON],

    [('G', 7), ('D', 9), ('A', 10), 'G', TON],
    [('G', 9), ('D', 10), ('A', 10), 'C', TON],
    [('G', 11), ('D', 12), ('A', 12), 'D', TON],
]
PART3_NOTES = _display_notes(PART3_SEQUENCE)

part3 = Part(
    name="G - C - D on strings A, D, G",
    notes_to_highlight=PART3_NOTES,
    play_sequence=PART3_SEQUENCE,
    highlight_chord_root=True,
    circle_sequence_elements=False,
    wrapping_distance=8,
    fillet_corners=True,
    fillet_radius=24,
    description="Play G-C-D in three ascending positions on the A, D, and G strings.",
)

# Part 4: D, A, low E. Three G-C-D groups on the bottom three strings.
PART4_SEQUENCE = [
    [('D', 0), ('A', 2), ('E', 3), 'G', TON],
    [('D', 2), ('A', 3), ('E', 3), 'C', TON],
    [('D', 4), ('A', 5), ('E', 5), 'D', TON],

    [('D', 5), ('A', 5), ('E', 7), 'G', TON],
    [('D', 5), ('A', 7), ('E', 8), 'C', TON],
    [('D', 7), ('A', 9), ('E', 10), 'D', TON],

    [('D', 9), ('A', 10), ('E', 10), 'G', TON],
    [('D', 10), ('A', 10), ('E', 12), 'C', TON],
    [('D', 12), ('A', 12), ('E', 14), 'D', TON],
]
PART4_NOTES = _display_notes(PART4_SEQUENCE)

part4 = Part(
    name="G - C - D on strings E, A, D",
    notes_to_highlight=PART4_NOTES,
    play_sequence=PART4_SEQUENCE,
    highlight_chord_root=True,
    circle_sequence_elements=False,
    wrapping_distance=8,
    fillet_corners=True,
    fillet_radius=24,
    description="Play G-C-D in three ascending positions on the low E, A, and D strings.",
)

lesson = Lesson(
    name="G - C - D major triads",
    chord_label_title="Triad playing",
    parts=[part1, part2, part3, part4],
    description=(
        "Practice a I-IV-V progression in G major in three positions on each "
        "of the four adjacent three-string sets."
    ),
    difficulty="Beginner",
    metadata={
        'key': 'G',
        'tags': ['triads', 'G major', 'chord progression', 'barre chords', 'inversions'],
    },
)

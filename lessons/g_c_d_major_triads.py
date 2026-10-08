"""G, C, and D major triads on the G, B, and high e strings."""

from models.lesson_model import Part, Lesson

TON = 1000  # Duration of each triad in milliseconds

PART1_NOTES = [
    ('e', 3), ('e', 5),
    ('B', 3), ('B', 5), ('B', 7),
    ('G', 4), ('G', 5), ('G', 7),
]

PART1_SEQUENCE = [
    [('e', 3), ('B', 3), ('G', 4), TON],  # G: E-shaped barre chord
    [('e', 3), ('B', 5), ('G', 5), TON],  # C: A-shaped barre chord
    [('e', 5), ('B', 7), ('G', 7), TON],  # D: A-shaped barre chord
]

part1 = Part(
    name="G - C - D on strings G, B, e",
    notes_to_highlight=PART1_NOTES,
    play_sequence=PART1_SEQUENCE,
    circle_sequence_elements=True,
    wrapping_distance=8,
    fillet_corners=True,
    fillet_radius=24,
    description=(
        "Play G from the E-shaped barre chord (frets 3 and 4), then C "
        "from the A-shaped barre chord (frets 3 and 5), then D from the "
        "A-shaped barre chord (frets 5 and 7). Use only the top three strings."
    ),
)

lesson = Lesson(
    name="G - C - D major triads",
    parts=[part1],
    description="Practice a I-IV-V progression in G major using top-string triads.",
    difficulty="Beginner",
    metadata={
        'key': 'G',
        'tags': ['triads', 'G major', 'chord progression', 'barre chords'],
    },
)

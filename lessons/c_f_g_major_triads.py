"""C-F-G major triads in four positions on each adjacent three-string set."""

from models.lesson_model import Part, Lesson
from models.sequence_step import SequenceStep

TON = 1000  # Duration of each triad in milliseconds


def _display_notes(sequence):
    """Collect the unique note positions from the named steps."""
    return list(dict.fromkeys(note for step in sequence for note in step.notes))


# Part 1: High e, B, G. Four successive C voicings with nearby F and G triads.
PART1_SEQUENCE = [
    SequenceStep(
        notes=(('e', 0), ('B', 1), ('G', 0)),
        chord_name='C_{0-1}',
        duration_ms=TON,
        shape='C/D',
        position_group=1,
    ),
    SequenceStep(
        notes=(('e', 1), ('B', 1), ('G', 2)),
        chord_name='F_{1-2}',
        duration_ms=TON,
        shape='E',
        position_group=1,
    ),
    SequenceStep(
        notes=(('e', 3), ('B', 3), ('G', 4)),
        chord_name='G_{3-4}',
        duration_ms=TON,
        shape='E',
        position_group=1,
    ),

    SequenceStep(
        notes=(('e', 3), ('B', 5), ('G', 5)),
        chord_name='C_{3-5}',
        duration_ms=TON,
        shape='A',
        position_group=2,
    ),
    SequenceStep(
        notes=(('e', 5), ('B', 6), ('G', 5)),
        chord_name='F_{5-6}',
        duration_ms=TON,
        shape='C/D',
        position_group=2,
    ),
    SequenceStep(
        notes=(('e', 7), ('B', 8), ('G', 7)),
        chord_name='G_{7-8}',
        duration_ms=TON,
        shape='C/D',
        position_group=2,
    ),

    SequenceStep(
        notes=(('e', 8), ('B', 8), ('G', 9)),
        chord_name='C_{8-9}',
        duration_ms=TON,
        shape='E',
        position_group=3,
    ),
    SequenceStep(
        notes=(('e', 8), ('B', 10), ('G', 10)),
        chord_name='F_{8-10}',
        duration_ms=TON,
        shape='A',
        position_group=3,
    ),
    SequenceStep(
        notes=(('e', 10), ('B', 12), ('G', 12)),
        chord_name='G_{10-12}',
        duration_ms=TON,
        shape='A',
        position_group=3,
    ),

    SequenceStep(
        notes=(('e', 12), ('B', 13), ('G', 12)),
        chord_name='C_{12-13}',
        duration_ms=TON,
        shape='C/D',
        position_group=4,
    ),
    SequenceStep(
        notes=(('e', 13), ('B', 13), ('G', 14)),
        chord_name='F_{13-14}',
        duration_ms=TON,
        shape='E',
        position_group=4,
    ),
    SequenceStep(
        notes=(('e', 15), ('B', 15), ('G', 16)),
        chord_name='G_{15-16}',
        duration_ms=TON,
        shape='E',
        position_group=4,
    ),
]
PART1_NOTES = _display_notes(PART1_SEQUENCE)

part1 = Part(
    name="1. Strings G, B, e",
    background_notes=PART1_NOTES,
    play_sequence=PART1_SEQUENCE,
    highlight_chord_root=True,
    circle_sequence_elements=False,
    wrapping_distance=8,
    fillet_corners=True,
    fillet_radius=24,
    description=(
        "Play C-F-G in four ascending positions on the top three strings. "
        "The C triads use C/D, A, E, and C/D shapes; F and G use nearby inversions."
    ),
)

# Part 2: B, G, D. Start with open-position C, then move up through its inversions.
PART2_SEQUENCE = [
    SequenceStep(notes=(('B', 1), ('G', 0), ('D', 2)), duration_ms=TON, chord_name='C_{0-2}', position_group=1),
    SequenceStep(notes=(('B', 1), ('G', 2), ('D', 3)), duration_ms=TON, chord_name='F_{1-3}', position_group=1),
    SequenceStep(notes=(('B', 3), ('G', 4), ('D', 5)), duration_ms=TON, chord_name='G_{3-5}', position_group=1),

    SequenceStep(notes=(('B', 5), ('G', 5), ('D', 5)), duration_ms=TON, chord_name='C_{5}', position_group=2),
    SequenceStep(notes=(('B', 6), ('G', 5), ('D', 7)), duration_ms=TON, chord_name='F_{5-7}', position_group=2),
    SequenceStep(notes=(('B', 8), ('G', 7), ('D', 9)), duration_ms=TON, chord_name='G_{7-9}', position_group=2),

    SequenceStep(notes=(('B', 8), ('G', 9), ('D', 10)), duration_ms=TON, chord_name='C_{8-10}', position_group=3),
    SequenceStep(notes=(('B', 10), ('G', 10), ('D', 10)), duration_ms=TON, chord_name='F_{10}', position_group=3),
    SequenceStep(notes=(('B', 12), ('G', 12), ('D', 12)), duration_ms=TON, chord_name='G_{12}', position_group=3),

    SequenceStep(notes=(('B', 13), ('G', 12), ('D', 14)), duration_ms=TON, chord_name='C_{12-14}', position_group=4),
    SequenceStep(notes=(('B', 13), ('G', 14), ('D', 15)), duration_ms=TON, chord_name='F_{13-15}', position_group=4),
    SequenceStep(notes=(('B', 15), ('G', 16), ('D', 17)), duration_ms=TON, chord_name='G_{15-17}', position_group=4),
]
PART2_NOTES = _display_notes(PART2_SEQUENCE)

part2 = Part(
    name="2. Strings D, G, B",
    background_notes=PART2_NOTES,
    play_sequence=PART2_SEQUENCE,
    highlight_chord_root=True,
    circle_sequence_elements=False,
    wrapping_distance=8,
    fillet_corners=True,
    fillet_radius=24,
    description="Play C-F-G in four ascending positions on the D, G, and B strings.",
)

# Part 3: G, D, A. Each group contains the root, third, and fifth of its chord.
PART3_SEQUENCE = [
    SequenceStep(notes=(('G', 0), ('D', 2), ('A', 3)), duration_ms=TON, chord_name='C_{0-3}', position_group=1),
    SequenceStep(notes=(('G', 2), ('D', 3), ('A', 3)), duration_ms=TON, chord_name='F_{2-3}', position_group=1),
    SequenceStep(notes=(('G', 4), ('D', 5), ('A', 5)), duration_ms=TON, chord_name='G_{4-5}', position_group=1),

    SequenceStep(notes=(('G', 5), ('D', 5), ('A', 7)), duration_ms=TON, chord_name='C_{5-7}', position_group=2),
    SequenceStep(notes=(('G', 5), ('D', 7), ('A', 8)), duration_ms=TON, chord_name='F_{5-8}', position_group=2),
    SequenceStep(notes=(('G', 7), ('D', 9), ('A', 10)), duration_ms=TON, chord_name='G_{7-10}', position_group=2),

    SequenceStep(notes=(('G', 9), ('D', 10), ('A', 10)), duration_ms=TON, chord_name='C_{9-10}', position_group=3),
    SequenceStep(notes=(('G', 10), ('D', 10), ('A', 12)), duration_ms=TON, chord_name='F_{10-12}', position_group=3),
    SequenceStep(notes=(('G', 12), ('D', 12), ('A', 14)), duration_ms=TON, chord_name='G_{12-14}', position_group=3),

    SequenceStep(notes=(('G', 12), ('D', 14), ('A', 15)), duration_ms=TON, chord_name='C_{12-15}', position_group=4),
    SequenceStep(notes=(('G', 14), ('D', 15), ('A', 15)), duration_ms=TON, chord_name='F_{14-15}', position_group=4),
    SequenceStep(notes=(('G', 16), ('D', 17), ('A', 17)), duration_ms=TON, chord_name='G_{16-17}', position_group=4),
]
PART3_NOTES = _display_notes(PART3_SEQUENCE)

part3 = Part(
    name="3. Strings A, D, G",
    background_notes=PART3_NOTES,
    play_sequence=PART3_SEQUENCE,
    highlight_chord_root=True,
    circle_sequence_elements=False,
    wrapping_distance=8,
    fillet_corners=True,
    fillet_radius=24,
    description="Play C-F-G in four ascending positions on the A, D, and G strings.",
)

# Part 4: D, A, low E. Four C-F-G groups on the bottom three strings.
PART4_SEQUENCE = [
    SequenceStep(notes=(('D', 2), ('A', 3), ('E', 3)), duration_ms=TON, chord_name='C_{2-3}', position_group=1),
    SequenceStep(notes=(('D', 3), ('A', 3), ('E', 5)), duration_ms=TON, chord_name='F_{3-5}', position_group=1),
    SequenceStep(notes=(('D', 5), ('A', 5), ('E', 7)), duration_ms=TON, chord_name='G_{5-7}', position_group=1),

    SequenceStep(notes=(('D', 5), ('A', 7), ('E', 8)), duration_ms=TON, chord_name='C_{5-8}', position_group=2),
    SequenceStep(notes=(('D', 7), ('A', 8), ('E', 8)), duration_ms=TON, chord_name='F_{7-8}', position_group=2),
    SequenceStep(notes=(('D', 9), ('A', 10), ('E', 10)), duration_ms=TON, chord_name='G_{9-10}', position_group=2),

    SequenceStep(notes=(('D', 10), ('A', 10), ('E', 12)), duration_ms=TON, chord_name='C_{10-12}', position_group=3),
    SequenceStep(notes=(('D', 10), ('A', 12), ('E', 13)), duration_ms=TON, chord_name='F_{10-13}', position_group=3),
    SequenceStep(notes=(('D', 12), ('A', 14), ('E', 15)), duration_ms=TON, chord_name='G_{12-15}', position_group=3),

    SequenceStep(notes=(('D', 14), ('A', 15), ('E', 15)), duration_ms=TON, chord_name='C_{14-15}', position_group=4),
    SequenceStep(notes=(('D', 15), ('A', 15), ('E', 17)), duration_ms=TON, chord_name='F_{15-17}', position_group=4),
    SequenceStep(notes=(('D', 17), ('A', 17), ('E', 19)), duration_ms=TON, chord_name='G_{17-19}', position_group=4),
]
PART4_NOTES = _display_notes(PART4_SEQUENCE)

part4 = Part(
    name="4. Strings E, A, D",
    background_notes=PART4_NOTES,
    play_sequence=PART4_SEQUENCE,
    highlight_chord_root=True,
    circle_sequence_elements=False,
    wrapping_distance=8,
    fillet_corners=True,
    fillet_radius=24,
    description="Play C-F-G in four ascending positions on the low E, A, and D strings.",
)

lesson = Lesson(
    name="C F G major triads",
    chord_label_title="Triad playing",
    parts=[part1, part2, part3, part4],
    description=(
        "Practice a I-IV-V progression in C major in four positions on each "
        "of the four adjacent three-string sets."
    ),
    difficulty="Beginner",
    metadata={
        'key': 'C',
        'tags': ['triads', 'C major', 'chord progression', 'barre chords', 'inversions'],
    },
)

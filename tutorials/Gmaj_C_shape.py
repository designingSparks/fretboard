"""Find G major triads across four string groups around the C-shape barre chord."""

from models.lesson_model import Lesson, Part
from models.sequence_step import SequenceStep

TON = 1000

# Full C-shape G major chord: x 10 9 7 8 7, from low E to high e.
# Barre at fret seven; the root is on the A string at fret ten.
PART1_NOTES = [
    ('A', 10),  # G
    ('D', 9),   # B
    ('G', 7),   # D
    ('B', 8),   # G
    ('e', 7),   # B
]

part1 = Part(
    name='Part 1: C-shape triads',
    background_notes=PART1_NOTES,
    play_sequence=[
        SequenceStep(notes=(('G', 7), ('B', 8), ('e', 7)),
                     duration_ms=TON, chord_name='G', shape='C'),
        SequenceStep(notes=(('D', 9), ('G', 7), ('B', 8)),
                     duration_ms=TON, chord_name='G', shape='C'),
        SequenceStep(notes=(('A', 10), ('D', 9), ('G', 7)),
                     duration_ms=TON, chord_name='G', shape='C'),
        SequenceStep(notes=(('E', 10), ('A', 10), ('D', 9)),
                     duration_ms=TON, chord_name='G', shape='C'),
    ],
    highlight_chord_root=True,
    description='Four G major triads from the top three strings to the bottom three strings around the C-shape barre chord.',
)

lesson = Lesson(
    name='G major: C-shape triads',
    parts=[part1],
    chord_label_title='Selected triad',
    description='Locate four three-string triads around the G major C-shape barre chord at fret seven.',
)

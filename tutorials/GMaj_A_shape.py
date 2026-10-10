"""Find G major triads across four string groups around the A-shape barre chord."""

from models.lesson_model import Lesson, Part
from models.sequence_step import SequenceStep

TON = 1000

# Full A-shape G major chord: x 10 12 12 12 10, from low E to high e.
# Barre at fret ten; the root is on the A string at fret ten.
PART1_NOTES = [
    ('A', 10),  # G
    ('D', 12),  # D
    ('G', 12),  # G
    ('B', 12),  # B
    ('e', 10),  # D
]

part1 = Part(
    name='Part 1: A-shape triads',
    background_notes=PART1_NOTES,
    play_sequence=[
        SequenceStep(notes=(('G', 12), ('B', 12), ('e', 10)),
                     duration_ms=TON, chord_name='G', shape='A'),
        SequenceStep(notes=(('D', 12), ('G', 12), ('B', 12)),
                     duration_ms=TON, chord_name='G', shape='A'),
        SequenceStep(notes=(('A', 14), ('D', 12), ('G', 12)),
                     duration_ms=TON, chord_name='G', shape='A'),
        SequenceStep(notes=(('E', 15), ('A', 14), ('D', 12)),
                     duration_ms=TON, chord_name='G', shape='A'),
    ],
    highlight_chord_root=True,
    description='Four G major triads from the top three strings to the bottom three strings around the A-shape barre chord.',
)

lesson = Lesson(
    name='G major: A-shape triads',
    parts=[part1],
    chord_label_title='Selected triad',
    description='Locate four three-string triads around the G major A-shape barre chord at fret ten.',
)

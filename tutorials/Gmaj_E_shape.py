"""Find G major triads across four string groups around the E-shape barre chord."""

from models.lesson_model import Lesson, Part
from models.background_layer import BackgroundLayer
from models.sequence_step import SequenceStep

TON = 1000

# Full E-shape G major chord: 355433, from low E to high e.
PART1_NOTES = [
    ('E', 3),  # G
    ('A', 5),  # D
    ('D', 5),  # G
    ('G', 4),  # B
    ('B', 3),  # D
    ('e', 3),  # G
]

# Playback notes outside the barre chord.
EXTRA_NOTES = [
    ('E', 7),  # B
]

part1 = Part(
    name='Part 1: E-shape triads',
    background_notes=PART1_NOTES,
    background_layers=[
        # Muted mid blue with the default grey background's brightness and opacity.
        BackgroundLayer(notes=EXTRA_NOTES, color='#91c2e6'),
    ],
    play_sequence=[
        SequenceStep(notes=(('G', 4), ('B', 3), ('e', 3)),
                     duration_ms=TON, chord_name='G', shape='E'),
        SequenceStep(notes=(('D', 5), ('G', 4), ('B', 3)),
                     duration_ms=TON, chord_name='G', shape='E'),
        SequenceStep(notes=(('A', 5), ('D', 5), ('G', 4)),
                     duration_ms=TON, chord_name='G', shape='E'),
        SequenceStep(notes=(('E', 7), ('A', 5), ('D', 5)),
                     duration_ms=TON, chord_name='G', shape='E'),
    ],
    highlight_chord_root=True,
    description='Four G major triads from the top three strings to the bottom three strings around the E-shape barre chord.',
)

lesson = Lesson(
    name='G major: E-shape triads',
    parts=[part1],
    chord_label_title='Selected triad',
    description='Locate four three-string triads around the G major E-shape barre chord at fret three.',
)

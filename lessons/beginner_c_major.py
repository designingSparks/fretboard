"""
Beginner C Major Lesson

This lesson teaches the C major scale in position 4 on the fretboard.
Students will practice ascending patterns with two different variations.
"""

from models.lesson_model import Part, Lesson
from models.sequence_step import SequenceStep
from scales import C_MAJOR_POS4_HIGHLIGHT

# ============================================================================
# PART 1: Position 4 - Ascending
# ============================================================================

TON = 500

PART1_SEQUENCE = [
    SequenceStep(notes=(('A', 3),), duration_ms=TON),
    SequenceStep(notes=(('A', 5),), duration_ms=TON),
    SequenceStep(notes=(('D', 2),), duration_ms=TON),
    SequenceStep(notes=(('D', 3),), duration_ms=TON),
    SequenceStep(notes=(('D', 5),), duration_ms=TON),
    SequenceStep(notes=(('G', 2),), duration_ms=TON),
    SequenceStep(notes=(('G', 4),), duration_ms=TON),
    SequenceStep(notes=(('G', 5),), duration_ms=TON),
]

part1 = Part(
    name="Position 4 - Ascending",
    background_notes=C_MAJOR_POS4_HIGHLIGHT,
    play_sequence=PART1_SEQUENCE,
    highlight_classes={'C': 'highlight1'},
    description='Start with your index finger on the 2nd fret'
)

# ============================================================================
# PART 2: Position 4 - Descending (custom sequence)
# ============================================================================

# Create a descending version by reversing the ascending sequence
DESCENDING_PLAY = [
    SequenceStep(notes=(('G', 5),), duration_ms=TON),
    SequenceStep(notes=(('G', 4),), duration_ms=TON),
    SequenceStep(notes=(('G', 2),), duration_ms=TON),
    SequenceStep(notes=(('D', 5),), duration_ms=TON),
    SequenceStep(notes=(('D', 3),), duration_ms=TON),
    SequenceStep(notes=(('D', 2),), duration_ms=TON),
    SequenceStep(notes=(('A', 5),), duration_ms=TON),
    SequenceStep(notes=(('A', 3),), duration_ms=TON),
]

part2 = Part(
    name="Position 4 - Descending",
    background_notes=C_MAJOR_POS4_HIGHLIGHT,
    play_sequence=DESCENDING_PLAY,
    highlight_classes={'C': 'highlight1'},
    description='Practice going back down the scale'
)

# ============================================================================
# LESSON
# ============================================================================

lesson = Lesson(
    name="Beginner C Major - Position 4",
    parts=[part1, part2],
    description=(
        "Learn the C major scale in position 4. "
        "Practice ascending and descending, focusing on clean note transitions "
        "and proper finger placement."
    ),
    author="LearnLeadFast",
    metadata={
        'tags': ['beginner', 'scales', 'C major', 'position 4'],
        'estimated_time_minutes': 10,
        'prerequisites': [],
    }
)

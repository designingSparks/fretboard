"""
Beginner C Major Lesson

This lesson teaches the C major scale in position 4 on the fretboard.
Students will practice ascending patterns with two different variations.
"""

from models.lesson_model import Part, Lesson
from scales import C_MAJOR_POS4_HIGHLIGHT, C_MAJOR_POS4_PLAY

# ============================================================================
# PART 1: Position 4 - Ascending
# ============================================================================

part1 = Part(
    name="Position 4 - Ascending",
    notes_to_highlight=C_MAJOR_POS4_HIGHLIGHT,
    play_sequence=C_MAJOR_POS4_PLAY,
    highlight_classes={'C': 'highlight1'},
    description='Start with your index finger on the 2nd fret'
)

# ============================================================================
# PART 2: Position 4 - Descending (custom sequence)
# ============================================================================

TON = 500

# Create a descending version by reversing the ascending sequence
DESCENDING_PLAY = [
    [('G', 5), TON],
    [('G', 4), TON],
    [('G', 2), TON],
    [('D', 5), TON],
    [('D', 3), TON],
    [('D', 2), TON],
    [('A', 5), TON],
    [('A', 3), TON],
]

part2 = Part(
    name="Position 4 - Descending",
    notes_to_highlight=C_MAJOR_POS4_HIGHLIGHT,
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

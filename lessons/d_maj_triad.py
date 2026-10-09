"""
D major triads on 3 adjacent strings at a time, starting from the top 3 strings and ending on the bottom 3 strings.
Plays the first four triads horizontally, starting from the triad closest to the guitar nut.
"""

from models.lesson_model import Part, Lesson
from models.sequence_step import SequenceStep
TON = 1000  # Default note duration in milliseconds

# ============================================================================
# Part 1: Top 3 strings, G, B, e
# ============================================================================
PART1_NOTES = [
    ('e', 2), ('e', 5), ('e', 10), ('e', 14),
    ('B', 3), ('B', 7), ('B', 10), ('B', 15),
    ('G', 2), ('G', 7), ('G', 11), ('G', 14),
]
PART1_SEQUENCE = [
    SequenceStep(notes=(('e', 2), ('B', 3), ('G', 2)), duration_ms=TON),
    SequenceStep(notes=(('e', 5), ('B', 7), ('G', 7)), duration_ms=TON),
    SequenceStep(notes=(('e', 10), ('B', 10), ('G', 11)), duration_ms=TON),
    SequenceStep(notes=(('e', 14), ('B', 15), ('G', 14)), duration_ms=TON),
]
part1 = Part(
    name="Strings G, B, e",
    notes_to_highlight=PART1_NOTES,
    play_sequence=PART1_SEQUENCE,
    highlight_classes={'D': 'highlight1'},  # Highlight root note
    description='',
)

# ============================================================================
# Part 2: Strings D, G, B
# ============================================================================
PART2_NOTES = [
    ('B', 3), ('B', 7), ('B', 10), ('B', 15),
    ('G', 2), ('G', 7), ('G', 11), ('G', 14),
    ('D', 4), ('D', 7), ('D', 12), ('D', 16)
]
PART2_SEQUENCE = [
    SequenceStep(notes=(('B', 3), ('G', 2), ('D', 4)), duration_ms=TON),
    SequenceStep(notes=(('B', 7), ('G', 7), ('D', 7)), duration_ms=TON),
    SequenceStep(notes=(('B', 10), ('G', 11), ('D', 12)), duration_ms=TON),
    SequenceStep(notes=(('B', 15), ('G', 14), ('D', 16)), duration_ms=TON),
]
part2 = Part(
    name="Strings D, G, B",
    notes_to_highlight=PART2_NOTES,
    play_sequence=PART2_SEQUENCE,
    highlight_classes={'D': 'highlight1'},
    description='',
)

# ============================================================================
# Part 3: Strings A, D, G
# ============================================================================
PART3_NOTES = [
    ('G', 2), ('G', 7), ('G', 11), ('G', 14),
    ('D', 4), ('D', 7), ('D', 12), ('D', 16),
    ('A', 5), ('A', 9), ('A', 12), ('A', 17)
]
PART3_SEQUENCE = [
    SequenceStep(notes=(('G', 2), ('D', 4), ('A', 5)), duration_ms=TON),
    SequenceStep(notes=(('G', 7), ('D', 7), ('A', 9)), duration_ms=TON),
    SequenceStep(notes=(('G', 11), ('D', 12), ('A', 12)), duration_ms=TON),
    SequenceStep(notes=(('G', 14), ('D', 16), ('A', 17)), duration_ms=TON),
]
part3 = Part(
    name="Strings A, D, G",
    notes_to_highlight=PART3_NOTES,
    play_sequence=PART3_SEQUENCE,
    highlight_classes={'D': 'highlight1'},
    description='',
)

# ============================================================================
# Part 4: Strings E, A, D
# ============================================================================
PART4_NOTES = [
    ('D', 0), ('D', 4), ('D', 7), ('D', 12),
    ('A', 0), ('A', 5), ('A', 9), ('A', 12),
    ('E', 2), ('E', 5), ('E', 10), ('E', 14)
]
PART4_SEQUENCE = [
    SequenceStep(notes=(('D', 0), ('A', 0), ('E', 2)), duration_ms=TON),
    SequenceStep(notes=(('D', 4), ('A', 5), ('E', 5)), duration_ms=TON),
    SequenceStep(notes=(('D', 7), ('A', 9), ('E', 10)), duration_ms=TON),
    SequenceStep(notes=(('D', 12), ('A', 12), ('E', 14)), duration_ms=TON),
]
part4 = Part(
    name="Strings E, A, D",
    notes_to_highlight=PART4_NOTES,
    play_sequence=PART4_SEQUENCE,
    highlight_classes={'D': 'highlight1'},
    description='',
)


# ============================================================================
# LESSON - Combine parts into a lesson
# ============================================================================

# REQUIRED: Export a 'lesson' variable
lesson = Lesson(
    name="D major triads",
    parts=[part1, part2, part3, part4],
    description="Learn D major triads across 3 adjacent strings, moving from high to low strings",
    author="Your Name",
    metadata={
        'tags': ['beginner', 'triads', 'D major'],
        'estimated_time_minutes': 10,
    }
)
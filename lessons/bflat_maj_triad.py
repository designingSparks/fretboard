"""
Bb major triads on 3 adjacent strings at a time, starting from the top 3 strings and ending on the bottom 3 strings.
"""

from models.lesson_model import Part, Lesson
from models.sequence_step import SequenceStep
TON = 1000  # Default note duration in milliseconds

# ============================================================================
# Part 1: Top 3 strings, G, B, e
# ============================================================================
PART1_NOTES = [
    ('e', 1), ('e', 6), ('e', 10), ('e', 13),
    ('B', 3), ('B', 6), ('B', 11), ('B', 15),
    ('G', 3), ('G', 7), ('G', 10), ('G', 15)
]
PART1_SEQUENCE = [
    SequenceStep(notes=(('e', 1), ('B', 3), ('G', 3)), duration_ms=TON),
    SequenceStep(notes=(('e', 6), ('B', 6), ('G', 7)), duration_ms=TON),
    SequenceStep(notes=(('e', 10), ('B', 11), ('G', 10)), duration_ms=TON),
    SequenceStep(notes=(('e', 13), ('B', 15), ('G', 15)), duration_ms=TON)
]
part1 = Part(
    name="Strings G, B, e",
    background_notes=PART1_NOTES,
    play_sequence=PART1_SEQUENCE,
    highlight_classes={'Bb': 'highlight1'},  # Highlight root note (Bb = A#)
    description='',
)

# ============================================================================
# Part 2: Strings D, G, B
# ============================================================================
PART2_NOTES = [
    ('B', 3), ('B', 6), ('B', 11), ('B', 15),
    ('G', 3), ('G', 7), ('G', 10), ('G', 15),
    ('D', 3), ('D', 8), ('D', 12), ('D', 15)
]
PART2_SEQUENCE = [
    SequenceStep(notes=(('B', 3), ('G', 3), ('D', 3)), duration_ms=TON),
    SequenceStep(notes=(('B', 6), ('G', 7), ('D', 8)), duration_ms=TON),
    SequenceStep(notes=(('B', 11), ('G', 10), ('D', 12)), duration_ms=TON),
    SequenceStep(notes=(('B', 15), ('G', 15), ('D', 15)), duration_ms=TON)
]
part2 = Part(
    name="Strings D, G, B",
    background_notes=PART2_NOTES,
    play_sequence=PART2_SEQUENCE,
    highlight_classes={'Bb': 'highlight1'},
    description='',
)

# ============================================================================
# Part 3: Strings A, D, G
# ============================================================================
PART3_NOTES = [
    ('A', 5), ('A', 8), ('A', 13), ('A', 17),
    ('D', 3), ('D', 8), ('D', 12), ('D', 15),
    ('G', 3), ('G', 7), ('G', 10), ('G', 15)
]
PART3_SEQUENCE = [
    SequenceStep(notes=(('A', 5), ('D', 3), ('G', 3)), duration_ms=TON),
    SequenceStep(notes=(('A', 8), ('D', 8), ('G', 7)), duration_ms=TON),
    SequenceStep(notes=(('A', 13), ('D', 12), ('G', 10)), duration_ms=TON),
    SequenceStep(notes=(('A', 17), ('D', 15), ('G', 15)), duration_ms=TON)
]
part3 = Part(
    name="Strings A, D, G",
    background_notes=PART3_NOTES,
    play_sequence=PART3_SEQUENCE,
    highlight_classes={'Bb': 'highlight1'},
    description='',
)

# ============================================================================
# Part 4: Strings E, A, D
# ============================================================================
PART4_NOTES = [
    ('E', 1), ('E', 6), ('E', 10), ('E', 13),
    ('A', 1), ('A', 5), ('A', 8), ('A', 13),
    ('D', 0), ('D', 3), ('D', 8), ('D', 12)
]
PART4_SEQUENCE = [
    SequenceStep(notes=(('E', 1), ('A', 1), ('D', 0)), duration_ms=TON),
    SequenceStep(notes=(('E', 6), ('A', 5), ('D', 3)), duration_ms=TON),
    SequenceStep(notes=(('E', 10), ('A', 8), ('D', 8)), duration_ms=TON),
    SequenceStep(notes=(('E', 13), ('A', 13), ('D', 12)), duration_ms=TON)
]
part4 = Part(
    name="Strings E, A, D",
    background_notes=PART4_NOTES,
    play_sequence=PART4_SEQUENCE,
    highlight_classes={'Bb': 'highlight1'},
    description='',
)


# ============================================================================
# LESSON - Combine parts into a lesson
# ============================================================================

# REQUIRED: Export a 'lesson' variable
lesson = Lesson(
    name="Bb major triads",
    parts=[part1, part2, part3, part4],
    description="Learn Bb major triads across 3 adjacent strings, moving from high to low strings",
    author="Your Name",
    use_sharp=False,
    metadata={
        'tags': ['beginner', 'triads', 'Bb major'],
        'estimated_time_minutes': 10,
    }
)

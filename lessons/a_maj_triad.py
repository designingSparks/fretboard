"""
A major triads on 3 adjacent strings at a time, starting from the top 3 strings and ending on the bottom 3 strings.
Plays the first four triads horizontally, starting from the triad closest to the guitar nut.
"""

from models.lesson_model import Part, Lesson
TON = 1000  # Default note duration in milliseconds

# ============================================================================
# Part 1: Top 3 strings, G, B, e
# ============================================================================
PART1_NOTES = [
    ('e', 0), ('e', 5), ('e', 9), ('e', 12),
    ('B', 2), ('B', 5), ('B', 10), ('B', 14),
    ('G', 2), ('G', 6), ('G', 9), ('G', 14),
]
PART1_SEQUENCE = [
    [('e', 0), ('B', 2), ('G', 2), TON],
    [('e', 5), ('B', 5), ('G', 6), TON],
    [('e', 9), ('B', 10), ('G', 9), TON],
    [('e', 12), ('B', 14), ('G', 14), TON],
]
part1 = Part(
    name="Strings G, B, e",
    notes_to_highlight=PART1_NOTES,
    play_sequence=PART1_SEQUENCE,
    highlight_classes={'A': 'highlight1'},  # Highlight root note
    description='',
)

# ============================================================================
# Part 2: Strings D, G, B
# ============================================================================
PART2_NOTES = [
    ('B', 2), ('B', 5), ('B', 10), ('B', 14),
    ('G', 2), ('G', 6), ('G', 9), ('G', 14),
    ('D', 2), ('D', 7), ('D', 11), ('D', 14)
]
PART2_SEQUENCE = [
    [('B', 2), ('G', 2), ('D', 2), TON],
    [('B', 5), ('G', 6), ('D', 7), TON],
    [('B', 10), ('G', 9), ('D', 11), TON],
    [('B', 14), ('G', 14), ('D', 14), TON],
]
part2 = Part(
    name="Strings D, G, B",
    notes_to_highlight=PART2_NOTES,
    play_sequence=PART2_SEQUENCE,
    highlight_classes={'A': 'highlight1'},
    description='',
)

# ============================================================================
# Part 3: Strings A, D, G
# ============================================================================
PART3_NOTES = [
    ('G', 2), ('G', 6), ('G', 9), ('G', 14),
    ('D', 2), ('D', 7), ('D', 11), ('D', 14),
    ('A', 4), ('A', 7), ('A', 12), ('A', 16)
]
PART3_SEQUENCE = [
    [('G', 2), ('D', 2), ('A', 4), TON],
    [('G', 6), ('D', 7), ('A', 7), TON],
    [('G', 9), ('D', 11), ('A', 12), TON],
    [('G', 14), ('D', 14), ('A', 16), TON],
]
part3 = Part(
    name="Strings A, D, G",
    notes_to_highlight=PART3_NOTES,
    play_sequence=PART3_SEQUENCE,
    highlight_classes={'A': 'highlight1'},
    description='',
)

# ============================================================================
# Part 4: Strings E, A, D
# ============================================================================
PART4_NOTES = [
    ('D', 2), ('D', 7), ('D', 11), ('D', 14),
    ('A', 4), ('A', 7), ('A', 12), ('A', 16),
    ('E', 5), ('E', 9), ('E', 12), ('E', 17)
]
PART4_SEQUENCE = [
    [('D', 2), ('A', 4), ('E', 5), TON],
    [('D', 7), ('A', 7), ('E', 9), TON],
    [('D', 11), ('A', 12), ('E', 12), TON],
    [('D', 14), ('A', 16), ('E', 17), TON],
]
part4 = Part(
    name="Strings E, A, D",
    notes_to_highlight=PART4_NOTES,
    play_sequence=PART4_SEQUENCE,
    highlight_classes={'A': 'highlight1'},
    description='',
)


# ============================================================================
# LESSON - Combine parts into a lesson
# ============================================================================

# REQUIRED: Export a 'lesson' variable
lesson = Lesson(
    name="A major triads",
    parts=[part1, part2, part3, part4],
    description="Learn A major triads across 3 adjacent strings, moving from high to low strings",
    author="Your Name",
    metadata={
        'tags': ['beginner', 'triads', 'A major'],
        'estimated_time_minutes': 10,
    }
)
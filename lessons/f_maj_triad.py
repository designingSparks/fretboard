"""
F major triads on 3 adjacent strings at a time, starting from the top 3 strings and ending on the bottom 3 strings.
"""

from models.lesson_model import Part, Lesson
TON = 1000  # Default note duration in milliseconds

# ============================================================================
# Part 1: Top 3 strings, G, B, e
# ============================================================================
PART1_NOTES = [
    ('e', 1), ('e', 5), ('e', 8), ('e', 13),
    ('B', 1), ('B', 6), ('B', 10), ('B', 13),
    ('G', 2), ('G', 5), ('G', 10), ('G', 14),
]
PART1_SEQUENCE = [
    [('e', 1), ('B', 1), ('G', 2), TON],
    [('e', 5), ('B', 6), ('G', 5), TON],
    [('e', 8), ('B', 10), ('G', 10), TON],
    [('e', 13), ('B', 13), ('G', 14), TON]
]
part1 = Part(
    name="Strings G, B, e",
    notes_to_highlight=PART1_NOTES,
    play_sequence=PART1_SEQUENCE,
    highlight_classes={'F': 'highlight1'},  # Highlight root note
    description='',
)

# ============================================================================
# Part 2: Strings D, G, B
# ============================================================================
PART2_NOTES = [
    ('B', 1), ('B', 6), ('B', 10), ('B', 13),
    ('G', 2), ('G', 5), ('G', 10), ('G', 14),
    ('D', 3), ('D', 7), ('D', 10), ('D', 15)
]
PART2_SEQUENCE = [
    [('B', 1), ('G', 2), ('D', 3), TON],
    [('B', 6), ('G', 5), ('D', 7), TON],
    [('B', 10), ('G', 10), ('D', 10), TON],
    [('B', 13), ('G', 14), ('D', 15), TON]
]
part2 = Part(
    name="Strings D, G, B",
    notes_to_highlight=PART2_NOTES,
    play_sequence=PART2_SEQUENCE,
    highlight_classes={'F': 'highlight1'},
    description='',
)

# ============================================================================
# Part 3: Strings A, D, G
# ============================================================================
PART3_NOTES = [
    ('G', 2), ('G', 5), ('G', 10), ('G', 14),
    ('D', 3), ('D', 7), ('D', 10), ('D', 15),
    ('A', 3), ('A', 8), ('A', 12), ('A', 15)
]
PART3_SEQUENCE = [
    [('G', 2), ('D', 3), ('A', 3), TON],
    [('G', 5), ('D', 7), ('A', 8), TON],
    [('G', 10), ('D', 10), ('A', 12), TON],
    [('G', 14), ('D', 15), ('A', 15), TON]
]
part3 = Part(
    name="Strings A, D, G",
    notes_to_highlight=PART3_NOTES,
    play_sequence=PART3_SEQUENCE,
    highlight_classes={'F': 'highlight1'},
    description='',
)

# ============================================================================
# Part 4: Strings E, A, D
# ============================================================================
PART4_NOTES = [
    ('D', 3), ('D', 7), ('D', 10), ('D', 15),
    ('A', 3), ('A', 8), ('A', 12), ('A', 15),
    ('E', 5), ('E', 8), ('E', 13), ('E', 17)
]
PART4_SEQUENCE = [
    [('D', 3), ('A', 3), ('E', 5), TON],
    [('D', 7), ('A', 8), ('E', 8), TON],
    [('D', 10), ('A', 12), ('E', 13), TON],
    [('D', 15), ('A', 15), ('E', 17), TON]
]
part4 = Part(
    name="Strings E, A, D",
    notes_to_highlight=PART4_NOTES,
    play_sequence=PART4_SEQUENCE,
    highlight_classes={'F': 'highlight1'},
    description='',
)


# ============================================================================
# LESSON - Combine parts into a lesson
# ============================================================================

# REQUIRED: Export a 'lesson' variable
lesson = Lesson(
    name="F major triads",
    parts=[part1, part2, part3, part4],
    description="Learn F major triads across 3 adjacent strings, moving from high to low strings",
    author="Your Name",
    metadata={
        'tags': ['beginner', 'triads', 'F major'],
        'estimated_time_minutes': 10,
    }
)

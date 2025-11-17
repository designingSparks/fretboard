"""
G major triads on 3 adjacent strings at a time, starting from the top 3 strings and ending on the bottom 3 strings.
"""

from models.lesson_model import Part, Lesson
TON = 1000  # Default note duration in milliseconds

# ============================================================================
# Part 1: Top 3 strings, G, B, e
# ============================================================================
PART1_NOTES = [
    ('e', 3), ('e', 7), ('e', 10), ('e', 15),
    ('B', 3), ('B', 8), ('B', 12), ('B', 15), 
    ('G', 4), ('G', 7), ('G', 12), ('G', 16),
]
PART1_SEQUENCE = [
    [('e', 3), ('B', 3), ('G', 4), TON],
    [('e', 7), ('B', 8), ('G', 7), TON],
    [('e', 10), ('B', 12), ('G', 12), TON],
    [('e', 15), ('B', 15), ('G', 16), TON]
]
part1 = Part(
    name="Strings G, B, e",
    notes_to_highlight=PART1_NOTES,
    play_sequence=PART1_SEQUENCE,
    highlight_classes={'G': 'highlight1'},  # Highlight root note
    description='',
)

# ============================================================================
# Part 2: Strings D, G, B
# ============================================================================
PART2_NOTES = [
    ('B', 0), ('B', 3), ('B', 8), ('B', 12),
    ('G', 0), ('G', 4), ('G', 7), ('G', 12),
    ('D', 0), ('D', 5), ('D', 9), ('D', 12)
]
PART2_SEQUENCE = [
    [('B', 0), ('G', 0), ('D', 0), TON],
    [('B', 3), ('G', 4), ('D', 5), TON],
    [('B', 8), ('G', 7), ('D', 9), TON],
    [('B', 12), ('G', 12), ('D', 12), TON]
]
part2 = Part(
    name="Strings D, G, B",
    notes_to_highlight=PART2_NOTES,
    play_sequence=PART2_SEQUENCE,
    highlight_classes={'G': 'highlight1'},
    description='',
)

# ============================================================================
# Part 3: Strings A, D, G
# ============================================================================
PART3_NOTES = [
    ('G', 0), ('G', 4), ('G', 7), ('G', 12),
    ('D', 0), ('D', 5), ('D', 9), ('D', 12),
    ('A', 2), ('A', 5), ('A', 10), ('A', 14)
]
PART3_SEQUENCE = [
    [('G', 0), ('D', 0), ('A', 2), TON],
    [('G', 4), ('D', 5), ('A', 5), TON],
    [('G', 7), ('D', 9), ('A', 10), TON],
    [('G', 12), ('D', 12), ('A', 14), TON]
]
part3 = Part(
    name="Strings A, D, G",
    notes_to_highlight=PART3_NOTES,
    play_sequence=PART3_SEQUENCE,
    highlight_classes={'G': 'highlight1'},
    description='',
)

# ============================================================================
# Part 4: Strings E, A, D
# ============================================================================
PART4_NOTES = [
    ('D', 0), ('D', 5), ('D', 9), ('D', 12),
    ('A', 2), ('A', 5), ('A', 10), ('A', 14),
    ('E', 3), ('E', 7), ('E', 10), ('E', 15)
]
PART4_SEQUENCE = [
    [('D', 0), ('A', 2), ('E', 3), TON],
    [('D', 5), ('A', 5), ('E', 7), TON],
    [('D', 9), ('A', 10), ('E', 10), TON],
    [('D', 12), ('A', 14), ('E', 15), TON]
]
part4 = Part(
    name="Strings E, A, D",
    notes_to_highlight=PART4_NOTES,
    play_sequence=PART4_SEQUENCE,
    highlight_classes={'G': 'highlight1'},
    description='',
)


# ============================================================================
# LESSON - Combine parts into a lesson
# ============================================================================

# REQUIRED: Export a 'lesson' variable
lesson = Lesson(
    name="G major triads",
    parts=[part1, part2, part3, part4],
    description="Learn G major triads across 3 adjacent strings, moving from high to low strings",
    author="Your Name",
    metadata={
        'tags': ['beginner', 'triads', 'G major'],
        'estimated_time_minutes': 10,
    }
)
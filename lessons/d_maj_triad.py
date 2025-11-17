"""
D major triads on 3 adjacent strings at a time, starting from the top 3 strings and ending on the bottom 3 strings.
"""

from models.lesson_model import Part, Lesson
TON = 1000  # Default note duration in milliseconds

# ============================================================================
# Part 1: Top 3 strings, G, B, e
# ============================================================================
PART1_NOTES = [
    ('e', 2), ('e', 5), ('e', 10), 
    ('B', 3), ('B', 7), ('B', 10), 
    ('G', 2), ('G', 7), ('G', 11), 
]
PART1_SEQUENCE = [
    [('e', 2), ('B', 3), ('G', 2), TON],
    [('e', 5), ('B', 7), ('G', 7), TON],
    [('e', 10), ('B', 10), ('G', 11), TON],
    # [('e', 14), ('B', 15), ('G', 14), TON]
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
    ('B', 3), ('B', 7), ('B', 10), 
    ('G', 2), ('G', 7), ('G', 11),
    ('D', 4), ('D', 7), ('D', 12)
]
PART2_SEQUENCE = [
    [('B', 3), ('G', 2), ('D', 4), TON],
    [('B', 7), ('G', 7), ('D', 7), TON],
    [('B', 10), ('G', 11), ('D', 12), TON],
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
    ('G', 2), ('G', 7), ('G', 11),
    ('D', 4), ('D', 7), ('D', 12),
    ('A', 5), ('A', 9), ('A', 12)
]
PART3_SEQUENCE = [
    [('G', 2), ('D', 4), ('A', 5), TON],
    [('G', 7), ('D', 7), ('A', 9), TON],
    [('G', 11), ('D', 12), ('A', 12), TON],
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
    ('D', 0), ('D', 4), ('D', 7), 
    ('A', 0), ('A', 5), ('A', 9), 
    ('E', 2), ('E', 5), ('E', 10)
]
PART4_SEQUENCE = [
    [('D', 0), ('A', 0), ('E', 2), TON],
    [('D', 4), ('A', 5), ('E', 5), TON],
    [('D', 7), ('A', 9), ('E', 10), TON],
    # [('D', 12), ('A', 12), ('E', 14), TON]
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
"""
E major triads on 3 adjacent strings at a time, starting from the top 3 strings and ending on the bottom 3 strings.
Plays the first four triads horizontally, starting from the triad closest to the guitar nut.
"""

from models.lesson_model import Part, Lesson
TON = 1000  # Default note duration in milliseconds

# ============================================================================
# Part 1: Top 3 strings, G, B, e
# ============================================================================
PART1_NOTES = [
    ('e', 0), ('e', 4), ('e', 7), ('e', 12),
    ('B', 0), ('B', 5), ('B', 9), ('B', 12),
    ('G', 1), ('G', 4), ('G', 9), ('G', 13),
]
PART1_SEQUENCE = [
    [('e', 0), ('B', 0), ('G', 1), TON],
    [('e', 4), ('B', 5), ('G', 4), TON],
    [('e', 7), ('B', 9), ('G', 9), TON],
    [('e', 12), ('B', 12), ('G', 13), TON],
]
part1 = Part(
    name="Strings G, B, e",
    notes_to_highlight=PART1_NOTES,
    play_sequence=PART1_SEQUENCE,
    highlight_classes={'E': 'highlight1'},  # Highlight root note
    description='',
)

# ============================================================================
# Part 2: Strings D, G, B
# ============================================================================
PART2_NOTES = [
    ('B', 0), ('B', 5), ('B', 9), ('B', 12),
    ('G', 1), ('G', 4), ('G', 9), ('G', 13),
    ('D', 2), ('D', 6), ('D', 9), ('D', 14)
]
PART2_SEQUENCE = [
    [('B', 0), ('G', 1), ('D', 2), TON],
    [('B', 5), ('G', 4), ('D', 6), TON],
    [('B', 9), ('G', 9), ('D', 9), TON],
    [('B', 12), ('G', 13), ('D', 14), TON],
]
part2 = Part(
    name="Strings D, G, B",
    notes_to_highlight=PART2_NOTES,
    play_sequence=PART2_SEQUENCE,
    highlight_classes={'E': 'highlight1'},
    description='',
)

# ============================================================================
# Part 3: Strings A, D, G
# ============================================================================
PART3_NOTES = [
    ('G', 1), ('G', 4), ('G', 9), ('G', 13),
    ('D', 2), ('D', 6), ('D', 9), ('D', 14),
    ('A', 2), ('A', 7), ('A', 11), ('A', 14)
]
PART3_SEQUENCE = [
    [('G', 1), ('D', 2), ('A', 2), TON],
    [('G', 4), ('D', 6), ('A', 7), TON],
    [('G', 9), ('D', 9), ('A', 11), TON],
    [('G', 13), ('D', 14), ('A', 14), TON],
]
part3 = Part(
    name="Strings A, D, G",
    notes_to_highlight=PART3_NOTES,
    play_sequence=PART3_SEQUENCE,
    highlight_classes={'E': 'highlight1'},
    description='',
)

# ============================================================================
# Part 4: Strings E, A, D
# ============================================================================
PART4_NOTES = [
    ('D', 2), ('D', 6), ('D', 9), ('D', 14),
    ('A', 2), ('A', 7), ('A', 11), ('A', 14),
    ('E', 4), ('E', 7), ('E', 12), ('E', 16)
]
PART4_SEQUENCE = [
    [('D', 2), ('A', 2), ('E', 4), TON],
    [('D', 6), ('A', 7), ('E', 7), TON],
    [('D', 9), ('A', 11), ('E', 12), TON],
    [('D', 14), ('A', 14), ('E', 16), TON],
]
part4 = Part(
    name="Strings E, A, D",
    notes_to_highlight=PART4_NOTES,
    play_sequence=PART4_SEQUENCE,
    highlight_classes={'E': 'highlight1'},
    description='',
)


# ============================================================================
# LESSON - Combine parts into a lesson
# ============================================================================

# REQUIRED: Export a 'lesson' variable
lesson = Lesson(
    name="E major triads",
    parts=[part1, part2, part3, part4],
    description="Learn E major triads across 3 adjacent strings, moving from high to low strings",
    author="Your Name",
    use_sharp=True,  # Display notes with flat notation (Db, Gb, Ab) - demonstrates flat notation
    metadata={
        'tags': ['beginner', 'triads', 'E major'],
        'estimated_time_minutes': 10,
    }
)
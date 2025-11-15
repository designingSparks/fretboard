""" 
C major triads on 3 adjacent strings at a time, starting from the top 3 strings and ending on the bottom 3 strings.
"""

from models.lesson_model import Part, Lesson
TON = 1000  # Default note duration in milliseconds

# ============================================================================
# Top 3 strings, G, B, E up to 13th fret
# ============================================================================
PART1_NOTES = [
    ('e', 0), ('e', 3), ('e', 8), ('e', 12),
    ('B', 1), ('B', 5), ('B', 8), ('B', 13),
    ('G', 0), ('G', 5), ('G', 9), ('G', 12)
]
PART1_SEQUENCE = [
    [('e', 0), ('B', 1), ('G', 0), TON],
    [('e', 3), ('B', 5), ('G', 5), TON],
    [('e', 8), ('B', 8), ('G', 9), TON],
    [('e', 12), ('B', 13), ('G', 12), TON]
]  
part1 = Part(
    name="Strings G, B, e",
    notes_to_highlight=PART1_NOTES,
    play_sequence=PART1_SEQUENCE,
    highlight_classes={'C': 'highlight1'},  # Optional: highlight specific notes
    description='',
)

PART2_NOTES = [
    ('B', 1), ('B', 5), ('B', 8), ('B', 13),
    ('G', 0), ('G', 5), ('G', 9), ('G', 12),
    ('D', 2), ('D', 5), ('D', 10), ('D', 14)
]
PART2_SEQUENCE = [
    [('B', 1), ('G', 0), ('D', 2), TON],
    [('B', 5), ('G', 5), ('D', 5), TON],
    [('B', 8), ('G', 9), ('D', 10), TON],
    [('B', 13), ('G', 12), ('D', 14), TON]
]  
part2 = Part(
    name="Strings D, G, B",
    notes_to_highlight=PART2_NOTES,
    play_sequence=PART2_SEQUENCE,
    highlight_classes={'C': 'highlight1'},  # Optional: highlight specific notes
    description='',
)

# ============================================================================
# Part 3: Strings A, D, G
# ============================================================================
PART3_NOTES = [
    ('A', 3), ('A', 7), ('A', 10), ('A', 15),
    ('D', 2), ('D', 5), ('D', 10), ('D', 14),
    ('G', 0), ('G', 5), ('G', 9), ('G', 12)
]
PART3_SEQUENCE = [
    [('A', 3), ('D', 2), ('G', 0), TON],
    [('A', 7), ('D', 5), ('G', 5), TON],
    [('A', 10), ('D', 10), ('G', 9), TON],
    [('A', 15), ('D', 14), ('G', 12), TON]
]
part3 = Part(
    name="Strings A, D, G",
    notes_to_highlight=PART3_NOTES,
    play_sequence=PART3_SEQUENCE,
    highlight_classes={'C': 'highlight1'},
    description='',
)

# ============================================================================
# Part 4: Strings E, A, D
# ============================================================================
PART4_NOTES = [
    ('E', 3), ('E', 8), ('E', 12), ('E', 15),
    ('A', 3), ('A', 7), ('A', 10), ('A', 15),
    ('D', 2), ('D', 5), ('D', 10), ('D', 14)
]
PART4_SEQUENCE = [
    [('E', 3), ('A', 3), ('D', 2), TON],
    [('E', 8), ('A', 7), ('D', 5), TON],
    [('E', 12), ('A', 10), ('D', 10), TON],
    [('E', 15), ('A', 15), ('D', 14), TON]
]
part4 = Part(
    name="Strings E, A, D",
    notes_to_highlight=PART4_NOTES,
    play_sequence=PART4_SEQUENCE,
    highlight_classes={'C': 'highlight1'},
    description='',
)


# ============================================================================
# LESSON - Combine parts into a lesson
# ============================================================================

# REQUIRED: Export a 'lesson' variable
lesson = Lesson(
    name="C major triads",
    parts=[part1, part2, part3, part4],  # Add all your parts here
    description="A detailed description of what this lesson teaches",
    author="Your Name",
    metadata={
        'tags': ['beginner', 'scales', 'C major'],
        'estimated_time_minutes': 10,
    }
)

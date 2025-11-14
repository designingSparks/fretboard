"""
Lesson Template - Copy this file to create your own lessons

Instructions:
1. Copy this file to a new name (e.g., my_custom_lesson.py)
2. Modify the note sequences below
3. Update part names and metadata
4. The lesson will be automatically discovered

Note Format:
- String names: 'e' (high), 'B', 'G', 'D', 'A', 'E' (low)
- Fret numbers: 0-24 (0 = open string)
- Tuples: (string_name, fret_number)
- Duration: milliseconds (e.g., 500 = half second)
"""

from models.lesson_model import Part, Lesson

# ============================================================================
# CONFIGURATION
# ============================================================================

TON = 500  # Default note duration in milliseconds

# ============================================================================
# PART 1 - Define your first part here
# ============================================================================

# Notes to display on the fretboard (shown in grey/inactive state)
# These are all the notes available in this position/scale
PART1_HIGHLIGHT = [
    ('e', 3), ('e', 5),  # High e string, frets 3 and 5
    ('B', 3), ('B', 5), ('B', 6),
    ('G', 2), ('G', 4), ('G', 5),
    ('D', 2), ('D', 3), ('D', 5),
    ('A', 2), ('A', 3), ('A', 5),
    ('E', 3), ('E', 5),  # Low E string, frets 3 and 5
]

# Sequence of notes to actually play
# Format for single notes: [[note_tuple, duration], ...]
PART1_PLAY = [
    [('A', 3), TON],  # A string, 3rd fret, hold for TON milliseconds
    [('A', 5), TON],
    [('D', 2), TON],
    [('D', 3), TON],
    [('D', 5), TON],
    [('G', 2), TON],
    [('G', 4), TON],
    [('G', 5), TON],
]

# For chords/triads, include multiple notes in one step:
# PART1_PLAY = [
#     [('e', 0), ('B', 1), ('G', 0), 1000],  # Play these 3 notes together
#     [('e', 3), ('B', 5), ('G', 5), 1000],  # Then these 3
# ]

# Create the Part object
part1 = Part(
    name="Part 1: Your Description Here",
    notes_to_highlight=PART1_HIGHLIGHT,
    play_sequence=PART1_PLAY,
    highlight_classes={'C': 'highlight1'},  # Optional: highlight specific notes
    metadata={
        'difficulty': 'beginner',  # beginner, intermediate, advanced
        'tempo_bpm': 60,
        'notes': 'Practice slowly at first'
    }
)

# ============================================================================
# PART 2 - Add more parts as needed
# ============================================================================

PART2_HIGHLIGHT = [
    ('e', 8), ('e', 10),
    ('B', 8), ('B', 10),
    # ... add more notes
]

PART2_PLAY = [
    [('e', 8), TON],
    [('e', 10), TON],
    # ... add more notes
]

part2 = Part(
    name="Part 2: Your Description Here",
    notes_to_highlight=PART2_HIGHLIGHT,
    play_sequence=PART2_PLAY,
)

# ============================================================================
# LESSON - Combine parts into a lesson
# ============================================================================

# REQUIRED: Export a 'lesson' variable
lesson = Lesson(
    name="My Custom Lesson",
    parts=[part1, part2],  # Add all your parts here
    description="A detailed description of what this lesson teaches",
    author="Your Name",
    metadata={
        'tags': ['beginner', 'scales', 'C major'],
        'estimated_time_minutes': 10,
    }
)

# ============================================================================
# ALTERNATIVE 1: Import existing scales/triads
# ============================================================================

# Instead of defining notes inline, you can import from scales.py:
#
# from scales import C_MAJOR_POS4_HIGHLIGHT, C_MAJOR_POS4_PLAY
#
# part1 = Part(
#     name="Position 4",
#     notes_to_highlight=C_MAJOR_POS4_HIGHLIGHT,
#     play_sequence=C_MAJOR_POS4_PLAY
# )

# ============================================================================
# ALTERNATIVE 2: Use Pattern Generator (Recommended for Pentatonic Scales)
# ============================================================================

# For pentatonic scales, you can generate patterns dynamically using lesson_utils:
#
# from lesson_utils import generate_pattern, create_play_sequence
#
# # Generate a pentatonic pattern
# # Pattern numbers: 1-5 (CAGED positions)
# # Scale names: 'Gmaj', 'Amin', 'F#min', etc.
# G_MAJ_PENT_POS1 = generate_pattern('Gmaj', 1)
#
# # Create simple ascending sequence
# PART1_PLAY = create_play_sequence(G_MAJ_PENT_POS1, duration=500)
#
# # Or create descending sequence
# PART1_PLAY_DESC = create_play_sequence(G_MAJ_PENT_POS1, duration=500, ascending=False)
#
# # Or create ascending then descending
# from lesson_utils import create_ascending_descending_sequence
# PART1_PLAY_BOTH = create_ascending_descending_sequence(G_MAJ_PENT_POS1, duration=500)
#
# part1 = Part(
#     name="Position 1 (E Shape)",
#     notes_to_highlight=G_MAJ_PENT_POS1,
#     play_sequence=PART1_PLAY
# )
#
# Available helper functions from lesson_utils:
# - generate_pattern(scale_name, pattern_num, start_fret=0)
# - create_play_sequence(notes, duration=200, ascending=True)
# - create_ascending_descending_sequence(notes, duration=200)
# - repeat_sequence(notes, duration=200, repetitions=2)

""" 
C major triads on 3 adjacent strings at a time, starting from the top 3 strings and ending on the bottom 3 strings.
"""

from models.lesson_model import Part, Lesson
from models.sequence_step import SequenceStep
TON = 300  # Default note duration in milliseconds

PART1_NOTES = [
    ('B', 6), ('G', 0), ('G', 3), ('G', 5),
    ('G', 7), ('D', 0), ('D', 3), ('D', 5)
]

PART1_SEQUENCE = [
    SequenceStep(notes=(('G', 7), ('D', 5)), duration_ms=500),
    SequenceStep(notes=(('G', 7), ('D', 5)), duration_ms=500),
    SequenceStep(notes=(('G', 7), ('D', 5)), duration_ms=250),
    SequenceStep(notes=(('G', 5), ('D', 5)), duration_ms=250),
    SequenceStep(notes=(('G', 7), ('D', 5)), duration_ms=250),
    SequenceStep(notes=(('B', 6), ('G', 5)), duration_ms=250),

    SequenceStep(notes=(('D', 5),), duration_ms=500),
    SequenceStep(notes=(('G', 7), ('D', 5)), duration_ms=250),
    SequenceStep(notes=(('G', 5), ('D', 5)), duration_ms=250),
    SequenceStep(notes=(('G', 5), ('D', 5)), duration_ms=250),
    SequenceStep(notes=(('G', 3), ('D', 3)), duration_ms=250),
    SequenceStep(notes=(('G', 0), ('D', 0)), duration_ms=300),
]

part1 = Part(
    name="Intro Riff - Bars 1-2",
    notes_to_highlight=PART1_NOTES,
    play_sequence=PART1_SEQUENCE,
    description="First half of the iconic intro riff"
)
PART2_NOTES = [
    ('G', 0), ('G', 3), ('G', 5), ('D', 0),
    ('D', 3), ('D', 5), ('A', 1), ('A', 3)
]

PART2_SEQUENCE = [
    SequenceStep(notes=(('G', 0), ('D', 0)), duration_ms=300),
    SequenceStep(notes=(('G', 0), ('D', 0)), duration_ms=300),
    SequenceStep(notes=(('G', 3), ('D', 3)), duration_ms=300),
    SequenceStep(notes=(('D', 0),), duration_ms=300),
    SequenceStep(notes=(('G', 0), ('D', 0)), duration_ms=300),
    SequenceStep(notes=(('D', 3), ('A', 1)), duration_ms=300),
    SequenceStep(notes=(('D', 3), ('A', 1)), duration_ms=300),
    SequenceStep(notes=(('D', 5), ('A', 3)), duration_ms=300),
    SequenceStep(notes=(('D', 3),), duration_ms=300),
    SequenceStep(notes=(('G', 5),), duration_ms=300),
    SequenceStep(notes=(('D', 3),), duration_ms=300),
    SequenceStep(notes=(('G', 3), ('D', 0)), duration_ms=300),
    SequenceStep(notes=(('G', 0),), duration_ms=300),
]

part2 = Part(
    name="Intro Riff - Bars 3-4",
    notes_to_highlight=PART2_NOTES,
    play_sequence=PART2_SEQUENCE,
    description="Second half with the descending line"
)

# REQUIRED: Export a 'lesson' variable
lesson = Lesson(
    name="Money for nothing",
    parts=[part1, part2],  # Add all your parts here
    description="Intro riff money for nothing by dire straits",
    author="Your Name",
    metadata={
        'tags': ['beginner', 'scales', 'C major'],
        'estimated_time_minutes': 10,
    }
)

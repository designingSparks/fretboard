"""
Lesson files for guitar learning application.

Each .py file in this directory can define a lesson by creating
a 'lesson' variable containing a Lesson object.

To create a new lesson:
1. Copy _template.py to a new file (e.g., my_lesson.py)
2. Edit the note sequences and part definitions
3. The lesson will automatically be discovered by the loader

Define sequence entries with named fields:
    SequenceStep(notes=(('e', 3), ('B', 3), ('G', 4)), duration_ms=1000,
                 chord_name='G', shape='E', position_group=1)
Import SequenceStep from models.sequence_step. chord_name, shape, and
position_group are optional; an empty notes tuple represents a rest.
"""

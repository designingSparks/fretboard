"""
Utilities for creating guitar lesson files.

This package provides helper functions for generating patterns, creating
play sequences, and working with fretboard note data.
"""

# Pattern generation functions
from lesson_utils.patterns import (
    generate_pattern,
    parse_scale_name,
    format_pattern_output,
    print_pattern,
)

# Sequence creation helpers
from lesson_utils.utils import (
    create_play_sequence,
    create_ascending_descending_sequence,
    repeat_sequence,
)

# Triad generation functions
from lesson_utils.triads import (
    generate_triad_notes,
    parse_key,
)

__all__ = [
    # Pattern generation
    'generate_pattern',
    'parse_scale_name',
    'format_pattern_output',
    'print_pattern',
    # Sequence helpers
    'create_play_sequence',
    'create_ascending_descending_sequence',
    'repeat_sequence',
    # Triad generation
    'generate_triad_notes',
    'parse_key',
]

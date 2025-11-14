"""
G Major Pentatonic Scale - All 5 CAGED Positions

This lesson teaches the G major pentatonic scale across all five positions
on the fretboard using the CAGED system. The patterns are dynamically generated
using the generate_scale.py utility.
"""

import sys
from pathlib import Path

# Add utils directory to path for importing generate_scale
utils_path = Path(__file__).parent.parent / 'utils'
sys.path.insert(0, str(utils_path))

from generate_scale import generate_pattern
from models.lesson_model import Part, Lesson

# ============================================================================
# CONFIGURATION
# ============================================================================

TON = 200  # Default note duration in milliseconds

# ============================================================================
# HELPER FUNCTION
# ============================================================================

def create_play_sequence(notes, asc=True):
    """
    Convert a list of note tuples to a play sequence with durations.

    Args:
        notes: List of (string, fret) tuples
        asc: If True, play notes in ascending order (low E to high e).
             If False, reverse to descending order (high e to low E). Default: True.

    Returns:
        List of [[note_tuple, duration], ...] for play sequence
    """
    sequence = notes if asc else list(reversed(notes))
    return [[note, TON] for note in sequence]

# ============================================================================
# PATTERN GENERATION
# ============================================================================

# Generate all 5 patterns for G major pentatonic
G_MAJ_PENT_POS1 = generate_pattern('Gmaj', 1)
G_MAJ_PENT_POS2 = generate_pattern('Gmaj', 2)
G_MAJ_PENT_POS3 = generate_pattern('Gmaj', 3)
G_MAJ_PENT_POS4 = generate_pattern('Gmaj', 4)
G_MAJ_PENT_POS5 = generate_pattern('Gmaj', 5)

# ============================================================================
# PART 1: Position 1 (E Shape)
# ============================================================================

part1 = Part(
    name="Position 1 (E Shape)",
    notes_to_highlight=G_MAJ_PENT_POS1,
    play_sequence=create_play_sequence(G_MAJ_PENT_POS1),
    highlight_classes={'G': 'highlight1'},
    description='Start with the E shape pattern around fret 3. Root note: Low E string fret 3'
)

# ============================================================================
# PART 2: Position 2 (D Shape)
# ============================================================================

part2 = Part(
    name="Position 2 (D Shape)",
    notes_to_highlight=G_MAJ_PENT_POS2,
    play_sequence=create_play_sequence(G_MAJ_PENT_POS2),
    highlight_classes={'G': 'highlight1'},
    description='D shape pattern around fret 5. Root note: D string fret 5'
)

# ============================================================================
# PART 3: Position 3 (C Shape)
# ============================================================================

part3 = Part(
    name="Position 3 (C Shape)",
    notes_to_highlight=G_MAJ_PENT_POS3,
    play_sequence=create_play_sequence(G_MAJ_PENT_POS3),
    highlight_classes={'G': 'highlight1'},
    description='C shape pattern around fret 7. Root note: A string fret 7'
)

# ============================================================================
# PART 4: Position 4 (A Shape)
# ============================================================================

part4 = Part(
    name="Position 4 (A Shape)",
    notes_to_highlight=G_MAJ_PENT_POS4,
    play_sequence=create_play_sequence(G_MAJ_PENT_POS4),
    highlight_classes={'G': 'highlight1'},
    description='A shape pattern around fret 10. Root note: A string fret 10'
)

# ============================================================================
# PART 5: Position 5 (G Shape)
# ============================================================================

part5 = Part(
    name="Position 5 (G Shape)",
    notes_to_highlight=G_MAJ_PENT_POS5,
    play_sequence=create_play_sequence(G_MAJ_PENT_POS5),
    highlight_classes={'G': 'highlight1'},
    description='G shape pattern around fret 12. Root notes: A string fret 10, Low E string fret 10'
)

# ============================================================================
# LESSON
# ============================================================================

lesson = Lesson(
    name="G Major Pentatonic - All 5 Positions",
    parts=[part1, part2, part3, part4, part5],
    description=(
        "Master the G major pentatonic scale across the entire fretboard. "
        "This lesson covers all five CAGED positions, allowing you to play "
        "the pentatonic scale in any position. Practice each pattern slowly, "
        "focusing on clean note transitions and memorizing the shapes."
    ),
    author="LearnLeadFast",
    metadata={
        'tags': ['pentatonic', 'scales', 'G major', 'CAGED', 'intermediate'],
        'estimated_time_minutes': 25,
        'key': 'G',
        'scale_type': 'major pentatonic',
        'prerequisites': ['Basic fretboard knowledge', 'Familiarity with pentatonic scales'],
    }
)

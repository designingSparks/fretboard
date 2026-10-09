"""Helper functions for creating lessons with named SequenceStep objects."""

from models.sequence_step import SequenceStep


def create_play_sequence(notes, duration=200, ascending=True):
    """Build one named step per note, preserving the requested playback order.

    Args:
        notes: List of (string, fret) tuples.
        duration: Note duration in milliseconds (default: 200).
        ascending: Use the given order when True, or reverse it when False.

    Returns:
        A list of SequenceStep objects.

    Example:
        >>> sequence = create_play_sequence([('E', 0), ('A', 2)], duration=500)
        >>> [(step.notes, step.duration_ms) for step in sequence]
        [((('E', 0),), 500), ((('A', 2),), 500)]
    """
    sequence = notes if ascending else reversed(notes)
    return [SequenceStep(notes=(note,), duration_ms=duration) for note in sequence]


def create_ascending_descending_sequence(notes, duration=200):
    """Build named steps in ascending and descending order, repeating the top note."""
    return (create_play_sequence(notes, duration=duration)
            + create_play_sequence(notes, duration=duration, ascending=False))


def repeat_sequence(notes, duration=200, repetitions=2):
    """Repeat a pattern of immutable, named steps the requested number of times."""
    return create_play_sequence(notes, duration=duration) * repetitions

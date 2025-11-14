"""
Helper functions for creating lesson play sequences.
"""


def create_play_sequence(notes, duration=200, ascending=True):
    """
    Convert a list of note tuples to a play sequence with durations.

    Args:
        notes: List of (string, fret) tuples
        duration: Note duration in milliseconds (default: 200)
        ascending: If True, play notes in given order (low E to high e).
                  If False, reverse to descending order. Default: True.

    Returns:
        List of [[note_tuple, duration], ...] for play sequence

    Examples:
        >>> notes = [('E', 0), ('A', 2), ('D', 2)]
        >>> create_play_sequence(notes, duration=500)
        [[('E', 0), 500], [('A', 2), 500], [('D', 2), 500]]

        >>> create_play_sequence(notes, ascending=False)
        [[('D', 2), 200], [('A', 2), 200], [('E', 0), 200]]
    """
    sequence = notes if ascending else list(reversed(notes))
    return [[note, duration] for note in sequence]


def create_ascending_descending_sequence(notes, duration=200):
    """
    Create a sequence that plays notes ascending then descending.

    Args:
        notes: List of (string, fret) tuples
        duration: Note duration in milliseconds (default: 200)

    Returns:
        List of [[note_tuple, duration], ...] going up then down

    Example:
        >>> notes = [('E', 0), ('A', 2), ('D', 2)]
        >>> create_ascending_descending_sequence(notes, duration=300)
        [[('E', 0), 300], [('A', 2), 300], [('D', 2), 300],
         [('D', 2), 300], [('A', 2), 300], [('E', 0), 300]]
    """
    ascending = [[note, duration] for note in notes]
    descending = [[note, duration] for note in reversed(notes)]
    return ascending + descending


def repeat_sequence(notes, duration=200, repetitions=2):
    """
    Repeat a note sequence multiple times.

    Args:
        notes: List of (string, fret) tuples
        duration: Note duration in milliseconds (default: 200)
        repetitions: Number of times to repeat (default: 2)

    Returns:
        List of [[note_tuple, duration], ...] repeated

    Example:
        >>> notes = [('E', 0), ('A', 2)]
        >>> repeat_sequence(notes, duration=400, repetitions=3)
        [[('E', 0), 400], [('A', 2), 400],
         [('E', 0), 400], [('A', 2), 400],
         [('E', 0), 400], [('A', 2), 400]]
    """
    single_pass = [[note, duration] for note in notes]
    return single_pass * repetitions

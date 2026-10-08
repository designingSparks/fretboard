"""Shared interpretation of legacy and chord-labelled playback rows."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SequenceStep:
    notes: tuple[tuple[str, int], ...]
    duration_ms: int
    chord_name: str | None = None


def parse_sequence_row(row) -> SequenceStep:
    """Read [note, ..., optional chord name, duration in milliseconds]."""
    if not isinstance(row, (list, tuple)) or not row:
        raise ValueError("A sequence row must end with a duration in milliseconds")
    duration = row[-1]
    if isinstance(duration, bool) or not isinstance(duration, int) or duration < 0:
        raise ValueError("Sequence duration must be a non-negative integer, placed last")

    items = list(row[:-1])
    chord_name = None
    if items and isinstance(items[-1], str):
        chord_name = items.pop().strip()
        if not chord_name:
            raise ValueError("Chord name cannot be empty")

    notes = []
    for note in items:
        if not isinstance(note, (tuple, list)) or len(note) != 2:
            raise ValueError("Expected a (string, fret) note; chord name belongs before duration")
        string_name, fret = note
        if string_name not in ('e', 'B', 'G', 'D', 'A', 'E'):
            raise ValueError(f"Invalid sequence string: {string_name!r}")
        if isinstance(fret, bool) or not isinstance(fret, int) or not 0 <= fret <= 24:
            raise ValueError(f"Invalid sequence fret: {fret!r}")
        notes.append((string_name, fret))
    return SequenceStep(tuple(notes), duration, chord_name)

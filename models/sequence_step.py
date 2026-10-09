"""Named playback steps and compatibility with older list-based sequence rows."""

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class SequenceStep:
    """One note/chord event. An empty notes tuple represents a rest.

    shape and position_group are optional lesson metadata, independent of playback.
    In chord_name, braces mark subtext below the chord, e.g. 'G_{3-4}'.
    Note positions are normalized to immutable tuples so steps can be reused safely.
    """

    notes: tuple[tuple[str, int], ...]
    duration_ms: int
    chord_name: str | None = None
    shape: str | None = None
    position_group: int | None = None

    def __post_init__(self):
        if (isinstance(self.duration_ms, bool) or not isinstance(self.duration_ms, int)
                or self.duration_ms < 0):
            raise ValueError("duration_ms must be a non-negative integer")
        for field in ('chord_name', 'shape'):
            value = getattr(self, field)
            if value is not None:
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"{field} must be a non-empty string or None")
                object.__setattr__(self, field, value.strip())
        if self.position_group is not None and (
                isinstance(self.position_group, bool)
                or not isinstance(self.position_group, int) or self.position_group < 1):
            raise ValueError("position_group must be a positive integer or None")

        if not isinstance(self.notes, (list, tuple)):
            raise ValueError("notes must be a list or tuple of (string, fret) positions")
        notes = []
        for note in self.notes:
            if not isinstance(note, (tuple, list)) or len(note) != 2:
                raise ValueError("Expected a (string, fret) note")
            string_name, fret = note
            if string_name not in ('e', 'B', 'G', 'D', 'A', 'E'):
                raise ValueError(f"Invalid sequence string: {string_name!r}")
            if isinstance(fret, bool) or not isinstance(fret, int) or not 0 <= fret <= 24:
                raise ValueError(f"Invalid sequence fret: {fret!r}")
            notes.append((string_name, fret))
        object.__setattr__(self, 'notes', tuple(notes))


def parse_sequence_row(row) -> SequenceStep:
    """Accept a named step or read [note, ..., optional chord name, duration]."""
    if isinstance(row, SequenceStep):
        return row
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

    return SequenceStep(notes=items, duration_ms=duration, chord_name=chord_name)

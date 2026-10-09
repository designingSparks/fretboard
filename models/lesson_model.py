"""
Data models for guitar learning lessons.

A Lesson consists of multiple Parts. Each Part represents a single scale,
riff section, or exercise that can be played independently.
"""

from dataclasses import dataclass, field
import math
from typing import List, Tuple, Dict, Any
from models.sequence_step import SequenceStep, parse_sequence_row


@dataclass
class Part:
    """
    Represents a single playable section of a lesson.

    A Part contains all the information needed to display and play
    a musical sequence on the fretboard.

    Attributes:
        name: Display name for this part (e.g., "Position 4 - Ascending")
        notes_to_highlight: List of (string, fret) tuples to display on fretboard
                           These are shown in grey/inactive state
        play_sequence: SequenceStep objects with named notes, duration_ms, and optional
                       chord_name, shape, and position_group fields. Legacy lists are
                       accepted and converted to SequenceStep when the Part is created.
        highlight_classes: Optional dict mapping note names to CSS classes
                          e.g., {'C': 'highlight1', 'E': 'highlight2'}
        highlight_chord_root: Use highlight1 for the current labelled chord's root
        description: Optional string describing this part
        circle_sequence_elements: Enclose each playback row's notes in a rounded outline
        wrapping_distance: Gap from note markers to the outline, in CSS pixels (>= 0)
        fillet_corners: Round the enclosing polygon's corners when outlines are enabled
        fillet_radius: Requested corner radius in CSS pixels; capped at marker radius
                       plus wrapping_distance to preserve clearance around every note

    Examples:
        >>> # Single note sequence
        >>> part = Part(
        ...     name="C Major Scale",
        ...     notes_to_highlight=[('A', 3), ('A', 5), ('D', 2)],
        ...     play_sequence=[SequenceStep(notes=(note,), duration_ms=500)
        ...                    for note in [('A', 3), ('A', 5), ('D', 2)]]
        ... )

        >>> # Chord sequence
        >>> part = Part(
        ...     name="C Major Triad",
        ...     notes_to_highlight=[('e', 0), ('B', 1), ('G', 0)],
        ...     play_sequence=[SequenceStep(notes=(('e', 0), ('B', 1), ('G', 0)),
        ...                                 duration_ms=1000, chord_name='C')]
        ... )
    """
    name: str
    notes_to_highlight: List[Tuple[str, int]]
    play_sequence: List[SequenceStep]
    highlight_classes: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    circle_sequence_elements: bool = False
    wrapping_distance: float = 8.0
    fillet_corners: bool = False
    fillet_radius: float = 24.0
    highlight_chord_root: bool = False

    def __post_init__(self):
        """Validate the part data."""
        if not self.name:
            raise ValueError("Part name cannot be empty")

        if not self.notes_to_highlight:
            raise ValueError(f"Part '{self.name}' must have notes_to_highlight")

        if not self.play_sequence:
            raise ValueError(f"Part '{self.name}' must have play_sequence")
        self.play_sequence = [parse_sequence_row(row) for row in self.play_sequence]

        for setting in ('circle_sequence_elements', 'fillet_corners', 'highlight_chord_root'):
            if not isinstance(getattr(self, setting), bool):
                raise ValueError(f"{setting} must be a boolean")
        for setting in ('wrapping_distance', 'fillet_radius'):
            value = getattr(self, setting)
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value) or value < 0):
                raise ValueError(f"{setting} must be a finite, non-negative number")

        # Validate string names
        valid_strings = {'e', 'B', 'G', 'D', 'A', 'E'}
        for string_name, fret in self.notes_to_highlight:
            if string_name not in valid_strings:
                raise ValueError(
                    f"Invalid string name '{string_name}' in part '{self.name}'. "
                    f"Must be one of {valid_strings}"
                )
            if not isinstance(fret, int) or fret < 0 or fret > 24:
                raise ValueError(
                    f"Invalid fret {fret} in part '{self.name}'. "
                    f"Must be integer between 0 and 24"
                )

    def get_duration_ms(self) -> int:
        """
        Calculate total duration of this part in milliseconds.

        Returns:
            Total duration in milliseconds
        """
        return sum(parse_sequence_row(row).duration_ms for row in self.play_sequence)

    def get_note_count(self) -> int:
        """
        Get the number of steps in this part's play sequence.

        Returns:
            Number of playback steps
        """
        return len(self.play_sequence)


@dataclass
class Lesson:
    """
    Represents a complete lesson consisting of multiple parts.

    A Lesson groups related Parts together into a cohesive learning unit.
    Users can navigate between parts using prev/next buttons.

    Attributes:
        name: Display name for this lesson
        parts: List of Part objects that make up this lesson
        description: Optional description of what the lesson teaches
        author: Optional author name
        difficulty: Optional difficulty level (e.g., 'Beginner', 'Intermediate', 'Advanced')
        use_sharp: If True, display notes with sharp notation (C#, D#, etc.)
                   If False, display notes with flat notation (Db, Eb, etc.)
                   Defaults to True for backward compatibility
                   TODO: Future enhancement - allow per-Part override
        metadata: Optional dict for additional info (tags, etc.)
        chord_label_title: Caption above the chord buttons; empty hides the caption

    Example:
        >>> part1 = Part(name="Position 4", ...)
        >>> part2 = Part(name="Position 5", ...)
        >>> lesson = Lesson(
        ...     name="C Major - Two Positions",
        ...     parts=[part1, part2],
        ...     description="Learn C major scale in positions 4 and 5"
        ... )
    """
    name: str
    parts: List[Part]
    description: str = ""
    author: str = ""
    difficulty: str = ""  # e.g., 'Beginner', 'Intermediate', 'Advanced'
    use_sharp: bool = True  # Default to sharp notation for backward compatibility
    metadata: Dict[str, Any] = field(default_factory=dict)
    chord_label_title: str = "Triad playing"

    def __post_init__(self):
        """Validate the lesson data."""
        if not self.name:
            raise ValueError("Lesson name cannot be empty")

        if not isinstance(self.chord_label_title, str):
            raise ValueError("chord_label_title must be a string")

        if not self.parts:
            raise ValueError(f"Lesson '{self.name}' must have at least one part")

        if not all(isinstance(part, Part) for part in self.parts):
            raise ValueError(f"Lesson '{self.name}' parts must be Part instances")

    def get_part_count(self) -> int:
        """
        Get the number of parts in this lesson.

        Returns:
            Number of parts
        """
        return len(self.parts)

    def get_part(self, index: int) -> Part:
        """
        Get a part by index.

        Args:
            index: Zero-based index of the part

        Returns:
            Part object at the given index

        Raises:
            IndexError: If index is out of range
        """
        return self.parts[index]

    def get_total_duration_ms(self) -> int:
        """
        Calculate total duration of all parts in milliseconds.

        Returns:
            Total duration in milliseconds
        """
        return sum(part.get_duration_ms() for part in self.parts)

    def __str__(self) -> str:
        """String representation of the lesson."""
        return f"Lesson(name='{self.name}', parts={len(self.parts)})"

    def __repr__(self) -> str:
        """Detailed representation of the lesson."""
        return (
            f"Lesson(name='{self.name}', "
            f"parts={len(self.parts)}, "
            f"duration={self.get_total_duration_ms()}ms)"
        )

"""
Data models for guitar learning lessons.

A Lesson consists of multiple Parts. Each Part represents a single scale,
riff section, or exercise that can be played independently.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Union


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
        play_sequence: The actual sequence of notes to play. Format:
                      - Single notes: [[('A', 3), 500], [('A', 5), 500], ...]
                      - Chords: [[('e', 0), ('B', 1), ('G', 0), 1000], ...]
                      Last element in each sublist is duration in milliseconds
        highlight_classes: Optional dict mapping note names to CSS classes
                          e.g., {'C': 'highlight1', 'E': 'highlight2'}
        description: Optional string describing this part

    Examples:
        >>> # Single note sequence
        >>> part = Part(
        ...     name="C Major Scale",
        ...     notes_to_highlight=[('A', 3), ('A', 5), ('D', 2)],
        ...     play_sequence=[[('A', 3), 500], [('A', 5), 500], [('D', 2), 500]]
        ... )

        >>> # Chord sequence
        >>> part = Part(
        ...     name="C Major Triad",
        ...     notes_to_highlight=[('e', 0), ('B', 1), ('G', 0)],
        ...     play_sequence=[[('e', 0), ('B', 1), ('G', 0), 1000]]
        ... )
    """
    name: str
    notes_to_highlight: List[Tuple[str, int]]
    play_sequence: List[Union[List, Tuple]]
    highlight_classes: Dict[str, str] = field(default_factory=dict)
    description: str = ""

    def __post_init__(self):
        """Validate the part data."""
        if not self.name:
            raise ValueError("Part name cannot be empty")

        if not self.notes_to_highlight:
            raise ValueError(f"Part '{self.name}' must have notes_to_highlight")

        if not self.play_sequence:
            raise ValueError(f"Part '{self.name}' must have play_sequence")

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
        total = 0
        for item in self.play_sequence:
            # Last element is always duration
            total += item[-1]
        return total

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
        use_sharp: If True, display notes with sharp notation (C#, D#, etc.)
                   If False, display notes with flat notation (Db, Eb, etc.)
                   Defaults to True for backward compatibility
                   TODO: Future enhancement - allow per-Part override
        metadata: Optional dict for additional info (tags, difficulty, etc.)

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
    use_sharp: bool = True  # Default to sharp notation for backward compatibility
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate the lesson data."""
        if not self.name:
            raise ValueError("Lesson name cannot be empty")

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

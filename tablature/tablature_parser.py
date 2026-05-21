"""
Tablature Parser Module

Converts guitar tablature text files into Part objects compatible with the
Fretboard application's lesson system.

The parser takes tablature in standard ASCII format and configuration specifying:
- Which bars belong to which parts
- Note durations for timing

Returns Part objects ready to be used in Lesson definitions.
"""

from typing import List, Dict, Tuple, Union, Any
from models.lesson_model import Part
import re


# String mapping from tab notation to internal format
STRING_MAP = {
    'e': 'e',   # High E string
    'B': 'B',   # B string
    'G': 'G',   # G string
    'D': 'D',   # D string
    'A': 'A',   # A string
    'E': 'E',   # Low E string
}

# Order of strings in tab files (top to bottom)
STRING_ORDER = ['e', 'B', 'G', 'D', 'A', 'E']


def split_by_bars(tab_text: str) -> List[List[str]]:
    """
    Split tablature text into individual bars.

    Args:
        tab_text: Raw tablature text with bar delimiters (|)

    Returns:
        List of bars, where each bar is a list of 6 strings (one per guitar string)
    """
    lines = tab_text.strip().split('\n')

    # Filter out empty lines and keep only string lines
    string_lines = []
    for line in lines:
        # Look for lines that start with a string identifier
        if any(line.strip().startswith(f'{s}|') for s in STRING_ORDER):
            string_lines.append(line)

    if len(string_lines) != 6:
        raise ValueError(f"Expected 6 string lines in tablature, found {len(string_lines)}")

    # Find bar delimiters (|) positions
    # Use the first string line as reference
    first_line = string_lines[0]

    # Split by | but keep track of positions
    bar_delimiters = []
    for i, char in enumerate(first_line):
        if char == '|':
            bar_delimiters.append(i)

    if len(bar_delimiters) < 2:
        raise ValueError("Need at least 2 bar delimiters (|) to define bars")

    # Extract content between delimiters for each bar
    bars = []
    for bar_idx in range(len(bar_delimiters) - 1):
        start_pos = bar_delimiters[bar_idx] + 1
        end_pos = bar_delimiters[bar_idx + 1]

        bar_strings = []
        for string_line in string_lines:
            # Extract the segment between delimiters
            segment = string_line[start_pos:end_pos]
            bar_strings.append(segment)

        bars.append(bar_strings)

    return bars


def parse_bar(bar_strings: List[str]) -> List[Dict[str, Any]]:
    """
    Parse a single bar into note events with position information.

    Args:
        bar_strings: List of 6 strings representing the bar content (one per guitar string)

    Returns:
        List of note events, where each event is:
        {
            'position': int (character position in bar),
            'notes': [(string, fret), ...],  # List for chords, single item for single notes
        }
    """
    if len(bar_strings) != 6:
        raise ValueError(f"Expected 6 strings for bar, got {len(bar_strings)}")

    # Strip parentheses from the bar strings (treat (6) as 6, etc.)
    cleaned_bar_strings = []
    for bar_string in bar_strings:
        # Remove all parentheses
        cleaned = bar_string.replace('(', '').replace(')', '')
        cleaned_bar_strings.append(cleaned)

    bar_strings = cleaned_bar_strings

    # Ensure all strings have same length (pad if needed)
    max_length = max(len(s) for s in bar_strings)
    bar_strings = [s.ljust(max_length) for s in bar_strings]

    events = []

    # Scan through each position in the bar
    for pos in range(max_length):
        notes_at_position = []

        # Check each string at this position
        for string_idx, string_name in enumerate(STRING_ORDER):
            char = bar_strings[string_idx][pos] if pos < len(bar_strings[string_idx]) else '-'

            # Check if it's a fret number
            if char.isdigit():
                fret = int(char)

                # Check for two-digit fret numbers (e.g., 12, 15)
                if pos + 1 < max_length and bar_strings[string_idx][pos + 1].isdigit():
                    fret = int(char + bar_strings[string_idx][pos + 1])

                notes_at_position.append((string_name, fret))

            # Check for open string (0)
            elif char == '0':
                notes_at_position.append((string_name, 0))

        # If we found notes at this position, create an event
        if notes_at_position:
            events.append({
                'position': pos,
                'notes': notes_at_position,
            })

    return events


def extract_notes_from_bars(bars: List[List[str]], bar_indices: List[int]) -> List[Tuple[str, int]]:
    """
    Extract all unique notes from specified bars for the highlight list.

    Args:
        bars: List of all bars from the tablature
        bar_indices: List of bar numbers (1-indexed) to extract from

    Returns:
        List of unique (string, fret) tuples
    """
    all_notes = set()

    for bar_num in bar_indices:
        if bar_num < 1 or bar_num > len(bars):
            raise ValueError(f"Bar number {bar_num} out of range (1-{len(bars)})")

        bar = bars[bar_num - 1]  # Convert to 0-indexed
        events = parse_bar(bar)

        for event in events:
            for note in event['notes']:
                all_notes.add(note)

    # Sort by string order, then by fret
    string_order_map = {s: i for i, s in enumerate(STRING_ORDER)}
    sorted_notes = sorted(all_notes, key=lambda x: (string_order_map[x[0]], x[1]))

    return sorted_notes


def create_play_sequence_from_bars(bars: List[List[str]], bar_indices: List[int],
                                   note_durations: List[int]) -> List[List[Union[Tuple[str, int], int]]]:
    """
    Create a play sequence from specified bars with given note durations.

    Args:
        bars: List of all bars from the tablature
        bar_indices: List of bar numbers (1-indexed) to use
        note_durations: List of durations (in ms) for each note/chord event

    Returns:
        Play sequence in the format: [[note(s)..., duration], ...]
    """
    all_events = []

    # Collect events from specified bars
    for bar_num in bar_indices:
        if bar_num < 1 or bar_num > len(bars):
            raise ValueError(f"Bar number {bar_num} out of range (1-{len(bars)})")

        bar = bars[bar_num - 1]  # Convert to 0-indexed
        events = parse_bar(bar)
        all_events.extend(events)

    # Build play sequence
    play_sequence = []

    for i, event in enumerate(all_events):
        # Get duration for this event
        if i < len(note_durations):
            duration = note_durations[i]
        else:
            # If we run out of durations, use the last one
            duration = note_durations[-1] if note_durations else 500

        # Build the sequence entry
        if len(event['notes']) == 1:
            # Single note
            seq_entry = [event['notes'][0], duration]
        else:
            # Chord (multiple notes)
            seq_entry = list(event['notes']) + [duration]

        play_sequence.append(seq_entry)

    return play_sequence


def parse_tablature(tab_text: str, config: Dict[str, Any]) -> List[Part]:
    """
    Parse tablature text into Part objects.

    Args:
        tab_text: Raw tablature text with bar delimiters (|)
        config: Configuration dictionary with:
            - 'parts_list': List[List[int]] - Bar groupings, e.g., [[1,2], [3,4]]
            - 'note_durations': List[int] - Duration in ms for each note event
            - 'part_names': List[str] (optional) - Names for each part
            - 'part_descriptions': List[str] (optional) - Descriptions for each part

    Returns:
        List of Part objects ready to use in a Lesson

    Example:
        config = {
            'parts_list': [[1, 2], [3, 4]],
            'note_durations': [300] * 20,
            'part_names': ['Intro - Part 1', 'Intro - Part 2']
        }
        parts = parse_tablature(tab_text, config)
    """
    # Validate config
    if 'parts_list' not in config:
        raise ValueError("Config must include 'parts_list'")
    if 'note_durations' not in config:
        raise ValueError("Config must include 'note_durations'")

    parts_list = config['parts_list']
    note_durations = config['note_durations']
    part_names = config.get('part_names', [f"Part {i+1}" for i in range(len(parts_list))])
    part_descriptions = config.get('part_descriptions', [''] * len(parts_list))

    # Split tablature into bars
    bars = split_by_bars(tab_text)

    # Create Parts
    parts = []
    duration_index = 0  # Track position in duration list

    for i, bar_indices in enumerate(parts_list):
        # Extract notes for highlighting
        highlight_notes = extract_notes_from_bars(bars, bar_indices)

        # Calculate how many note events are in these bars
        total_events = 0
        for bar_num in bar_indices:
            bar = bars[bar_num - 1]
            events = parse_bar(bar)
            total_events += len(events)

        # Get durations for this part
        part_durations = note_durations[duration_index:duration_index + total_events]
        if len(part_durations) < total_events:
            # Pad with last duration if needed
            last_duration = part_durations[-1] if part_durations else 500
            part_durations.extend([last_duration] * (total_events - len(part_durations)))

        duration_index += total_events

        # Create play sequence
        play_sequence = create_play_sequence_from_bars(bars, bar_indices, part_durations)

        # Create Part object
        part = Part(
            name=part_names[i] if i < len(part_names) else f"Part {i+1}",
            notes_to_highlight=highlight_notes,
            play_sequence=play_sequence,
            description=part_descriptions[i] if i < len(part_descriptions) else ''
        )

        parts.append(part)

    return parts


def print_parse_info(tab_text: str) -> None:
    """
    Utility function to analyze tablature and print useful information
    for configuring the parser.

    Args:
        tab_text: Raw tablature text
    """
    bars = split_by_bars(tab_text)

    print(f"Found {len(bars)} bars in tablature")
    print()

    for bar_num, bar in enumerate(bars, 1):
        events = parse_bar(bar)
        print(f"Bar {bar_num}: {len(events)} note events")
        for event in events:
            if len(event['notes']) == 1:
                print(f"  Position {event['position']}: {event['notes'][0]}")
            else:
                print(f"  Position {event['position']}: CHORD {event['notes']}")

    print()
    total_events = sum(len(parse_bar(bar)) for bar in bars)
    print(f"Total note events: {total_events}")
    print(f"Suggested note_durations length: {total_events}")


def print_part_code(part: Part, part_name_variable: str = 'part1',
                    notes_constant: str = 'PART1_NOTES',
                    sequence_constant: str = 'PART1_SEQUENCE') -> None:
    """
    Print a Part object as formatted Python code for copy/paste into lesson files.

    Args:
        part: The Part object to print
        part_name_variable: Variable name for the part (e.g., 'part1', 'part2')
        notes_constant: Constant name for notes_to_highlight array
        sequence_constant: Constant name for play_sequence array

    Example:
        print_part_code(part1, 'part1', 'PART1_NOTES', 'PART1_SEQUENCE')
    """
    # Print notes_to_highlight
    print(f"{notes_constant} = [")

    # Group notes by 4 per line for readability
    notes = part.notes_to_highlight
    for i in range(0, len(notes), 4):
        chunk = notes[i:i+4]
        formatted_notes = ', '.join(f"{note}" for note in chunk)
        if i + 4 < len(notes):
            print(f"    {formatted_notes},")
        else:
            print(f"    {formatted_notes}")

    print("]")
    print()

    # Print play_sequence
    print(f"{sequence_constant} = [")

    for seq_item in part.play_sequence:
        print(f"    {seq_item},")

    print("]")
    print()

    # Print Part constructor
    print(f"{part_name_variable} = Part(")
    print(f'    name="{part.name}",')
    print(f"    notes_to_highlight={notes_constant},")
    print(f"    play_sequence={sequence_constant},")
    if part.description:
        print(f'    description="{part.description}"')
    else:
        print(f'    description=""')
    print(")")


def print_lesson_code(parts: List[Part], lesson_name: str = "My Lesson",
                      lesson_description: str = "",
                      author: str = "",
                      difficulty: str = "Intermediate") -> None:
    """
    Print complete lesson code for all parts, ready to copy/paste.

    Args:
        parts: List of Part objects
        lesson_name: Name of the lesson
        lesson_description: Description of what the lesson teaches
        author: Author/artist name
        difficulty: Difficulty level (Beginner, Intermediate, Advanced)

    Example:
        parts = parse_tablature(tab_text, config)
        print_lesson_code(parts, "Money for Nothing - Intro",
                         "Learn the iconic intro riff", "Dire Straits")
    """
    print('"""')
    print(f'{lesson_name}')
    if author:
        print(f'Artist: {author}')
    print()
    print(f'{lesson_description}')
    print('"""')
    print()
    print("from models.lesson_model import Part, Lesson")
    print()
    print("# ============================================================================")
    print()

    # Print each part
    part_variables = []
    for i, part in enumerate(parts, 1):
        part_var = f"part{i}"
        notes_const = f"PART{i}_NOTES"
        seq_const = f"PART{i}_SEQUENCE"

        print(f"# Part {i}: {part.name}")
        print("# " + "=" * 76)
        print_part_code(part, part_var, notes_const, seq_const)
        print()

        part_variables.append(part_var)

    # Print lesson constructor
    print("# ============================================================================")
    print("# LESSON - Combine parts into a lesson")
    print("# ============================================================================")
    print("lesson = Lesson(")
    print(f'    name="{lesson_name}",')
    print(f"    parts=[{', '.join(part_variables)}],")
    print(f'    description="{lesson_description}",')
    if author:
        print(f'    author="{author}",')
    print(f'    difficulty="{difficulty}",')
    print("    use_sharp=True,")
    print("    metadata={")
    print("        'tags': ['rock', 'riff'],")
    print("        'estimated_time_minutes': 10,")
    print("    }")
    print(")")

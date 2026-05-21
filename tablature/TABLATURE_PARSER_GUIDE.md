# Tablature Parser Guide

The `tablature_parser.py` module converts ASCII guitar tablature into Python `Part` objects that can be used in the Fretboard application's lesson system.

## Quick Start

### 1. Prepare Your Tablature File

Create a `.txt` file with standard ASCII tablature format:

```
e|---------------|------------------|
B|-------------6-|-(6)--------------|
G|-7--7--7-5-7-5-|-(5)--7-5-5-3---0-|
D|-5--5--5-5-5---|--5---5-5-5-3-x-0-|
A|---------------|------------------|
E|---------------|------------------|
```

**Requirements:**
- 6 lines representing strings (e, B, G, D, A, E from top to bottom)
- Bar delimiters using `|` characters
- Fret numbers (0-24) or `-` for no note
- Each line should start with `stringName|` (e.g., `e|`, `B|`)

**Special notation supported:**
- `(n)` - Bracketed notes (parentheses are stripped, note treated as regular note)
- `x` - Muted strings (currently ignored/not parsed as notes)
- Open strings: `0`
- Two-digit frets: `12`, `15`, etc.

**Note:** Parentheses around numbers like `(6)` or `(0)` are automatically removed during parsing, so `(6)` is treated exactly the same as `6`.

### 2. Analyze Your Tablature

Before parsing, use the `print_parse_info()` function to see how many bars and note events you have:

```python
from tablature.tablature_parser import print_parse_info

with open('tablature/your_song.txt', 'r') as f:
    tab = f.read()

print_parse_info(tab)
```

This outputs:
```
Found 4 bars in tablature

Bar 1: 6 note events
  Position 1: CHORD [('G', 7), ('D', 5)]
  Position 4: CHORD [('G', 7), ('D', 5)]
  ...

Total note events: 23
Suggested note_durations length: 23
```

### 3. Create Your Lesson File

Create a new Python file in the `lessons/` directory:

```python
"""
Your Song Title - Artist Name
Description of the riff/song
"""

import sys
import os

# Add parent directory to path for imports when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.lesson_model import Lesson
from tablature.tablature_parser import parse_tablature

# Load the tablature file
# Handle both running from project root and from tablature directory
tab_file = 'tablature/your_song.txt'
if not os.path.exists(tab_file):
    tab_file = 'your_song.txt'  # Running from tablature directory

with open(tab_file, 'r') as f:
    tab_text = f.read()

# Configure the parser
config = {
    # Define which bars belong to each part
    # [[1, 2], [3, 4]] means bars 1-2 are part 1, bars 3-4 are part 2
    'parts_list': [[1, 2], [3, 4]],

    # Duration in milliseconds for each note event
    # Length should match total events (from print_parse_info)
    'note_durations': [300] * 23,  # 300ms per note

    # Optional: custom names for each part
    'part_names': [
        'Intro - Bars 1-2',
        'Intro - Bars 3-4'
    ],

    # Optional: descriptions for each part
    'part_descriptions': [
        'First half of the riff',
        'Second half with variation'
    ]
}

# Parse the tablature
parts = parse_tablature(tab_text, config)

# Create the lesson
lesson = Lesson(
    name="Your Song Title",
    parts=parts,
    description="Learn this awesome riff!",
    author="Artist Name",
    difficulty="Intermediate",  # Beginner, Intermediate, Advanced
    use_sharp=True,  # True for sharps, False for flats
    metadata={
        'tags': ['rock', 'riff', 'intermediate'],
        'estimated_time_minutes': 10,
    }
)
```

**IMPORTANT:**
- The file must export a variable named `lesson`!
- The `sys.path` setup at the top allows you to run the lesson file directly from VSCode or the command line for testing, while still working when imported by the main application.

## Configuration Options

### `parts_list`
**Required.** List of lists defining bar groupings for each part.

Examples:
```python
# All bars in one part
'parts_list': [[1, 2, 3, 4]]

# Each bar as separate part
'parts_list': [[1], [2], [3], [4]]

# Group bars together
'parts_list': [[1, 2], [3, 4]]

# Non-sequential grouping
'parts_list': [[1, 3], [2, 4]]
```

**Note:** Bar numbers are 1-indexed (first bar = 1).

### `note_durations`
**Required.** List of integers specifying duration in milliseconds for each note event.

```python
# All notes same duration
'note_durations': [300] * 23  # 23 events, each 300ms

# Variable durations
'note_durations': [
    500, 500, 500, 300, 300, 300,  # Bar 1 notes
    400, 400, 200, 200, 200,       # Bar 2 notes
    # ... etc
]
```

**Tip:** Use `print_parse_info()` to find the exact number of events needed.

### `part_names` (optional)
List of strings for part names. Defaults to "Part 1", "Part 2", etc.

```python
'part_names': [
    'Intro Riff',
    'Verse Pattern',
    'Chorus Riff'
]
```

### `part_descriptions` (optional)
List of strings for part descriptions. Defaults to empty strings.

```python
'part_descriptions': [
    'Start with palm muting',
    'Let notes ring out',
    'Build intensity here'
]
```

## Common Patterns

### Practice Each Bar Separately
```python
config = {
    'parts_list': [[1], [2], [3], [4]],
    'note_durations': [300] * total_events,
    'part_names': ['Bar 1', 'Bar 2', 'Bar 3', 'Bar 4']
}
```

### Split Into Two Halves
```python
config = {
    'parts_list': [[1, 2], [3, 4]],
    'note_durations': [300] * total_events,
    'part_names': ['First Half', 'Second Half']
}
```

### Single Complete Riff
```python
config = {
    'parts_list': [[1, 2, 3, 4]],
    'note_durations': [300] * total_events,
    'part_names': ['Complete Riff']
}
```

### Variable Tempo
```python
# Slow notes at beginning, faster at end
durations = [500] * 8 + [300] * 10 + [200] * 5

config = {
    'parts_list': [[1, 2, 3, 4]],
    'note_durations': durations
}
```

## Timing and Tempo

The `note_durations` values control playback speed:

- **500ms** = 0.5 seconds per note (slower, good for learning)
- **300ms** = 0.3 seconds per note (medium tempo)
- **200ms** = 0.2 seconds per note (faster)
- **150ms** = 0.15 seconds per note (very fast)

To match a specific BPM:
```python
# For quarter notes at 120 BPM:
# 60000ms / 120 BPM = 500ms per beat
quarter_note = 60000 / 120  # 500ms

# For eighth notes:
eighth_note = quarter_note / 2  # 250ms
```

## Example: Money for Nothing

See [lessons/money_for_nothing.py](lessons/money_for_nothing.py) for a complete working example.

## Troubleshooting

### "Expected 6 string lines in tablature"
Make sure your tab file has exactly 6 lines (one for each string) and each line starts with a string identifier (`e|`, `B|`, `G|`, `D|`, `A|`, `E|`).

### "Need at least 2 bar delimiters"
Ensure you have `|` characters delimiting bars in your tablature.

### Duration list too short
If you get warnings about durations, use `print_parse_info()` to find the exact number of note events, then provide that many durations.

### Notes not aligned correctly
Make sure your tablature is properly formatted with consistent spacing. Notes played together (chords) should be vertically aligned.

## API Reference

### `parse_tablature(tab_text, config)`
Main parsing function.

**Args:**
- `tab_text` (str): Raw tablature text
- `config` (dict): Configuration dictionary with `parts_list`, `note_durations`, and optional keys

**Returns:**
- `List[Part]`: List of Part objects ready for use in a Lesson

### `print_parse_info(tab_text)`
Utility function to analyze tablature structure.

**Args:**
- `tab_text` (str): Raw tablature text

**Output:**
Prints bar count, events per bar, and total event count to console.

### `print_part_code(part, part_name_variable, notes_constant, sequence_constant)`
Print a Part object as formatted Python code for copy/paste into lesson files.

**Args:**
- `part` (Part): The Part object to print
- `part_name_variable` (str): Variable name for the part (default: 'part1')
- `notes_constant` (str): Constant name for notes_to_highlight array (default: 'PART1_NOTES')
- `sequence_constant` (str): Constant name for play_sequence array (default: 'PART1_SEQUENCE')

**Example:**
```python
from tablature.tablature_parser import parse_tablature, print_part_code

parts = parse_tablature(tab_text, config)
print_part_code(parts[0], 'part1', 'PART1_NOTES', 'PART1_SEQUENCE')
```

**Output:**
```python
PART1_NOTES = [
    ('G', 7), ('D', 5), ('B', 6), ('G', 5),
]

PART1_SEQUENCE = [
    [('G', 7), ('D', 5), 300],
    [('G', 7), ('D', 5), 300],
]

part1 = Part(
    name="Intro Riff",
    notes_to_highlight=PART1_NOTES,
    play_sequence=PART1_SEQUENCE,
    description=""
)
```

### `print_lesson_code(parts, lesson_name, lesson_description, author, difficulty)`
Print complete lesson code for all parts, ready to copy/paste.

**Args:**
- `parts` (List[Part]): List of Part objects
- `lesson_name` (str): Name of the lesson (default: "My Lesson")
- `lesson_description` (str): Description of what the lesson teaches (default: "")
- `author` (str): Author/artist name (default: "")
- `difficulty` (str): Difficulty level (default: "Intermediate")

**Example:**
```python
from tablature.tablature_parser import parse_tablature, print_lesson_code

parts = parse_tablature(tab_text, config)
print_lesson_code(parts, "Money for Nothing - Intro",
                 "Learn the iconic intro riff", "Dire Straits", "Intermediate")
```

This prints a complete lesson file with all parts, ready to copy into a `.py` file.

### `split_by_bars(tab_text)`
Split tablature into individual bars.

**Returns:**
- `List[List[str]]`: List of bars, each bar is 6 strings

### `extract_notes_from_bars(bars, bar_indices)`
Extract all unique notes from specified bars.

**Returns:**
- `List[Tuple[str, int]]`: List of (string, fret) tuples

### `create_play_sequence_from_bars(bars, bar_indices, note_durations)`
Create a play sequence from bars.

**Returns:**
- `List[List]`: Play sequence in format `[[note(s), duration], ...]`

## Quick Workflow: Generate Lesson Code

The fastest way to create a lesson from tablature:

1. **Analyze the tablature:**
   ```bash
   python analyze_tab.py tablature/your_song.txt
   ```

2. **Generate lesson code:**
   ```python
   from tablature.tablature_parser import parse_tablature, print_lesson_code

   with open('tablature/your_song.txt', 'r') as f:
       tab = f.read()

   config = {
       'parts_list': [[1, 2], [3, 4]],
       'note_durations': [300] * 28,
       'part_names': ['Part 1', 'Part 2']
   }

   parts = parse_tablature(tab, config)
   print_lesson_code(parts, "Song Title", "Description", "Artist")
   ```

3. **Copy/paste the output** into a new lesson file and customize as needed!

## Tips

1. **Start simple:** Begin with `parts_list: [[1, 2, 3, 4]]` to play the whole riff, then split into parts later.

2. **Use consistent durations:** Start with the same duration for all notes (e.g., `[300] * 23`), then adjust as needed.

3. **Test incrementally:** Use `print_parse_info()` first, then test with simple config, then refine.

4. **Match the original tempo:** Listen to the original recording and adjust `note_durations` to match.

5. **Practice sections:** Create parts that make sense for practice (intro, verse, chorus) rather than just bar numbers.

6. **Use print functions:** Use `print_part_code()` and `print_lesson_code()` to quickly generate copy/paste-ready code.

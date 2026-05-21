# Tablature Parser - Example Usage

Quick examples showing how to use the tablature parser functions.

## Example 1: Basic Parsing and Lesson Creation

```python
from tablature.tablature_parser import parse_tablature
from models.lesson_model import Lesson

# Load tablature
with open('tablature/money_for_nothing.txt', 'r') as f:
    tab_text = f.read()

# Configure parser
config = {
    'parts_list': [[1, 2], [3, 4]],  # Bars 1-2, then 3-4
    'note_durations': [300] * 28,     # 300ms per note
    'part_names': ['Intro - Part 1', 'Intro - Part 2']
}

# Parse into Part objects
parts = parse_tablature(tab_text, config)

# Create lesson
lesson = Lesson(
    name="Money for Nothing - Intro",
    parts=parts,
    description="Learn the iconic intro riff",
    author="Dire Straits",
    difficulty="Intermediate",
    metadata={'tags': ['rock', 'riff']}
)

# Use in your application...
```

## Example 2: Analyze Tablature Structure

```python
from tablature.tablature_parser import print_parse_info

# Load tablature
with open('tablature/your_song.txt', 'r') as f:
    tab_text = f.read()

# Analyze structure
print_parse_info(tab_text)

# Output:
# Found 4 bars in tablature
# Bar 1: 6 note events
#   Position 1: CHORD [('G', 7), ('D', 5)]
#   ...
# Total note events: 23
# Suggested note_durations length: 23
```

## Example 3: Generate Copy/Paste Code for Single Part

```python
from tablature.tablature_parser import parse_tablature, print_part_code

# Parse tablature
with open('tablature/song.txt', 'r') as f:
    tab = f.read()

config = {
    'parts_list': [[1, 2]],
    'note_durations': [300] * 15,
}

parts = parse_tablature(tab, config)

# Print code for first part
print_part_code(parts[0], 'part1', 'PART1_NOTES', 'PART1_SEQUENCE')

# Copy the output and paste into your lesson file!
```

## Example 4: Generate Complete Lesson File Code

```python
from tablature.tablature_parser import parse_tablature, print_lesson_code

# Parse tablature
with open('tablature/song.txt', 'r') as f:
    tab = f.read()

config = {
    'parts_list': [[1, 2], [3, 4]],
    'note_durations': [300] * 28,
    'part_names': ['Verse', 'Chorus'],
    'part_descriptions': ['Main verse pattern', 'Chorus riff']
}

parts = parse_tablature(tab, config)

# Print complete lesson code
print_lesson_code(
    parts,
    lesson_name="My Song - Main Riff",
    lesson_description="Learn the main riff with verse and chorus sections",
    author="Artist Name",
    difficulty="Intermediate"
)

# Copy everything from the output into a new .py file in lessons/
```

## Example 5: Different Bar Groupings

```python
# Each bar as separate part (for practice)
config = {
    'parts_list': [[1], [2], [3], [4]],
    'note_durations': [300] * 20,
    'part_names': ['Bar 1', 'Bar 2', 'Bar 3', 'Bar 4']
}

# All bars together
config = {
    'parts_list': [[1, 2, 3, 4]],
    'note_durations': [300] * 20,
    'part_names': ['Complete Riff']
}

# Non-sequential grouping
config = {
    'parts_list': [[1, 3], [2, 4]],  # Odd bars, then even bars
    'note_durations': [300] * 20,
    'part_names': ['Pattern A', 'Pattern B']
}
```

## Example 6: Variable Note Durations

```python
# Different speeds for different sections
config = {
    'parts_list': [[1, 2], [3, 4]],
    'note_durations': [
        # Bar 1-2: slower for learning
        500, 500, 500, 500, 500, 500, 500, 500,
        # Bar 3-4: faster
        300, 300, 300, 300, 300, 300, 300, 300,
    ],
    'part_names': ['Slow Practice', 'Full Speed']
}
```

## Example 7: Interactive Workflow

```python
# In Python REPL or Jupyter notebook
from tablature.tablature_parser import *

# 1. Analyze
with open('tablature/song.txt', 'r') as f:
    tab = f.read()

print_parse_info(tab)  # See how many events

# 2. Parse with config based on analysis
config = {
    'parts_list': [[1, 2]],
    'note_durations': [300] * 15,  # Use count from analysis
}

parts = parse_tablature(tab, config)

# 3. Check what we got
print(f"Created {len(parts)} parts")
print(f"Part 1 has {len(parts[0].play_sequence)} events")

# 4. Generate code to copy/paste
print_part_code(parts[0])

# 5. Or generate complete lesson
print_lesson_code(parts, "Song Title", "Description")
```

## Example 8: Command Line Tools

```bash
# Analyze tablature structure
python analyze_tab.py lessons/money_for_nothing.txt

# Generate lesson code interactively
python generate_lesson_code.py lessons/money_for_nothing.txt
# Follow the prompts to configure...
```

## Example 9: In VSCode

Create a lesson file that can be run directly:

```python
"""
My Song - Riff
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tablature.tablature_parser import parse_tablature, print_lesson_code
from models.lesson_model import Lesson

# Load tab
tab_file = 'tablature/my_song.txt'
if not os.path.exists(tab_file):
    tab_file = 'my_song.txt'

with open(tab_file, 'r') as f:
    tab = f.read()

# Parse
config = {
    'parts_list': [[1, 2]],
    'note_durations': [300] * 20,
}

parts = parse_tablature(tab, config)

# Create lesson
lesson = Lesson(name="My Song", parts=parts)

# Print for debugging
if __name__ == "__main__":
    print_lesson_code(parts, "My Song", "Awesome riff")
```

Then run it directly in VSCode: `python lessons/my_song.py`

## Tips

- **Always run `print_parse_info()` first** to understand your tablature structure
- **Use `print_lesson_code()` to generate boilerplate** then customize
- **Start with all bars in one part** `[[1,2,3,4]]`, test, then split
- **Keep tab files simple** - one riff/section per file works best

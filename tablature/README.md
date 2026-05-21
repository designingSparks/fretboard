# Tablature Parser

Tools for converting ASCII guitar tablature into playable lesson Parts for the Fretboard application.

## Contents

- **tablature_parser.py** - Main parser module
- **TABLATURE_PARSER_GUIDE.md** - Complete documentation and usage guide
- **EXAMPLE_USAGE.md** - Code examples and common patterns
- **money_for_nothing.py** - Example lesson using the parser
- **money_for_nothing.txt** - Example tablature file

## Quick Start

### 1. Analyze a Tablature File

```bash
python analyze_tab.py tablature/your_song.txt
```

### 2. Create a Lesson

```python
from tablature.tablature_parser import parse_tablature, print_lesson_code

with open('tablature/your_song.txt', 'r') as f:
    tab = f.read()

config = {
    'parts_list': [[1, 2], [3, 4]],
    'note_durations': [300] * 28,
}

parts = parse_tablature(tab, config)
print_lesson_code(parts, "Song Title", "Description", "Artist")
```

### 3. Copy/Paste and Customize

Copy the printed code into a new lesson file and customize as needed.

## Documentation

See [TABLATURE_PARSER_GUIDE.md](TABLATURE_PARSER_GUIDE.md) for complete documentation.

See [EXAMPLE_USAGE.md](EXAMPLE_USAGE.md) for code examples.

## Import Options

You can import from the package in two ways:

```python
# Direct import from module
from tablature.tablature_parser import parse_tablature, print_parse_info

# Convenient package-level import
from tablature import parse_tablature, print_parse_info
```

## Available Functions

- `parse_tablature(tab_text, config)` - Parse tab into Part objects
- `print_parse_info(tab_text)` - Analyze tablature structure
- `print_part_code(part, ...)` - Print Part as copy/paste Python code
- `print_lesson_code(parts, ...)` - Print complete lesson file code
- `split_by_bars(tab_text)` - Split tab into individual bars
- `extract_notes_from_bars(bars, bar_indices)` - Get unique notes
- `create_play_sequence_from_bars(bars, bar_indices, durations)` - Build sequences

## Utilities (Project Root)

- **analyze_tab.py** - Command-line tool to analyze tablature files
- **generate_lesson_code.py** - Interactive lesson code generator

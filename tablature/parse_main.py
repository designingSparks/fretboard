"""
This is the main entry point for parsing tablature files.
Uses the tablature_parser module to convert tablature files into playable Parts.

Usage:
    python parse_main.py <tablature_file> [options]

Example:
    python parse_main.py money_for_nothing.txt
"""

import sys
import os
import argparse

# Add parent directory to path for imports when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.lesson_model import Lesson
from tablature.tablature_parser import parse_tablature, print_part_code


def parse_file(tab_file, config):
    """Parse a tablature file with the given configuration."""
    # Handle both running from project root and from tablature directory
    if not os.path.isabs(tab_file):
        # Try relative to project root first
        project_path = os.path.join('tablature', tab_file)
        if os.path.exists(project_path):
            tab_file = project_path
        # If not found and not already in tablature dir, use as-is

    if not os.path.exists(tab_file):
        print(f"Error: File '{tab_file}' not found")
        sys.exit(1)

    print(f"Parsing tablature file: {tab_file}")

    with open(tab_file, 'r') as f:
        tab_text = f.read()

    # Parse the tablature into Part objects
    parts = parse_tablature(tab_text, config)

    # Print code for each part
    for i, part in enumerate(parts, 1):
        print(f"\n# Part {i}:")
        print_part_code(part, f'part{i}', f'PART{i}_NOTES', f'PART{i}_SEQUENCE')

    return parts


def get_default_config():
    """Return default configuration for Money for Nothing."""
    return {
        # Bars 1-2 for first part, bars 3-4 for second part
        'parts_list': [[1, 2], [3, 4]],

        # Note durations in milliseconds
        # Each note/chord gets 300ms (adjust for desired tempo)
        'note_durations': [300] * 28,

        # Names for each part
        'part_names': [
            'Intro Riff - Bars 1-2',
            'Intro Riff - Bars 3-4'
        ],

        # Descriptions
        'part_descriptions': [
            'First half of the iconic intro riff',
            'Second half with the descending line'
        ]
    }


def main():
    """Main entry point for tablature parsing."""
    parser = argparse.ArgumentParser(
        description='Parse guitar tablature files into playable Parts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Parse Money for Nothing tablature:
    python parse_main.py money_for_nothing.txt

  Parse a custom tablature file:
    python parse_main.py path/to/your_tab.txt
        """
    )

    parser.add_argument(
        'tab_file',
        nargs='?',
        default='money_for_nothing.txt',
        help='Tablature file to parse (default: money_for_nothing.txt)'
    )

    args = parser.parse_args()

    # Use default configuration
    # TODO: In future, could load config from JSON file or command-line args
    config = get_default_config()

    # Parse the file
    parse_file(args.tab_file, config)


if __name__ == "__main__":
    main()


# Example lesson creation (commented out)
# lesson = Lesson(
#     name="Money for Nothing - Intro Riff",
#     parts=parts,
#     description="Learn the iconic intro riff from Dire Straits' Money for Nothing. "
#                 "This riff features a syncopated rhythm on the lower strings with "
#                 "melodic embellishments. Pay attention to the timing and let notes ring where indicated.",
#     author="Dire Straits (Mark Knopfler)",
#     difficulty="Intermediate",
#     use_sharp=True,
#     metadata={
#         'tags': ['rock', 'riff', '80s', 'classic rock', 'intermediate'],
#         'estimated_time_minutes': 15,
#         'year': 1985,
#         'tempo_bpm': 138,
#         'key': 'G minor',
#     }
# )

# Alternative configuration examples:
#
# If you want all 4 bars as a single part:
# config = {
#     'parts_list': [[1, 2, 3, 4]],
#     'note_durations': [300] * 30,  # Adjust count as needed
#     'part_names': ['Complete Intro Riff']
# }
#
# If you want to practice each bar separately:
# config = {
#     'parts_list': [[1], [2], [3], [4]],
#     'note_durations': [300] * 30,
#     'part_names': ['Bar 1', 'Bar 2', 'Bar 3', 'Bar 4']
# }

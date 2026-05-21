#!/usr/bin/env python3
"""
Quick utility to analyze a tablature file.

Usage:
    python analyze_tab.py lessons/your_song.txt
"""

import sys
from tablature.tablature_parser import print_parse_info


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_tab.py <tablature_file>")
        print("Example: python analyze_tab.py lessons/money_for_nothing.txt")
        sys.exit(1)

    tab_file = sys.argv[1]

    try:
        with open(tab_file, 'r') as f:
            tab_text = f.read()

        print(f"Analyzing: {tab_file}")
        print("=" * 60)
        print()

        print_parse_info(tab_text)

        print()
        print("=" * 60)
        print("Next steps:")
        print("1. Copy the suggested note_durations length")
        print("2. Define your parts_list (which bars go in each part)")
        print("3. Create a lesson file using the parser")
        print()
        print("See tablature/TABLATURE_PARSER_GUIDE.md for detailed instructions.")

    except FileNotFoundError:
        print(f"Error: File '{tab_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error analyzing tablature: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

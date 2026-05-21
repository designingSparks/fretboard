#!/usr/bin/env python3
"""
Utility to generate Python lesson code from tablature files.

Usage:
    python generate_lesson_code.py lessons/your_song.txt

This script parses a tablature file and prints formatted Python code
that can be copy/pasted into a lesson file.
"""

import sys
from tablature.tablature_parser import parse_tablature, print_lesson_code


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_lesson_code.py <tablature_file>")
        print("Example: python generate_lesson_code.py lessons/money_for_nothing.txt")
        sys.exit(1)

    tab_file = sys.argv[1]

    try:
        with open(tab_file, 'r') as f:
            tab_text = f.read()

        # Prompt user for configuration
        print("=" * 70)
        print("Tablature to Lesson Code Generator")
        print("=" * 70)
        print()

        # Get lesson info
        lesson_name = input("Lesson name: ").strip() or "My Lesson"
        author = input("Artist/Author: ").strip()
        description = input("Description: ").strip()
        difficulty = input("Difficulty (Beginner/Intermediate/Advanced) [Intermediate]: ").strip() or "Intermediate"

        print()
        print("Enter bar groupings for parts.")
        print("Example: [[1,2], [3,4]] means bars 1-2 = part 1, bars 3-4 = part 2")
        parts_list_str = input("Parts list [[1,2,3,4]]: ").strip() or "[[1,2,3,4]]"

        try:
            parts_list = eval(parts_list_str)
        except:
            print("Error: Invalid parts_list format. Using default [[1,2,3,4]]")
            parts_list = [[1, 2, 3, 4]]

        duration = input("Note duration in ms [300]: ").strip()
        duration = int(duration) if duration else 300

        # Estimate total events (rough estimate, will be adjusted by parser)
        total_bars = max(max(group) for group in parts_list)
        estimated_events = total_bars * 8  # Rough estimate

        print()
        print(f"Estimated events: ~{estimated_events} (will be auto-adjusted)")
        print()
        print("=" * 70)
        print("GENERATED LESSON CODE")
        print("=" * 70)
        print()

        # Configure parser
        config = {
            'parts_list': parts_list,
            'note_durations': [duration] * 100,  # Large buffer, parser will handle
            'part_names': [f"Part {i+1}" for i in range(len(parts_list))],
        }

        # Parse and print
        parts = parse_tablature(tab_text, config)
        print_lesson_code(
            parts,
            lesson_name=lesson_name,
            lesson_description=description,
            author=author,
            difficulty=difficulty
        )

        print()
        print("=" * 70)
        print("Copy the code above and paste into a new lesson file!")
        print("=" * 70)

    except FileNotFoundError:
        print(f"Error: File '{tab_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

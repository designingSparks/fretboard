"""
Lesson scanning and metadata extraction.

This module provides functionality to scan the lessons directory and extract
metadata from lesson files for display in the lesson browser.
"""

from typing import List, Dict, Optional
from models.lesson_loader import LessonLoader


def _infer_key_from_filename(filename: str) -> Optional[str]:
    """
    Infer the musical key from the lesson filename.

    Args:
        filename: Lesson filename (without .py extension)

    Returns:
        Musical key (e.g., 'C', 'G', 'Bb') or None if not found

    Examples:
        'c_maj_triad' -> 'C'
        'g_maj_pentatonic' -> 'G'
        'bflat_maj_triad' -> 'Bb'
        'a_maj_triad' -> 'A'
    """
    # Extract first word from filename
    parts = filename.split('_')
    if not parts:
        return None

    first_part = parts[0]

    # Map common flat/sharp spellings
    note_map = {
        'bflat': 'Bb',
        'csharp': 'C#',
        'dflat': 'Db',
        'dsharp': 'D#',
        'eflat': 'Eb',
        'fsharp': 'F#',
        'gflat': 'Gb',
        'gsharp': 'G#',
        'aflat': 'Ab',
        'asharp': 'A#',
    }

    if first_part in note_map:
        return note_map[first_part]

    # Single letter notes (a-g)
    if len(first_part) == 1 and first_part.lower() in 'abcdefg':
        return first_part.upper()

    return None


def _infer_type_from_filename(filename: str) -> Optional[str]:
    """
    Infer the lesson type from the filename.

    Args:
        filename: Lesson filename (without .py extension)

    Returns:
        Lesson type (e.g., 'Triad', 'Scale', 'Riff') or None

    Examples:
        'c_maj_triad' -> 'Triad'
        'g_maj_pentatonic' -> 'Scale'
        'beginner_c_major' -> 'Scale'
    """
    filename_lower = filename.lower()

    if 'triad' in filename_lower:
        return 'Triad'
    elif 'scale' in filename_lower or 'pentatonic' in filename_lower or 'major' in filename_lower or 'minor' in filename_lower:
        return 'Scale'
    elif 'riff' in filename_lower:
        return 'Riff'
    elif 'chord' in filename_lower:
        return 'Chord'

    return None


def scan_lessons(lessons_dir: str = "lessons") -> List[Dict[str, any]]:
    """
    Scan the lessons directory and extract metadata from all lesson files.

    This function loads all lessons, extracts their metadata into lightweight
    dictionaries, and then unloads the lesson objects to free memory.

    Args:
        lessons_dir: Path to the lessons directory (relative or absolute)

    Returns:
        List of metadata dictionaries with keys:
            - filename: Lesson filename (without .py)
            - name: Display name of the lesson
            - key: Musical key (e.g., 'C', 'G', 'Bb')
            - type: Lesson type (e.g., 'Triad', 'Scale', 'Riff')
            - difficulty: Difficulty level or None
            - description: Lesson description
            - author: Lesson author
            - part_count: Number of parts in the lesson
            - tags: List of tags from metadata
    """
    loader = LessonLoader(lessons_dir)
    lessons = loader.load_all_lessons()

    metadata_list = []

    for lesson in lessons:
        # Get the filename from the loader's cache
        # The cache keys are the filenames
        filename = None
        for cached_filename, cached_lesson in loader._lesson_cache.items():
            if cached_lesson is lesson:
                filename = cached_filename
                break

        if filename is None:
            continue

        # Extract key from metadata or infer from filename
        key = None
        if lesson.metadata and 'key' in lesson.metadata:
            key = lesson.metadata['key']
        else:
            key = _infer_key_from_filename(filename)

        # Extract type from metadata or infer from filename
        lesson_type = None
        if lesson.metadata and 'scale_type' in lesson.metadata:
            # For scales, use the scale_type
            lesson_type = 'Scale'
        else:
            lesson_type = _infer_type_from_filename(filename)

        # Extract difficulty from lesson field or metadata
        difficulty = lesson.difficulty if lesson.difficulty else None
        if not difficulty and lesson.metadata and 'difficulty' in lesson.metadata:
            difficulty = lesson.metadata['difficulty']

        # Extract tags
        tags = []
        if lesson.metadata and 'tags' in lesson.metadata:
            tags = lesson.metadata['tags']

        metadata_dict = {
            'filename': filename,
            'name': lesson.name,
            'key': key,
            'type': lesson_type,
            'difficulty': difficulty,
            'description': lesson.description,
            'author': lesson.author,
            'part_count': lesson.get_part_count(),
            'tags': tags,
        }

        metadata_list.append(metadata_dict)

    # Clear the cache to unload lessons
    loader.clear_cache()

    # Sort by name
    metadata_list.sort(key=lambda x: x['name'])

    return metadata_list

"""
Lesson loading and discovery system.

This module provides functionality to discover and load lesson files
from the lessons directory.
"""

import os
import sys
import importlib.util
from pathlib import Path
from typing import List, Optional, Dict
from models.lesson_model import Lesson


class LessonLoader:
    """
    Discovers and loads lesson files from the lessons directory.

    Supports loading lessons from Python (.py) files. Each lesson file
    must export a 'lesson' variable containing a Lesson object.
    """

    def __init__(self, lessons_dir: str = "lessons"):
        """
        Initialize the lesson loader.

        Args:
            lessons_dir: Path to the lessons directory (relative or absolute)
        """
        self.lessons_dir = Path(lessons_dir)
        if not self.lessons_dir.is_absolute():
            # Make it relative to the current working directory
            self.lessons_dir = Path.cwd() / self.lessons_dir

        self._lesson_cache: Dict[str, Lesson] = {}

    def get_available_lesson_files(self) -> List[str]:
        """
        Get a list of available lesson files in the lessons directory.

        Returns:
            List of lesson filenames (without .py extension)
            Files starting with _ or . are excluded
        """
        if not self.lessons_dir.exists():
            print(f"Warning: Lessons directory '{self.lessons_dir}' does not exist")
            return []

        lesson_files = []
        for file_path in self.lessons_dir.glob("*.py"):
            filename = file_path.stem
            # Skip template files and private modules
            if not filename.startswith('_') and not filename.startswith('.'):
                lesson_files.append(filename)

        return sorted(lesson_files)

    def load_lesson(self, filename: str) -> Optional[Lesson]:
        """
        Load a lesson from a Python file.

        Args:
            filename: Lesson filename (with or without .py extension)

        Returns:
            Lesson object if successful, None if loading failed

        Example:
            >>> loader = LessonLoader()
            >>> lesson = loader.load_lesson("beginner_c_major")
            >>> print(lesson.name)
            Beginner C Major
        """
        # Remove .py extension if present
        if filename.endswith('.py'):
            filename = filename[:-3]

        # Check cache first
        if filename in self._lesson_cache:
            return self._lesson_cache[filename]

        file_path = self.lessons_dir / f"{filename}.py"

        if not file_path.exists():
            print(f"Error: Lesson file '{file_path}' not found")
            return None

        try:
            # Dynamically import the lesson module
            spec = importlib.util.spec_from_file_location(filename, file_path)
            if spec is None or spec.loader is None:
                print(f"Error: Could not load module spec for '{file_path}'")
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Extract the lesson object
            if not hasattr(module, 'lesson'):
                print(f"Error: Lesson file '{filename}.py' must export a 'lesson' variable")
                return None

            lesson = module.lesson

            if not isinstance(lesson, Lesson):
                print(f"Error: 'lesson' in '{filename}.py' must be a Lesson instance")
                return None

            # Cache the lesson
            self._lesson_cache[filename] = lesson
            print(f"Successfully loaded lesson: {lesson.name}")
            return lesson

        except Exception as e:
            print(f"Error loading lesson '{filename}': {e}")
            import traceback
            traceback.print_exc()
            return None

    def load_all_lessons(self) -> List[Lesson]:
        """
        Load all available lessons from the lessons directory.

        Returns:
            List of successfully loaded Lesson objects
        """
        lessons = []
        for filename in self.get_available_lesson_files():
            lesson = self.load_lesson(filename)
            if lesson is not None:
                lessons.append(lesson)

        return lessons

    def reload_lesson(self, filename: str) -> Optional[Lesson]:
        """
        Reload a lesson from disk, clearing the cache.

        Useful for development when lesson files are being edited.

        Args:
            filename: Lesson filename (with or without .py extension)

        Returns:
            Lesson object if successful, None if loading failed
        """
        # Remove .py extension if present
        if filename.endswith('.py'):
            filename = filename[:-3]

        # Clear from cache
        if filename in self._lesson_cache:
            del self._lesson_cache[filename]

        # Reload
        return self.load_lesson(filename)

    def clear_cache(self):
        """Clear the lesson cache, forcing reload on next access."""
        self._lesson_cache.clear()

    def get_lesson_info(self, filename: str) -> Optional[Dict[str, any]]:
        """
        Get basic information about a lesson without fully loading it.

        Args:
            filename: Lesson filename (with or without .py extension)

        Returns:
            Dict with lesson info (name, description, part_count) or None
        """
        lesson = self.load_lesson(filename)
        if lesson is None:
            return None

        return {
            'filename': filename,
            'name': lesson.name,
            'description': lesson.description,
            'author': lesson.author,
            'part_count': lesson.get_part_count(),
            'total_duration_ms': lesson.get_total_duration_ms(),
        }


# Global loader instance for convenience
_default_loader = None


def get_default_loader() -> LessonLoader:
    """
    Get the default lesson loader instance.

    Returns:
        Default LessonLoader instance
    """
    global _default_loader
    if _default_loader is None:
        _default_loader = LessonLoader()
    return _default_loader


# Convenience functions using the default loader

def get_available_lessons() -> List[str]:
    """Get list of available lesson filenames."""
    return get_default_loader().get_available_lesson_files()


def load_lesson(filename: str) -> Optional[Lesson]:
    """Load a lesson by filename."""
    return get_default_loader().load_lesson(filename)


def load_all_lessons() -> List[Lesson]:
    """Load all available lessons."""
    return get_default_loader().load_all_lessons()

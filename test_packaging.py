"""Bundled lesson discovery must work without lesson source files on disk."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from models import lesson_loader


class BundledLessonTests(unittest.TestCase):
    def test_compiled_lessons_load_without_source_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bundled_lessons.json").write_text(
                json.dumps(["c_maj_triad"]), encoding="utf-8"
            )
            with patch.object(lesson_loader, "__file__", str(root / "models" / "lesson_loader.py")), \
                    patch.object(lesson_loader, "__compiled__", True, create=True):
                loader = lesson_loader.LessonLoader()
                self.assertFalse(loader.lessons_dir.exists())
                self.assertEqual(loader.get_available_lesson_files(), ["c_maj_triad"])
                lesson = loader.load_lesson("c_maj_triad.py")
                self.assertIsNotNone(lesson)
                self.assertEqual(lesson.name, "C major triads")
                self.assertIs(loader.load_lesson("c_maj_triad"), lesson)
                self.assertEqual(loader.load_all_lessons(), [lesson])
                with patch.object(lesson_loader.importlib, "import_module") as importer:
                    self.assertIsNone(loader.load_lesson("Gmaj_C_shape"))
                    importer.assert_not_called()

    def test_external_source_lessons_still_work_in_compiled_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "example.py").write_text(
                "from models.lesson_model import Lesson, Part\n"
                "lesson = Lesson(name='External', parts=[Part('One', [('e', 3)], [[('e', 3), 1000]])])\n",
                encoding="utf-8"
            )
            with patch.object(lesson_loader, "__compiled__", True, create=True):
                loader = lesson_loader.LessonLoader(root)
                self.assertEqual(loader.get_available_lesson_files(), ["example"])
                self.assertEqual(loader.load_lesson("example").name, "External")


if __name__ == "__main__":
    unittest.main()

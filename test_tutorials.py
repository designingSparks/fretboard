"""Directory loading and the G major E-shape tutorial's display/playback data."""

import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from main import FretboardPlayer
from models.lesson_loader import LessonLoader
from test_chord_labels import FakeAudio, FakeView
from ui.fretboard_view import FretboardView


class TutorialTests(unittest.TestCase):
    def test_tutorial_displays_full_chord_and_selects_only_each_triad_root(self):
        lesson = LessonLoader('tutorials').load_lesson('Gmaj_E_shape')
        self.assertEqual(len(lesson.parts), 1)
        chord = {('E', 3), ('A', 5), ('D', 5), ('G', 4), ('B', 3), ('e', 3)}
        triads = [(('G', 4), ('B', 3), ('e', 3)), (('D', 5), ('G', 4), ('B', 3)),
                  (('A', 5), ('D', 5), ('G', 4)), (('E', 7), ('A', 5), ('D', 5))]
        part = lesson.parts[0]
        self.assertEqual(set(part.background_notes), chord)
        self.assertEqual(len(part.play_sequence), 4)
        scripts = []
        view = SimpleNamespace(page=lambda: SimpleNamespace(runJavaScript=scripts.append))
        FretboardView.display_notes(view, part)
        args = json.loads(scripts[0][len('displayNotes('):-2])
        markers = (args['backgroundNotes'] + args['hiddenNotes'])
        self.assertEqual({(n['stringName'], n['fret']) for n in markers},
                         chord | {('E', 7)})
        self.assertEqual({(n['stringName'], n['fret']) for n in markers if n['isBackground']},
                         chord | {('E', 7)})
        self.assertEqual(args['hiddenNotes'], [])
        self.assertEqual(next(n for n in markers if n['stringName'] == 'E' and n['fret'] == 7)
                         ['backgroundColor'], '#91c2e6')
        self.assertTrue(all(note['highlight'] is None for note in markers))
        for index, (triad, root) in enumerate(zip(
                triads, [('e', 3), ('D', 5), ('D', 5), ('D', 5)])):
            self.assertEqual(part.play_sequence[index].notes, triad)
            step = args['sequenceSteps'][index]
            self.assertEqual(step['chordName'], 'G')
            self.assertEqual([(n['stringName'], n['fret']) for n in step['notes']], list(triad))
            self.assertEqual([(n['stringName'], n['fret']) for n in step['notes'] if n['isRoot']], [root])

    def test_player_loads_from_any_working_directory_and_plays_all_steps(self):
        view, audio = FakeView(), FakeAudio()
        player = FretboardPlayer(view, audio)
        changes = []
        player.part_changed.connect(lambda index, total: changes.append((index, total)))
        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                lesson = player.load('tutorials', 'Gmaj_E_shape.py')
            finally:
                os.chdir(original_cwd)
        self.assertIs(player.current_lesson, lesson)
        self.assertEqual(view.title, lesson.name)
        self.assertIs(audio.part, lesson.parts[0])
        self.assertEqual(changes, [(0, 1)])
        audio.is_playing = True
        audio.playback_started.emit()
        for index in range(4):
            audio.highlight_note_index.emit(index)
            self.assertEqual(view.calls[-1], ('step', index))
        self.assertFalse(player.can_go_next())
        self.assertFalse(player.can_go_previous())
        existing = player.load('lessons', 'c_maj_triad')
        self.assertEqual(existing.name, 'C major triads')
        self.assertEqual(view.title, existing.name)

    def test_loading_before_browser_ready_uses_latest_lesson_title_and_part(self):
        view, audio = FakeView(), FakeAudio()
        player = FretboardPlayer(view, audio)
        with patch.object(view, 'isVisible', return_value=False):
            player.load('lessons', 'c_maj_triad')
            lesson = player.load('tutorials', 'Gmaj_E_shape', part_index=0)
            self.assertFalse(view.calls)
            view.view_loaded.emit()
        self.assertEqual(view.title, lesson.name)
        self.assertEqual(view.calls, [('display', lesson.parts[0].play_sequence)])

    def test_directory_caches_do_not_mix_identical_filenames(self):
        source = """from models.lesson_model import Lesson, Part
lesson = Lesson({name!r}, [Part('One', [('e', 3)], [[('e', 3), 1000]])])
"""
        player = FretboardPlayer(FakeView(), FakeAudio())
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / 'first', Path(directory) / 'second'
            for folder in (first, second):
                folder.mkdir()
                (folder / 'same.py').write_text(source.format(name=folder.name))
            a = player.load(first, 'same')
            b = player.load(second, 'same')
            self.assertEqual((a.name, b.name), ('first', 'second'))
            self.assertIs(player.load(first / '.', 'same.py'), a)
            self.assertIs(player.load(second, 'same'), b)

    def test_failed_load_or_invalid_part_preserves_current_lesson_and_playback(self):
        view, audio = FakeView(), FakeAudio()
        player = FretboardPlayer(view, audio)
        lesson = player.load('tutorials', 'Gmaj_E_shape')
        audio.is_playing = True
        calls = list(view.calls)
        self.assertIsNone(player.load('tutorials', 'does_not_exist'))
        self.assertIsNone(player.load('tutorials', 'Gmaj_E_shape', part_index=1))
        self.assertIs(player.current_lesson, lesson)
        self.assertIs(audio.part, lesson.parts[0])
        self.assertTrue(audio.is_playing)
        self.assertEqual(view.calls, calls)


if __name__ == '__main__':
    unittest.main()

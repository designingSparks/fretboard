"""Run: python -m unittest test_sequence_outlines -v

Set RUN_FRETBOARD_BROWSER_TESTS=1 to also exercise the real Qt web view.
"""

import json
import os
import unittest
from dataclasses import replace

from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide6.QtWidgets import QApplication

from models.lesson_model import Part
from models.lesson_loader import LessonLoader
from models.sequence_step import parse_sequence_row
from ui.fretboard_view import FretboardView


class OfflineRequests(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        if info.requestUrl().scheme() in ('http', 'https'):
            info.block(True)


@unittest.skipUnless(os.environ.get('RUN_FRETBOARD_BROWSER_TESTS') == '1',
                     'Set RUN_FRETBOARD_BROWSER_TESTS=1 for Qt browser checks')
class SequenceOutlineBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.view = FretboardView()
        cls.interceptor = OfflineRequests(cls.view)
        cls.view.page().profile().setUrlRequestInterceptor(cls.interceptor)
        cls.view.resize(1850, 600)
        loop = QEventLoop()
        loaded = []
        cls.view.loadFinished.connect(lambda ok: (loaded.append(ok), loop.quit()))
        QTimer.singleShot(10000, loop.quit)
        cls.view.show()
        loop.exec()
        if not loaded or not loaded[0]:
            raise RuntimeError('Fretboard did not load')
        cls.loader = LessonLoader()

    @classmethod
    def tearDownClass(cls):
        cls.view.close()

    def javascript(self, code):
        loop = QEventLoop()
        results = []
        self.view.page().runJavaScript(code, lambda value: (results.append(value), loop.quit()))
        QTimer.singleShot(5000, loop.quit)
        loop.exec()
        self.assertTrue(results, 'JavaScript callback timed out')
        return results[0]

    def display(self, part):
        self.view.display_notes(part)
        # Wait for layout/animation-frame work, including on offscreen Qt.
        loop = QEventLoop()
        QTimer.singleShot(150, loop.quit)
        loop.exec()

    def snapshot(self):
        return json.loads(self.javascript("""JSON.stringify(
            [...document.querySelectorAll('[data-sequence-group]')].map(group => {
                const bounds = group.getBBox();
                return {
                    notes: +group.getAttribute('data-note-count'),
                    hull: +group.getAttribute('data-hull-count'),
                    width: bounds.width, height: bounds.height,
                    x: bounds.x, y: bounds.y,
                    path: group.getAttribute('d'),
                };
            })
        )"""))

    def test_all_c_major_parts_and_another_key(self):
        lesson = self.loader.load_lesson('c_maj_triad')
        parts = lesson.parts + [replace(
            self.loader.load_lesson('g_maj_triad').parts[0],
            circle_sequence_elements=True,
        )]
        for part in parts:
            with self.subTest(part=part.name):
                self.display(part)
                groups = self.snapshot()
                self.assertEqual(len(groups), len(part.play_sequence))
                for group, row in zip(groups, part.play_sequence):
                    self.assertEqual(group['notes'], len(set(parse_sequence_row(row).notes)))
                    self.assertLessEqual(group['hull'], group['notes'])
                    self.assertGreaterEqual(group['x'], 0)
                    self.assertGreaterEqual(group['y'], 0)

    def test_background_colors_and_playback_only_visibility(self):
        from models.background_layer import BackgroundLayer
        from models.sequence_step import SequenceStep

        part = Part('Colored', [('G', 4)], [
            SequenceStep(notes=(('e', 3), ('E', 7)), duration_ms=1000, chord_name='G'),
            SequenceStep(notes=(('G', 0),), duration_ms=1000, chord_name='G'),
            SequenceStep(notes=(), duration_ms=1000),
        ], background_layers=[
            BackgroundLayer(notes=[('e', 3)], color='#123456'),
            BackgroundLayer(notes=[('e', 3), ('B', 3)], color='#abcdef'),
        ], highlight_chord_root=True, circle_sequence_elements=True)
        self.display(part)

        def marker(string, fret):
            return json.loads(self.javascript(f'''JSON.stringify((() => {{
                const note = document.querySelector('[data-string="{string}"] '
                    + '.{"open-string-note" if fret == 0 else "note"}[data-fret="{fret}"]');
                const style = getComputedStyle(note);
                return {{visible: style.visibility !== 'hidden', color: style.backgroundColor,
                    labelVisible: note.openStringLabel ? !note.openStringLabel.hidden : null}};
            }})())'''))

        # The first labelled step is selected on load, including the extra low B.
        self.assertTrue(marker(5, 7)['visible'])
        self.assertEqual(marker(0, 3)['color'], 'rgb(231, 76, 60)')
        self.javascript('clearNoteHighlights()')
        self.assertEqual(marker(0, 3)['color'], 'rgb(18, 52, 86)')
        self.assertEqual(marker(1, 3)['color'], 'rgb(171, 205, 239)')
        self.assertTrue(marker(2, 4)['visible'])
        self.assertFalse(marker(5, 7)['visible'])
        self.assertFalse(marker(2, 0)['visible'])
        self.assertTrue(marker(2, 0)['labelVisible'])
        self.javascript('setChordPlaybackState("playing"); highlightSequenceStep(1)')
        self.assertTrue(marker(2, 0)['visible'])
        self.assertFalse(marker(2, 0)['labelVisible'])
        self.javascript('setChordPlaybackState("paused")')
        self.assertTrue(marker(2, 0)['visible'])
        self.javascript('setChordPlaybackState("playing"); highlightSequenceStep(2)')
        self.assertFalse(marker(2, 0)['visible'])  # Rest restores the background.
        self.assertEqual(marker(0, 3)['color'], 'rgb(18, 52, 86)')
        self.javascript('setChordPlaybackState("stopped"); '
                        'document.querySelectorAll(".chord-label")[1].click()')
        self.assertTrue(marker(2, 0)['visible'])
        self.javascript('highlightNote("E", 7)')
        self.assertFalse(marker(2, 0)['visible'])
        self.assertTrue(marker(5, 7)['visible'])
        self.javascript('clearNoteHighlights()')
        self.assertFalse(marker(5, 7)['visible'])

    def test_tutorial_extra_low_e_restores_blue_background_after_selection(self):
        for name, fret in [('Gmaj_E_shape', 7), ('GMaj_A_shape', 15), ('Gmaj_C_shape', 10)]:
            with self.subTest(tutorial=name):
                part = LessonLoader('tutorials').load_lesson(name).parts[0]
                self.display(part)
                selector = f'td[data-string="5"][data-fret="{fret}"] .note'
                visible = f'getComputedStyle(document.querySelector({json.dumps(selector)})).visibility'
                color = f'getComputedStyle(document.querySelector({json.dumps(selector)})).backgroundColor'
                self.assertEqual(self.javascript(visible), 'visible')
                self.assertEqual(self.javascript(color), 'rgb(145, 194, 230)')
                self.javascript('document.querySelectorAll(".chord-label")[3].click()')
                self.assertEqual(self.javascript(visible), 'visible')
                self.javascript('clearNoteHighlights()')
                self.assertEqual(self.javascript(visible), 'visible')
                self.assertEqual(self.javascript(color), 'rgb(145, 194, 230)')

    def test_g_c_d_root_follows_each_triad_and_clears_on_stop(self):
        from constants import FRETBOARD_NOTES_SHARP, STRING_ID
        from models.sequence_step import parse_sequence_row

        def roots():
            return json.loads(self.javascript("""JSON.stringify(
                [...document.querySelectorAll('.highlight1')].map(note => [
                    GUITAR_TUNING[+note.parentElement.dataset.string].name,
                    +note.dataset.fret
                ])
            )"""))

        for part in self.loader.load_lesson('g_c_d_major_triads').parts:
            self.display(part)
            self.assertEqual(roots(), [])
            self.javascript('setChordPlaybackState("playing")')
            for index, row in enumerate(part.play_sequence):
                step = parse_sequence_row(row)
                with self.subTest(part=part.name, index=index):
                    self.javascript(f'highlightSequenceStep({index})')
                    expected = [[s, f] for s, f in step.notes
                                if FRETBOARD_NOTES_SHARP[STRING_ID.index(s)][f] == step.chord_name[0]]
                    self.assertEqual(len(expected), 1)
                    self.assertEqual(roots(), expected)
            self.javascript('setChordPlaybackState("stopped")')
            self.assertEqual(roots(), [])
            self.javascript('document.querySelectorAll(".chord-label")[1].click()')
            step = parse_sequence_row(part.play_sequence[1])
            self.assertEqual(roots(), [[s, f] for s, f in step.notes
                                      if FRETBOARD_NOTES_SHARP[STRING_ID.index(s)][f] == 'C'])

        # Fixed root coloring in existing lessons survives playback resets.
        self.display(self.loader.load_lesson('g_maj_triad').parts[0])
        fixed_roots = roots()
        self.assertTrue(fixed_roots)
        self.javascript('setChordPlaybackState("playing"); highlightSequenceStep(0); '
                        'setChordPlaybackState("stopped")')
        self.assertEqual(roots(), fixed_roots)

    def test_spread_notes_missing_highlights_and_wrapping_distance(self):
        part = Part('Wide', [('e', 0)], [[('e', 0), ('e', 12), 1000]],
                    circle_sequence_elements=True, wrapping_distance=8,
                    fillet_corners=True, fillet_radius=24)
        self.display(part)
        small = self.snapshot()[0]
        self.assertEqual(small['notes'], 2)  # Missing highlight was displayed.
        self.assertGreater(small['width'], small['height'] * 5)
        self.assertAlmostEqual(small['height'], 46, delta=1)
        self.display(replace(part, wrapping_distance=20))
        large = self.snapshot()[0]
        self.assertAlmostEqual(large['height'] - small['height'], 24, delta=0.1)
        self.javascript('window.dispatchEvent(new Event("resize"))')
        self.display(replace(part, wrapping_distance=20))
        self.assertEqual(self.snapshot()[0], large)

    def test_single_shared_repeated_notes_rests_and_disabled_switch(self):
        part = Part('Groups', [('e', 0)], [
            [('e', 0), ('B', 1), 1000],
            [('B', 1), ('e', 0), 1000],
            [('e', 0), ('e', 0), 1000],
            [1000],
        ], circle_sequence_elements=True)
        self.display(part)
        groups = self.snapshot()
        self.assertEqual(len(groups), 3)
        self.assertEqual(groups[0], groups[1])
        self.assertEqual(groups[2]['notes'], 1)
        self.javascript('clearNoteHighlights()')
        self.assertEqual(self.snapshot(), groups)
        self.display(replace(part, circle_sequence_elements=False))
        self.assertEqual(self.snapshot(), [])

class SequenceOutlineModelTests(unittest.TestCase):
    def test_model_validation_and_default(self):
        part = Part('Default', [('e', 0)], [[('e', 0), 1000]])
        self.assertFalse(part.circle_sequence_elements)
        self.assertEqual(part.wrapping_distance, 8)
        self.assertFalse(part.fillet_corners)
        self.assertEqual(part.fillet_radius, 24)
        for setting in ('wrapping_distance', 'fillet_radius'):
            for value in (-1, float('nan'), float('inf'), '8', True):
                with self.subTest(setting=setting, value=value), self.assertRaises(ValueError):
                    replace(part, **{setting: value})
        with self.assertRaises(ValueError):
            replace(part, fillet_corners='yes')
        self.assertEqual(replace(part, wrapping_distance=0).wrapping_distance, 0)
        self.assertEqual(replace(part, fillet_radius=0).fillet_radius, 0)

    def test_bridge_keeps_rows_and_adds_missing_markers(self):
        class RecordingView:
            def page(self):
                return self

            def runJavaScript(self, script):
                self.script = script

        view = RecordingView()
        part = Part(
            'Groups', [('e', 0)], play_sequence=[
                [('e', 0), ('B', 1), 1000],
                [('B', 1), ('e', 0), 1000],
                [('G', 5), ('G', 5), 500], [500],
            ], circle_sequence_elements=True, wrapping_distance=12,
            fillet_corners=True, fillet_radius=10,
        )
        FretboardView.display_notes(view, part)
        args = json.loads(view.script[len('displayNotes('):-2])
        notes, groups, distance = (args['backgroundNotes'] + args['hiddenNotes']), args['sequenceGroups'], args['wrappingDistance']
        self.assertEqual(len(notes), 3)
        self.assertEqual([len(group) for group in groups], [2, 2, 1])
        self.assertEqual(groups[0], list(reversed(groups[1])))
        self.assertEqual(distance, 12)
        self.assertEqual([args['filletCorners'], args['filletRadius']], [True, 10])
        FretboardView.display_notes(view, Part('Default', [('e', 0)], [[500]]))
        args = json.loads(view.script[len('displayNotes('):-2])
        self.assertEqual(args['sequenceGroups'], [])
        self.assertEqual([args['filletCorners'], args['filletRadius']], [False, 24])

    def test_lessons_and_template_load(self):
        from lessons import _template
        self.assertIsNotNone(_template.lesson)
        loader = LessonLoader()
        for name in loader.get_available_lesson_files():
            self.assertIsNotNone(loader.load_lesson(name), name)
        self.assertTrue(all(part.circle_sequence_elements and part.fillet_corners
                            for part in loader.load_lesson('c_maj_triad').parts))


if __name__ == '__main__':
    unittest.main()

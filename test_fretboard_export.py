"""Run: QT_QPA_PLATFORM=offscreen python -m unittest discover -s Modular -p test_fretboard_export.py

Set FRETBOARD_BROWSER_TEST=1 to also exercise the actual Qt browser (requires
an environment that permits Chromium to start).
"""

import json
from dataclasses import replace
import os
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import xml.etree.ElementTree as ET

from PySide6.QtCore import QByteArray, QEventLoop, QTimer, QRect, QSize
from PySide6.QtGui import QImage
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

from fretboard_export import FretboardExporter, SVG_NS, add_svg_watermark, outline_svg_text, part_filename, save_png, visible_part_content
from models.lesson_loader import load_lesson
from models.lesson_model import Lesson, Part
from models.background_layer import BackgroundLayer, resolve_background_notes
from models.sequence_step import SequenceStep


SAMPLE = '''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="260" viewBox="0 0 1600 260">
<rect x="0" y="0" width="1600" height="260" fill="white"/>
<ellipse cx="40" cy="50" rx="15" ry="15" fill="#fec1bb"/>
<text x="40" y="50" fill="black" font-family="Arial" font-size="14" font-weight="700">G</text>
<text x="1570" y="230" fill="#666" font-family="Arial" font-size="14" font-weight="400">24</text>
<path d="M 20 90 L 1580 90" stroke="#527a8a" stroke-width="2" fill="none"/>
</svg>'''

GEOMETRY = {'left': 50, 'right': 1590, 'strings': {
    name: {'y': 30 + index * 35, 'width': 3}
    for index, name in enumerate(('e', 'B', 'G', 'D', 'A', 'E'))
}}
PLACEMENTS = {'GBe': ('E', 'A'), 'DGB': ('E', 'A'),
              'ADG': ('B', 'e'), 'EAD': ('B', 'e')}


class FakeView:
    """Asynchronous browser boundary; geometry/rasterization still use real Qt."""
    def __init__(self):
        self.fret_count = 15
        self.parts = []
        self.ready = False
        self.polls = 0
        self.scripts = []

    def page(self):
        return self

    def display_notes(self, notes, colors, **options):
        self.parts.append((notes, colors, options))
        self.ready = False

    def runJavaScript(self, script, callback):
        self.scripts.append(script)
        if script.startswith('JSON.stringify'):
            self.polls += 1
            value = json.dumps({'svg': SAMPLE, 'geometry': GEOMETRY}) if self.ready else 'null'
            self.ready = True
        else:
            value = True
        QTimer.singleShot(0, lambda: callback(value))


class ExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_real_lesson_filenames_and_string_case(self):
        lesson = load_lesson('g_maj_triad')
        self.assertEqual([part_filename('g_maj_triad', part) for part in lesson.parts],
                         [f'g_maj_triad_{strings}' for strings in ('GBe', 'DGB', 'ADG', 'EAD')])
        with self.assertRaises(ValueError):
            part_filename('../outside', lesson.parts[0])

    def test_export_passes_filtered_layers_without_changing_precedence(self):
        part = Part('Layers', [], [[('e', 3), 1000]], background_layers=[
            BackgroundLayer(notes=[('E', 3), ('B', 20)], color='#123'),
            BackgroundLayer(notes=[('E', 3), ('A', 5)], color='#456'),
        ])
        view = FakeView()
        exporter = FretboardExporter(view)
        loop = QEventLoop()
        failures = []
        exporter.finished.connect(loop.quit)
        exporter.failed.connect(lambda error: (failures.append(error), loop.quit()))
        timeout = QTimer()
        timeout.setSingleShot(True)
        timeout.timeout.connect(loop.quit)
        timeout.start(5000)
        with tempfile.TemporaryDirectory() as directory, patch(
                'fretboard_export.load_lesson', return_value=Lesson('Layers', [part])):
            exporter.export_lesson('layers', directory, formats=('svg',))
            loop.exec()
        timeout.stop()
        self.assertFalse(failures)
        self.assertFalse(exporter.busy)
        notes, _, options = view.parts[0]
        layers = options['background_layers']
        self.assertEqual([layer.notes for layer in layers], [(('E', 3),), (('E', 3), ('A', 5))])
        self.assertEqual(resolve_background_notes(notes, layers)[('E', 3)]['backgroundColor'], '#123')
        self.assertIn(('B', 20), part.background_layers[0].notes)  # Source remains intact.

    def test_last_fret_triads_are_omitted_and_logged_once(self):
        lesson = load_lesson('g_maj_triad')
        with self.assertLogs('glead.fretboard_export', level='WARNING') as logs:
            results = [visible_part_content(part, 15) for part in lesson.parts]
        self.assertEqual(len(logs.output), 2)  # GBe reaches 16; EAD reaches exactly 15.
        self.assertTrue(all('could not be rendered' in message for message in logs.output))
        self.assertEqual([len(steps) for _, steps in results], [3, 4, 4, 3])
        self.assertEqual([len(notes) for notes, _ in results], [9, 12, 12, 9])
        for notes, steps in results:
            self.assertTrue(all(fret < 15 for _, fret in notes))
            self.assertEqual(set(notes), {note for step in steps for note in step.notes})
        self.assertTrue(all(len(part.play_sequence) == 4 for part in lesson.parts))

    def test_skipped_triad_keeps_notes_shared_with_a_visible_triad(self):
        base = load_lesson('g_maj_triad').parts[0]
        visible = SequenceStep(notes=(('e', 3), ('B', 3), ('G', 4)), duration_ms=1000)
        skipped = SequenceStep(notes=(('e', 3), ('B', 15), ('G', 12)), duration_ms=1000)
        part = replace(base, background_notes=list(dict.fromkeys(visible.notes + skipped.notes)),
                       play_sequence=[visible, skipped])
        with self.assertLogs('glead.fretboard_export', level='WARNING'):
            notes, steps = visible_part_content(part, 15)
        self.assertEqual(set(notes), set(visible.notes))
        self.assertEqual(steps, [visible])

    def test_final_fret_can_be_included_but_beyond_board_is_still_omitted(self):
        part = load_lesson('g_maj_triad').parts[0]
        notes, steps = visible_part_content(part, 16, include_last_fret=True)
        self.assertEqual(len(steps), 4)
        self.assertEqual(set(notes), set(part.background_notes))
        self.assertIn(('G', 16), steps[-1].notes)
        with self.assertLogs('glead.fretboard_export', level='WARNING'):
            notes, steps = visible_part_content(part, 15, include_last_fret=True)
        self.assertEqual(len(steps), 3)
        self.assertNotIn(('G', 16), notes)
        self.assertNotIn(('e', 15), notes)  # Omit the whole out-of-range triad.

    def test_bad_geometry_cannot_resize_window_beyond_screen(self):
        from main_export import ExportWindow
        sizes = []
        window = SimpleNamespace(
            screen=lambda: SimpleNamespace(availableGeometry=lambda: QRect(0, 0, 1440, 900)),
            frameGeometry=lambda: QRect(0, 0, 1200, 408), size=lambda: QSize(1200, 380),
            statusBar=lambda: SimpleNamespace(sizeHint=lambda: QSize(100, 22)),
            setMinimumSize=lambda w, h: sizes.append((w, h)), resize=lambda w, h: sizes.append((w, h)),
        )
        ExportWindow._fit_diagram(window, 14573, 6923)
        self.assertEqual(sizes, [(1440, 872), (1440, 872)])

    def test_vector_labels_and_full_width_png(self):
        svg = outline_svg_text(SAMPLE, 'G major triads')
        root = ET.fromstring(svg)
        self.assertEqual(root.find(f'{{{SVG_NS}}}title').text, 'G major triads')
        self.assertFalse(root.findall(f'.//{{{SVG_NS}}}text'))
        self.assertFalse(root.findall(f'.//{{{SVG_NS}}}image'))
        labels = root.findall(f'.//{{{SVG_NS}}}path[@aria-label]')
        self.assertEqual([label.attrib['aria-label'] for label in labels], ['G', '24'])
        self.assertTrue(all(label.attrib['d'] for label in labels))
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / 'test.png'
            save_png(svg, filename)
            image = QImage(str(filename))
            self.assertEqual((image.width(), image.height()), (3200, 520))
            self.assertEqual(image.pixelColor(5, 5).name(), '#ffffff')
            self.assertEqual(image.pixelColor(58, 100).name(), '#fec1bb')
            # The far right survives even when the display window is narrower.
            self.assertEqual(image.pixelColor(3000, 180).name(), '#527a8a')
            self.assertTrue(any(image.pixelColor(x, y).name() != '#ffffff'
                                for x in range(3120, 3160) for y in range(446, 474)))

    def test_invalid_svg_fails_without_writing_png(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / 'bad.png'
            with self.assertRaises(ValueError):
                save_png(b'not svg', filename)
            self.assertFalse(filename.exists())

    def test_watermark_fits_gap_and_long_text_shrinks_to_fretted_area(self):
        # Tight geometry forces vertical and horizontal fitting, including descenders.
        geometry = {'left': 100, 'right': 260, 'strings': {
            'E': {'y': 100, 'width': 4}, 'A': {'y': 80, 'width': 3},
        }}
        for text in ('learnleadfast.ch', 'A very long website address with descenders gyp' * 5):
            svg = add_svg_watermark(outline_svg_text(SAMPLE, 'Test'), text,
                                    ('A', 'E'), 0.25, geometry, 'Arial')
            renderer = QSvgRenderer(QByteArray(svg))
            bounds = renderer.boundsOnElement('watermark')
            self.assertAlmostEqual(bounds.center().x(), 180, places=3)
            self.assertAlmostEqual(bounds.center().y(), 90, places=3)
            self.assertGreaterEqual(bounds.left(), 108 - 0.001)
            self.assertLessEqual(bounds.right(), 252 + 0.001)
            self.assertGreaterEqual(bounds.top(), 86 - 0.001)
            self.assertLessEqual(bounds.bottom(), 94 + 0.001)
            self.assertFalse(ET.fromstring(svg).findall(f'.//{{{SVG_NS}}}text'))

    def test_watermark_settings_fail_before_writing(self):
        bad_options = [
            {'watermark_between': {'GBE': ('E', 'A')}},
            *({'watermark_between': {'GBe': pair}} for pair in
              [('E', 'G'), ('e', 'A'), ('E', 'E'), ('X', 'A'), ('E',), 'EA']),
            {'watermark_between': [('E', 'A')]},
            *({'watermark_opacity': value} for value in [-0.1, 1.1, float('nan'), float('inf'), True, '0.5']),
            *({'watermark_text': value} for value in ['', '   ', 42, 'a\nb']),
        ]
        for options in bad_options:
            with self.subTest(options=options), tempfile.TemporaryDirectory() as directory:
                view = FakeView()
                exporter = FretboardExporter(view)
                failures = []
                exporter.failed.connect(failures.append)
                exporter.export_lesson('g_maj_triad', directory, **options)
                self.assertEqual(len(failures), 1)
                self.assertFalse(exporter.busy)
                self.assertFalse(view.parts)
                self.assertFalse(list(Path(directory).iterdir()))

    def test_per_part_watermarks_match_png_and_can_be_omitted_or_disabled(self):
        for text, placements in [('learnleadfast.ch', PLACEMENTS),
                                  ('learnleadfast.ch', {'GBe': ('A', 'E')}),
                                  (None, PLACEMENTS)]:
            with self.subTest(text=text, placements=placements), tempfile.TemporaryDirectory() as directory:
                exporter = FretboardExporter(FakeView())
                failures = []
                loop = QEventLoop()
                exporter.finished.connect(loop.quit)
                exporter.failed.connect(lambda error: (failures.append(error), loop.quit()))
                timeout = QTimer()
                timeout.setSingleShot(True)
                timeout.timeout.connect(loop.quit)
                timeout.start(5000)
                exporter.export_lesson('g_maj_triad', directory, watermark_text=text,
                                       watermark_between=placements)
                loop.exec()
                timeout.stop()
                self.assertFalse(failures)
                self.assertFalse(exporter.busy)
                for suffix in PLACEMENTS:
                    filename = Path(directory) / f'g_maj_triad_{suffix}.svg'
                    svg = filename.read_bytes()
                    mark = ET.fromstring(svg).find(f'{{{SVG_NS}}}path[@id="watermark"]')
                    if text is None or suffix not in placements:
                        self.assertIsNone(mark)
                    else:
                        self.assertEqual(mark.attrib['aria-label'], text)
                        self.assertEqual(mark.attrib['fill-opacity'], '0.25')
                        bounds = QSvgRenderer(QByteArray(svg)).boundsOnElement('watermark')
                        expected_y = sum(GEOMETRY['strings'][s]['y'] for s in placements[suffix]) / 2
                        self.assertAlmostEqual(bounds.center().y(), expected_y, places=3)
                        self.assertAlmostEqual(bounds.center().x(), 820, places=3)
                        image = QImage(str(filename.with_suffix('.png')))
                        # The watermark visibly changes pixels in an otherwise blank region.
                        self.assertTrue(any(image.pixelColor(x, y).name() != '#ffffff'
                                            for x in range(1500, 1780)
                                            for y in range(int(bounds.top() * 2), int(bounds.bottom() * 2))))
                    raster = Path(directory) / 'rerendered.png'
                    save_png(svg, raster)
                    self.assertEqual(QImage(str(raster)), QImage(str(filename.with_suffix('.png'))))

    def test_batch_waits_for_each_part_and_writes_both_formats(self):
        view = FakeView()
        exporter = FretboardExporter(view)
        completed, failures, progress = [], [], []
        loop = QEventLoop()
        exporter.finished.connect(lambda paths: (completed.extend(paths), loop.quit()))
        exporter.failed.connect(lambda error: (failures.append(error), loop.quit()))
        exporter.progress.connect(progress.append)
        timeout = QTimer()
        timeout.setSingleShot(True)
        timeout.timeout.connect(loop.quit)
        timeout.start(5000)
        with tempfile.TemporaryDirectory() as directory:
            exporter.export_lesson('g_maj_triad', directory)
            loop.exec()
            self.assertFalse(failures)
            self.assertFalse(exporter.busy, 'Export did not finish before the test timeout')
            self.assertEqual(len(completed), 8)
            self.assertEqual(len(view.parts), 4)
            self.assertGreaterEqual(view.polls, 8)
            for filename in completed:
                self.assertGreater(filename.stat().st_size, 0)
                self.assertIn(filename.name, progress)
            self.assertEqual([p.name for p in completed],
                             [f'g_maj_triad_{strings}.{fmt}' for strings in ('GBe', 'DGB', 'ADG', 'EAD')
                              for fmt in ('svg', 'png')])
        timeout.stop()

    def test_duplicate_names_fail_before_overwriting_files(self):
        part = load_lesson('g_maj_triad').parts[0]
        lesson = Lesson('Duplicate strings', [part, part])
        exporter = FretboardExporter(FakeView())
        failures = []
        exporter.failed.connect(failures.append)
        with tempfile.TemporaryDirectory() as directory, patch('fretboard_export.load_lesson', return_value=lesson):
            filename = Path(directory) / 'example_GBe.svg'
            filename.write_text('existing')
            exporter.export_lesson('example', directory)
            self.assertIn('collide', failures[0])
            self.assertEqual(filename.read_text(), 'existing')
            self.assertFalse(exporter.busy)

    def test_circle_triads_overrides_all_parts_without_changing_lesson(self):
        original = load_lesson('g_maj_triad')
        lesson = replace(original, parts=[replace(part, circle_sequence_elements=bool(i % 2),
                                                  fillet_corners=bool(i % 2))
                                          for i, part in enumerate(original.parts)])
        for override, expected in ((None, [False, True, False, True]),
                                   (True, [True] * 4), (False, [False] * 4)):
            with self.subTest(circle_triads=override), tempfile.TemporaryDirectory() as directory:
                view = FakeView()
                view.fret_count = 16
                exporter = FretboardExporter(view)
                failures = []
                loop = QEventLoop()
                exporter.finished.connect(loop.quit)
                exporter.failed.connect(lambda error: (failures.append(error), loop.quit()))
                timeout = QTimer()
                timeout.setSingleShot(True)
                timeout.timeout.connect(loop.quit)
                timeout.start(5000)
                with patch('fretboard_export.load_lesson', return_value=lesson):
                    options = {} if override is None else {'circle_triads': override}
                    exporter.export_lesson('g_maj_triad', directory, formats=('svg',), **options)
                    loop.exec()
                timeout.stop()
                self.assertFalse(failures)
                self.assertFalse(exporter.busy)
                self.assertEqual([args[2]['circle_sequence_elements'] for args in view.parts], expected)
                self.assertEqual([len(args[2]['play_sequence']) for args in view.parts], [4] * 4)
                self.assertIn(('G', 16), view.parts[0][0])
                self.assertEqual([part.circle_sequence_elements for part in lesson.parts],
                                 [False, True, False, True])
                self.assertEqual([part.fillet_corners for part in lesson.parts],
                                 [False, True, False, True])
                for part, (_, _, options) in zip(lesson.parts, view.parts):
                    self.assertEqual(options['wrapping_distance'], part.wrapping_distance)
                    self.assertEqual(options['fillet_corners'], True if override is True else part.fillet_corners)
                    self.assertEqual(options['fillet_radius'], part.fillet_radius)

    def test_timeout_ignores_late_browser_callbacks(self):
        class StalledView(FakeView):
            def runJavaScript(self, script, callback):
                self.callback = callback

        view = StalledView()
        exporter = FretboardExporter(view)
        failures = []
        exporter.failed.connect(failures.append)
        with tempfile.TemporaryDirectory() as directory:
            exporter.export_lesson('g_maj_triad', directory)
            exporter._timeout.timeout.emit()
            view.callback(True)
            self.assertEqual(len(failures), 1)
            self.assertFalse(view.parts)
            self.assertFalse(list(Path(directory).iterdir()))

    def test_export_highlighting_overrides_colors_without_changing_lesson(self):
        lesson = load_lesson('g_maj_triad')
        original_colors = [dict(part.highlight_classes) for part in lesson.parts]
        for active, colors in [(False, None), (True, {'G': 'highlight3', 'B': 'highlight2'}),
                               (True, {})]:
            with self.subTest(active=active, colors=colors), tempfile.TemporaryDirectory() as directory:
                view = FakeView()
                exporter = FretboardExporter(view)
                failures = []
                loop = QEventLoop()
                exporter.finished.connect(loop.quit)
                exporter.failed.connect(lambda error: (failures.append(error), loop.quit()))
                timeout = QTimer()
                timeout.setSingleShot(True)
                timeout.timeout.connect(loop.quit)
                timeout.start(5000)
                with patch('fretboard_export.load_lesson', return_value=lesson):
                    exporter.export_lesson('g_maj_triad', directory, formats=('svg',),
                                           highlight_notes=active, highlight_classes=colors)
                    loop.exec()
                timeout.stop()
                self.assertFalse(failures)
                self.assertFalse(exporter.busy)
                self.assertEqual([part[1] for part in view.parts],
                                 original_colors if colors is None else [colors] * 4)
                preparations = [script for script in view.scripts if 'fretboardExport.prepare(' in script
                                and not script.startswith('/*')]
                self.assertEqual(len(preparations), 4)
                self.assertTrue(all(f'prepare({json.dumps(active)})' in script for script in preparations))
                self.assertEqual([part.highlight_classes for part in lesson.parts], original_colors)

    @unittest.skipUnless(os.environ.get('FRETBOARD_BROWSER_TEST') == '1', 'Opt-in Qt browser integration test')
    def test_real_browser_exports_all_parts(self):
        from ui.fretboard_view import FretboardView

        with tempfile.TemporaryDirectory() as directory:
            view = FretboardView(fret_count=16)
            view.resize(1200, 400)
            exporter = FretboardExporter(view)
            completed, failures = [], []
            loop = QEventLoop()
            exporter.finished.connect(lambda files: (completed.extend(files), loop.quit()))
            exporter.failed.connect(lambda error: (failures.append(error), loop.quit()))
            view.view_loaded.connect(lambda: exporter.export_lesson(
                'g_maj_triad', directory, circle_triads=True,
                highlight_notes=True, highlight_classes={'G': 'highlight1', 'B': 'highlight2'},
                watermark_text='learnleadfast.ch', watermark_between=PLACEMENTS))
            timeout = QTimer()
            timeout.setSingleShot(True)
            timeout.timeout.connect(loop.quit)
            timeout.start(45000)
            view.show()
            loop.exec()
            timeout.stop()
            view.close()
            self.assertFalse(failures)
            self.assertEqual(len(completed), 8)
            for filename in completed:
                if filename.suffix == '.svg':
                    root = ET.parse(filename).getroot()
                    self.assertGreater(float(root.attrib['width']), 800)
                    self.assertLess(float(root.attrib['width']), 1600)
                    self.assertLess(float(root.attrib['height']), 650)
                    self.assertEqual(len(root.findall(f'.//{{{SVG_NS}}}ellipse')), 7 + 12)
                    fills = [circle.attrib['fill'] for circle in root.findall(f'.//{{{SVG_NS}}}ellipse')]
                    self.assertEqual(fills.count('rgb(231, 76, 60)'), 4)
                    self.assertEqual(fills.count('rgb(142, 68, 173)'), 4)
                    self.assertEqual(fills.count('rgb(68, 68, 68)'), 4)
                    self.assertTrue(root.findall(f'.//{{{SVG_NS}}}path[@aria-label="16"]'))
                    self.assertFalse(root.findall(f'.//{{{SVG_NS}}}path[@aria-label="17"]'))
                    self.assertEqual(len(root.findall(f'.//{{{SVG_NS}}}path[@data-sequence-group]')),
                                     4)
                    for outline in root.findall(f'.//{{{SVG_NS}}}path[@data-sequence-group]'):
                        self.assertGreater(float(outline.attrib['data-fillet-radius']), 0)
                        self.assertIn('A ', outline.attrib['d'])
                    self.assertFalse(root.findall(f'.//{{{SVG_NS}}}text'))
                    self.assertIsNotNone(root.find(f'{{{SVG_NS}}}path[@id="watermark"]'))
                else:
                    self.assertFalse(QImage(str(filename)).isNull())


if __name__ == '__main__':
    unittest.main()

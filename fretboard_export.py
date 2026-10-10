"""Asynchronous lesson export for an already loaded FretboardView.

The browser supplies the actual diagram geometry. Text is outlined with Qt,
then the same standalone SVG is used to produce the PNG.
"""

import json
import math
from dataclasses import replace
from collections.abc import Mapping
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from PySide6.QtCore import QByteArray, QObject, QPointF, QRectF, QTimer, Signal
from PySide6.QtGui import QFont, QFontDatabase, QFontInfo, QFontMetricsF, QImage, QPainter, QPainterPath, QTransform
from PySide6.QtSvg import QSvgRenderer

from models.lesson_loader import load_lesson
from mylog import get_logger

logger = get_logger(__name__)

EXPORT_DIR = Path(__file__).resolve().parent.parent / 'export'
SVG_NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG_NS)


def part_filename(lesson_name, part):
    """Use the lesson module name and all displayed strings, low to high."""
    if not re.fullmatch(r'[A-Za-z0-9_-]+', lesson_name):
        raise ValueError('Lesson name must be a filename stem without a directory')
    strings = {string for string, _ in part.get_background_positions()}
    strings.update(string for step in part.play_sequence for string, _ in step.notes)
    suffix = ''.join(string for string in ('E', 'A', 'D', 'G', 'B', 'e') if string in strings)
    return f'{lesson_name}_{suffix}'


def visible_part_content(part, last_fret, *, include_last_fret=False):
    """Omit groups outside the export range, including their exclusive notes.

    Rounded outlines (or no outlines) can include the final displayed fret.
    Sharp outlines retain the extra-fret clearance used by existing exports.
    Keep notes shared with valid groups and independent highlighted notes.
    The lesson itself is never modified.
    """
    max_fret = last_fret if include_last_fret else last_fret - 1
    sequence = []
    omitted_notes = set()
    for index, step in enumerate(part.play_sequence, start=1):
        edge_notes = [(string, fret) for string, fret in step.notes if fret > max_fret]
        if edge_notes:
            omitted_notes.update(step.notes)
            logger.warning("%s: triad %s could not be rendered: notes %s exceed "
                           "the allowed export fret (%s); omitting the entire triad",
                           part.name, index, edge_notes, max_fret)
        else:
            sequence.append(step)
    retained_notes = {note for step in sequence for note in step.notes}
    notes = [note for note in part.get_background_positions()
             if note[1] <= max_fret and (note not in omitted_notes or note in retained_notes)]
    return notes, sequence


def _path_data(path):
    """Serialize Qt's move, line and cubic elements as native SVG geometry."""
    commands = []
    index = 0
    while index < path.elementCount():
        element = path.elementAt(index)
        if element.isMoveTo():
            commands.append(f'M {element.x:.5f} {element.y:.5f}')
        elif element.isLineTo():
            commands.append(f'L {element.x:.5f} {element.y:.5f}')
        elif element.isCurveTo():
            control = path.elementAt(index + 1)
            end = path.elementAt(index + 2)
            commands.append(f'C {element.x:.5f} {element.y:.5f} '
                            f'{control.x:.5f} {control.y:.5f} {end.x:.5f} {end.y:.5f}')
            index += 2
        index += 1
    return ' '.join(commands)


def outline_svg_text(svg, description):
    """Remove font dependencies; exported labels remain vectors at any size."""
    root = ET.fromstring(svg)
    title = ET.Element(f'{{{SVG_NS}}}title')
    title.text = description
    root.insert(0, title)
    for parent in root.iter():
        for text in list(parent):
            if text.tag != f'{{{SVG_NS}}}text':
                continue
            font = QFont()
            font.setFamilies([name.strip().strip('"\'') for name in text.attrib['font-family'].split(',')])
            font.setPixelSize(round(float(text.attrib['font-size'])))
            font.setWeight(QFont.Weight.Bold if int(text.attrib['font-weight']) >= 600 else QFont.Weight.Normal)
            spacing = text.attrib.get('letter-spacing', 'normal')
            if spacing != 'normal':
                font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, float(spacing.removesuffix('px')))
            label = text.text or ''
            metrics = QFontMetricsF(font)
            x = float(text.attrib['x']) - metrics.horizontalAdvance(label) / 2
            y = float(text.attrib['y']) + (metrics.ascent() - metrics.descent()) / 2
            path = QPainterPath()
            path.addText(QPointF(x, y), font, label)
            replacement = ET.Element(f'{{{SVG_NS}}}path', {
                'd': _path_data(path), 'fill': text.attrib['fill'],
                'fill-rule': 'evenodd', 'aria-label': label,
            })
            parent.insert(list(parent).index(text), replacement)
            parent.remove(text)
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def save_png(svg, filename, scale=2):
    """Rasterize the complete SVG, independent of window size or screen DPI."""
    renderer = QSvgRenderer(QByteArray(svg))
    if not renderer.isValid():
        raise ValueError('The generated SVG is invalid')
    size = renderer.viewBoxF().size()
    image = QImage(math.ceil(size.width() * scale), math.ceil(size.height() * scale),
                   QImage.Format.Format_ARGB32_Premultiplied)
    if image.isNull():
        raise ValueError('Could not allocate the PNG image')
    image.fill('white')
    painter = QPainter(image)
    try:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        renderer.render(painter, QRectF(0, 0, image.width(), image.height()))
    finally:
        painter.end()
    if not image.save(str(filename), 'PNG'):
        raise OSError(f'Could not write {filename}')


def add_svg_watermark(svg, text, between, opacity, geometry, font_family):
    """Fit outlined text in the measured string gap, centered over the frets."""
    first, second = (geometry['strings'][name] for name in between)
    left, right = geometry['left'], geometry['right']
    values = (left, right, first['y'], second['y'], first['width'], second['width'])
    if not all(math.isfinite(value) for value in values):
        raise ValueError('Invalid watermark geometry')
    gap = abs(first['y'] - second['y'])
    # Stay clear of string strokes, leaving at least 4px on either side.
    available_height = min(gap * 0.5, gap - max(first['width'], second['width']) - 8)
    available_width = right - left - 16
    if available_height <= 0 or available_width <= 0:
        raise ValueError('Not enough space between the selected strings for the watermark')
    font = QFont(font_family)
    font.setPixelSize(24)
    path = QPainterPath()
    path.addText(QPointF(0, 0), font, text)
    bounds = path.boundingRect()
    if bounds.isEmpty():
        raise ValueError('watermark_text must contain visible characters')
    scale = min(1, available_width / bounds.width(), available_height / bounds.height())
    center_x, center_y = (left + right) / 2, (first['y'] + second['y']) / 2
    transform = QTransform()
    transform.translate(center_x, center_y)
    transform.scale(scale, scale)
    transform.translate(-bounds.center().x(), -bounds.center().y())
    root = ET.fromstring(svg)
    ET.SubElement(root, f'{{{SVG_NS}}}path', {
        'id': 'watermark', 'd': _path_data(transform.map(path)),
        'fill': '#333333', 'fill-opacity': str(opacity), 'fill-rule': 'evenodd',
        'aria-label': text,
    })
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


class FretboardExporter(QObject):
    """Export one batch at a time; call export_lesson after view_loaded.

    Existing matching files are replaced. Progress emits the filename just
    before writing; finished emits all saved Paths, failed emits an error.
    """

    progress = Signal(str)
    diagram_size = Signal(int, int)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, view, parent=None):
        super().__init__(parent)
        self.view = view
        self.busy = False
        self._generation = 0
        self._timeout = QTimer(self)
        self._timeout.setSingleShot(True)
        self._timeout.timeout.connect(lambda: self._fail('Timed out waiting for the fretboard to render'))

    def export_lesson(self, lesson_name, output_dir=EXPORT_DIR, formats=('svg', 'png'),
                      png_scale=2, *, circle_triads=None, watermark_text=None,
                      watermark_between=None, watermark_opacity=0.25,
                      highlight_notes=False, highlight_classes=None):
        """Export all parts, optionally overriding their boundary setting.

        circle_triads=True enables rounded boundaries for every part; False disables
        them. None (the default) preserves each part's circle_sequence_elements.
        None also preserves its corner style. Spacing and corner radius always
        come from the part (defaults: 8px clearance and a 24px radius).

        highlight_notes=True uses active playback colors for every displayed
        note, including open strings. False keeps the faded appearance.
        highlight_classes overrides every part's note-name-to-CSS-class mapping
        (e.g. {'G': 'highlight1'}). None preserves each part's mapping; {} removes
        all fixed colors. Use highlight1 (red), highlight2 (purple), highlight3
        (blue); unmapped notes use dark grey when active. Note names follow the
        lesson's sharp/flat spelling (e.g. 'F#' or 'Bb').

        watermark_between maps filename suffixes (e.g. 'GBe') to adjacent string
        pairs (e.g. ('E', 'A')). Pair order does not matter; E is low, e is high.
        Unmapped parts are not watermarked. watermark_text=None disables all
        watermarks. Opacity ranges from 0 (invisible) to 1 (opaque).
        """
        if self.busy:
            raise RuntimeError('An export is already running')
        self.busy = True
        self._generation += 1
        try:
            if circle_triads is not None and not isinstance(circle_triads, bool):
                raise ValueError('circle_triads must be True, False, or None')
            self.circle_triads = circle_triads
            if not isinstance(highlight_notes, bool):
                raise ValueError('highlight_notes must be True or False')
            if highlight_classes is not None and (
                    not isinstance(highlight_classes, Mapping)
                    or any(not isinstance(note, str) or not isinstance(css, str)
                           or not css or any(char.isspace() for char in css)
                           for note, css in highlight_classes.items())):
                raise ValueError('highlight_classes must map note names to single CSS classes, or be None')
            self.highlight_notes = highlight_notes
            self.highlight_classes = None if highlight_classes is None else dict(highlight_classes)
            self.formats = tuple(formats)
            if not self.formats or len(set(self.formats)) != len(self.formats) or any(
                    fmt not in ('svg', 'png') for fmt in self.formats):
                raise ValueError('formats must contain svg and/or png without duplicates')
            if isinstance(png_scale, bool) or not math.isfinite(png_scale) or png_scale <= 0:
                raise ValueError('png_scale must be a positive finite number')
            if not re.fullmatch(r'[A-Za-z0-9_-]+', lesson_name):
                raise ValueError('Use a lesson module name without a path or .py extension')
            self.lesson = load_lesson(lesson_name)
            if self.lesson is None:
                raise ValueError(f'Could not load lesson {lesson_name}')
            self.names = [part_filename(lesson_name, part) for part in self.lesson.parts]
            if len(set(self.names)) != len(self.names):
                raise ValueError('Multiple parts use the same strings; their export filenames would collide')
            if watermark_text is not None and (not isinstance(watermark_text, str)
                                               or not watermark_text.strip()
                                               or any(c in watermark_text for c in '\r\n\t')):
                raise ValueError('watermark_text must be nonempty single-line text or None')
            if (isinstance(watermark_opacity, bool) or not isinstance(watermark_opacity, (int, float))
                    or not math.isfinite(watermark_opacity) or not 0 <= watermark_opacity <= 1):
                raise ValueError('watermark_opacity must be a finite number between 0 and 1')
            if watermark_between is not None and not isinstance(watermark_between, Mapping):
                raise ValueError('watermark_between must map part suffixes to adjacent string pairs')
            placements = dict(watermark_between or {})
            suffixes = [name.removeprefix(f'{lesson_name}_') for name in self.names]
            tuning = ('E', 'A', 'D', 'G', 'B', 'e')
            for suffix, pair in placements.items():
                if suffix not in suffixes:
                    raise ValueError(f'Unknown watermark part {suffix!r}; expected one of {suffixes}')
                if (not isinstance(pair, (tuple, list)) or len(pair) != 2
                        or any(string not in tuning for string in pair)
                        or abs(tuning.index(pair[0]) - tuning.index(pair[1])) != 1):
                    raise ValueError(f'Watermark for {suffix} must specify two adjacent strings (E A D G B e)')
                placements[suffix] = tuple(pair)
            self.watermark_text = watermark_text
            self.watermark_pairs = [placements.get(suffix) for suffix in suffixes]
            self.watermark_opacity = watermark_opacity
            self.output_dir = Path(output_dir).resolve()
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.png_scale = png_scale
            self.index = 0
            self.saved = []
            script = Path(__file__).with_suffix('.js').read_text(encoding='utf-8')
            installed = set(QFontDatabase.families())
            family = next((name for name in ('Montserrat', 'Arial', 'DejaVu Sans', 'Liberation Sans')
                           if name in installed), QFontInfo(QFont()).family())
            self._font_family = family
            script += f'\nwindow.initializeFretboardExport({json.dumps(family)});'
            self._timeout.start(30000)
            self._javascript(script, self._initialized)
        except Exception as error:
            self._fail(str(error))

    def _javascript(self, script, callback):
        generation = self._generation

        def receive(value):
            if not self.busy or generation != self._generation:
                return
            try:
                callback(value)
            except Exception as error:
                self._fail(str(error))

        self.view.page().runJavaScript(script, receive)

    def _initialized(self, success):
        if success is not True:
            raise RuntimeError('Could not initialize the fretboard exporter')
        self._next_part()

    def _next_part(self):
        if self.index == len(self.lesson.parts):
            self._timeout.stop()
            self.busy = False
            self.finished.emit(list(self.saved))
            return
        part = self.lesson.parts[self.index]
        circle = part.circle_sequence_elements if self.circle_triads is None else self.circle_triads
        rounded = True if self.circle_triads is True else part.fillet_corners
        notes, sequence = visible_part_content(
            part, self.view.fret_count, include_last_fret=not circle or rounded)
        visible_positions = set(notes)
        layers = [replace(layer, notes=tuple(note for note in layer.notes
                                            if note in visible_positions))
                  for layer in part.background_layers]
        self.progress.emit(f'{self.names[self.index]}.{self.formats[0]}')
        self.view.display_notes(
            notes, part.highlight_classes if self.highlight_classes is None else self.highlight_classes,
            use_sharp=self.lesson.use_sharp, play_sequence=sequence,
            background_layers=layers,
            circle_sequence_elements=circle,
            wrapping_distance=part.wrapping_distance,
            fillet_corners=rounded,
            fillet_radius=part.fillet_radius,
            highlight_chord_root=part.highlight_chord_root,
            chord_label_title=self.lesson.chord_label_title,
        )
        self._timeout.start(30000)
        # Browser commands execute in order; prepare follows the display update.
        self._javascript("window.renderChordSequence([], ''); window.clearNoteHighlights(); "
                         f'window.fretboardExport.prepare({json.dumps(self.highlight_notes)}); true;',
                         lambda _: self._poll())

    def _poll(self):
        self._javascript('JSON.stringify(window.fretboardExport.result)', self._receive_snapshot)

    def _receive_snapshot(self, result):
        snapshot = json.loads(result) if result else None
        if snapshot is None:
            generation = self._generation
            QTimer.singleShot(40, lambda: self._poll() if self.busy and generation == self._generation else None)
            return
        if 'error' in snapshot:
            raise RuntimeError(snapshot['error'])
        self._timeout.stop()
        bounds = ET.fromstring(snapshot['svg'])
        self.diagram_size.emit(math.ceil(float(bounds.attrib['width'])), math.ceil(float(bounds.attrib['height'])))
        svg = outline_svg_text(snapshot['svg'], f'{self.lesson.name}: {self.lesson.parts[self.index].name}')
        pair = self.watermark_pairs[self.index]
        if self.watermark_text is not None and pair is not None:
            svg = add_svg_watermark(svg, self.watermark_text, pair, self.watermark_opacity,
                                    snapshot['geometry'], self._font_family)
        self._pending_svg = svg
        self._format_index = 0
        self._save_next_format()

    def _save_next_format(self):
        if not self.busy:
            return
        try:
            if self._format_index == len(self.formats):
                self.index += 1
                self._next_part()
                return
            fmt = self.formats[self._format_index]
            filename = self.output_dir / f'{self.names[self.index]}.{fmt}'
            self.progress.emit(filename.name)
            # Give Qt an event-loop turn to paint the status before doing I/O.
            generation = self._generation

            def write():
                if not self.busy or generation != self._generation:
                    return
                try:
                    if fmt == 'svg':
                        filename.write_bytes(self._pending_svg)
                    else:
                        save_png(self._pending_svg, filename, self.png_scale)
                    self.saved.append(filename)
                    self._format_index += 1
                    self._save_next_format()
                except Exception as error:
                    self._fail(str(error))

            QTimer.singleShot(0, write)
        except Exception as error:
            self._fail(str(error))

    def _fail(self, message):
        self._timeout.stop()
        self.busy = False
        self._generation += 1
        self.failed.emit(message)

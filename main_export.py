"""Run with python Modular/main_export.py to export the G major triad lesson."""

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar

from fretboard_export import EXPORT_DIR, FretboardExporter
from ui.fretboard_view import FretboardView


def export_G_triads(exporter):
    """The export recipe: change the lesson or options here for other batches."""
    exporter.export_lesson(
        'g_maj_triad',
        output_dir=EXPORT_DIR,
        formats=('svg', 'png'),
        png_scale=2,
        circle_triads=True,
        watermark_text='   learnleadfast.com',
        # Filename suffix -> gap between two adjacent strings (E = low, e = high).
        watermark_between={
            'GBe': ('E', 'A'),
            'DGB': ('E', 'A'),
            'ADG': ('B', 'e'),
            'EAD': ('B', 'e'),
        },
        watermark_opacity=0.15,
    )


class ExportWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Fretboard Export')
        self.resize(1200, 380)
        self.view = FretboardView(self, fret_count=16)
        self.view.setZoomFactor(1.0)
        self.setCentralWidget(self.view)
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage('Loading fretboard…')
        self.exporter = FretboardExporter(self.view, self)
        self.exporter.progress.connect(lambda name: self.statusBar().showMessage(f'Exporting {name}'))
        self.exporter.finished.connect(self._finished)
        self.exporter.failed.connect(self._failed)
        self.exporter.diagram_size.connect(self._fit_diagram)
        self.view.loadFinished.connect(self._loaded)
        self._load_timeout = QTimer(self)
        self._load_timeout.setSingleShot(True)
        self._load_timeout.timeout.connect(self._load_failed)
        self._load_timeout.start(30000)
        self._started = False

    def _loaded(self, success):
        self._load_timeout.stop()
        if self._started:
            return
        self._started = True
        if success:
            export_G_triads(self.exporter)
        else:
            self._failed('Could not load the fretboard')

    def _load_failed(self):
        self._started = True
        self._failed('Timed out loading the fretboard')

    def _finished(self, files):
        self.statusBar().showMessage(f'Exported {len(files)} files to {EXPORT_DIR}')

    def _fit_diagram(self, width, height):
        # Geometry is in CSS pixels and this view uses 100% zoom. Include the
        # page margins and status bar, and prevent resizing below the diagram.
        width += 56
        height += 56 + self.statusBar().sizeHint().height()
        # A bad geometry result must never request a giant GPU-backed window.
        available = self.screen().availableGeometry()
        frame = self.frameGeometry().size() - self.size()
        width = min(width, max(1, available.width() - frame.width()))
        height = min(height, max(1, available.height() - frame.height()))
        self.setMinimumSize(width, height)
        self.resize(width, height)

    def _failed(self, message):
        self.statusBar().showMessage(f'Export failed: {message}')
        print(f'Export failed: {message}', file=sys.stderr)


def main():
    app = QApplication(sys.argv)
    window = ExportWindow()
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())

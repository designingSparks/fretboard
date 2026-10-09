# Exporting fretboards

Run `python Modular/main_export.py` from the repository root (or run
`main_export.py` from your editor). The window shows only the fretboard and an
export status bar. It automatically exports all four parts of `g_maj_triad` to
the repository's `export/` directory, then remains open on the final part.

Files are named `g_maj_triad_GBe.svg`, `g_maj_triad_GBe.png`, and likewise for
`DGB`, `ADG`, and `EAD`. Existing matching files are replaced. Exports contain
the board through fret 16 with a white background and the resting note colors;
the title, subtitle, chord buttons, and status bar are omitted.
The window fits the diagram within the available screen. Rounded outlines (or
disabled outlines) allow notes on the final displayed fret. The diagram adds
padding when an outline extends beyond the board. The export includes all four
GBe triads, including the last one on frets 15 and 16. Sharp outlines retain an
extra fret of clearance. Any triad exceeding the allowed range is omitted
entirely and logged once. Shared notes remain if another visible triad needs
them. The regular player continues to show 24 frets.

Edit `export_G_triads(exporter)` in `main_export.py` to select a different
lesson, output directory, formats, or PNG scale. PNG defaults to 2× resolution.
Pass `circle_triads=True` to enable rounded triad boundaries for every part, or `False`
to disable them. Omitting it (or using `None`) preserves the lesson's settings.
The G triad export recipe enables this option, using the same rounded outline
geometry as the C major lesson. Spacing and corner radius still come from each
part (defaults: 8px clearance and 24px radius). When preserving a lesson's sharp
corner style, very sharp corners are clipped to keep the outline compact while
preserving clearance around the notes.
The reusable `FretboardExporter.export_lesson()` method must be called after
the view loads and emits `progress(filename)`, `finished(paths)`, and
`failed(message)` signals. Parts with the same string suffix are rejected to
prevent filename collisions within a batch.

SVGs contain native vector geometry and outlined labels, so no fonts, scripts,
or stylesheets are needed on your website. Export mode uses an installed
Montserrat font when available, otherwise Arial or another installed sans-serif
font, shared by the preview and export renderer.

The G triad recipe also adds `learnleadfast.ch` to each exported SVG and PNG.
Choose the gap separately for each part in `main_export.py`:

```python
watermark_text='learnleadfast.ch',
watermark_between={
    'GBe': ('E', 'A'),
    'DGB': ('E', 'A'),
    'ADG': ('B', 'e'),
    'EAD': ('B', 'e'),
},
watermark_opacity=0.25,
```

Keys are the string suffixes in the exported filenames. Each pair must contain
adjacent strings; either order works. `E` is low E and `e` is high E. Choose a
gap away from that part's triads; placement is explicit, with no automatic
collision detection. Unknown suffixes and invalid pairs are rejected before
writing any files. Omit a part from the mapping to leave it unwatermarked, or
set `watermark_text=None` to disable all watermarks. The reusable exporter has
watermarking disabled by default.

The watermark is centered over the fretted area and halfway between the
selected strings. Its 18px font shrinks when necessary to fit with clearance.
Opacity ranges from 0 (invisible) to 1 (opaque). Text is converted to vector
paths before producing both formats, so no website fonts are needed. The
watermark appears in the saved files, not in the live fretboard window.

Tests (from the repository root):

```sh
QT_QPA_PLATFORM=offscreen python -m unittest discover -s Modular -p test_fretboard_export.py
node --test Modular/test_fretboard_export.cjs
```

Add `FRETBOARD_BROWSER_TEST=1` to the Python command to include the real Qt
browser integration test where Chromium can run.

# Notes on VS Code

When running or debugging a file using the Run > Start debugging, the root directory is always the project directory, even if the python file is in a subdirectory. Thus you should only use relative paths if they are relative to the project directory.


# Build command

Newest command:

Note: --include-data-dir causes the clean dir to be copied into the MacOS dir in the application package on Mac.

python3 -m nuitka --mode=app \
    --enable-plugin=pyside6 \
    --macos-app-icon=./icon/icon.icns \
    --output-dir=build \
    --include-data-dir=./clean=clean \
    ./qaudio.py

# Creating and building icons

Use the script in make_icon.sh


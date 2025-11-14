# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## General Notes
For loading .wav files, use the wavefile.py file directly rather than scipy.io.wavfile.read.
The avoids having to package scipy with the final distribution.

## Project Overview

This is a PySide6-based guitar learning application that visualizes scales and chords on an interactive fretboard. The app plays audio sequences synchronized with visual highlights on the fretboard display, helping users learn guitar patterns and positions.

## Build Commands

### Development
Run the main application:
```bash
python main.py
```

Note: VS Code debugging always uses the project directory as root, so all relative paths must be relative to the project directory.

### Production Build
Build a standalone macOS application using Nuitka:
```bash
python3 -m nuitka --mode=app \
    --enable-plugin=pyside6 \
    --macos-app-icon=./icon/icon.icns \
    --output-dir=build \
    --include-data-dir=./clean=clean \
    ./main.py
```

The `--include-data-dir` flag copies the `clean` directory (containing audio files) into the macOS application package.

### Creating Icons
Use the `make_icon.sh` script in the `icon` directory to create application icons.

## Architecture

### Core Components

**Main Application (`main.py`)**
- Entry point for the application
- Instantiates `FretboardPlayer` (audio engine), `MainWindow` (UI), and `FretboardView` (visualization)
- Connects UI signals to audio playback methods
- Uses Qt's signal/slot mechanism for communication between components

**Audio Engine (`FretboardPlayer` class in `main.py`)**
- Handles all audio processing, loading, mixing, and playback timing
- Uses `QAudioSink` for low-level audio streaming
- Implements precise timing with latency compensation for synchronized UI updates
- Loads guitar note samples from WAV files in the `clean` folder
- Mixes multiple notes with strum delay simulation
- Audio streaming architecture:
  - Timer-based push model (`push_audio_data` called every 50ms)
  - Dynamic latency compensation based on buffer fullness
  - UI updates scheduled with `QTimer.singleShot` to sync with actual audio output

**UI Components (`ui/` directory)**
- `main_window.py`: Main window with toolbar (play/pause/stop controls, speed control, navigation)
- `fretboard_view.py`: Web-based fretboard visualization using `QWebEngineView`
  - Loads `fretboard.html` and communicates via JavaScript
  - Provides methods to highlight notes and display scales
  - Emits `view_loaded` signal when ready

### Data Structures

**Scale/Chord Definitions (`scales.py`, `triads.py`)**
- Define note positions as tuples of `(string_name, fret_number)`
- Two arrays per pattern:
  - `*_HIGHLIGHT`: All notes in the pattern (displayed dimmed)
  - `*_PLAY`: Sequence to play with note durations in milliseconds
- Example: `[('A', 3), TON]` means play A string, 3rd fret, for TON milliseconds

**Constants (`constants.py`)**
- `STRING_ID`: String names from high e to low E: `['e', 'B', 'G', 'D', 'A', 'E']`
- `FRETBOARD_NOTES_NAME`: 2D array mapping string index and fret to note names
- `FRETBOARD_NOTES_MIDI`: 2D array mapping string index and fret to MIDI note numbers
- Helper functions: `create_tuple()` to generate note lists, `print_tuple()` for formatting

### Audio System

**MIDI to Audio Mapping**
- Guitar samples stored in `clean/` folder as `clean_XX.wav` (XX = MIDI note number)
- Open string MIDI values: E=40, A=45, D=50, G=55, B=59, e=64
- Standard tuning with frets added to open string MIDI value

**Audio Processing Pipeline**
1. `init_midi()`: Converts play sequence to MIDI note numbers
2. `create_sound_list()`: Loads WAV files, mixes with strum delay, truncates to duration
3. `_mix_notes()`: Adds progressive delay between strings (strum effect), normalizes amplitude
4. Playback: Streams pre-processed byte buffers to `QAudioSink`

### Configuration

**Settings System (`settings.py`)**
- TOML-based configuration stored in `~/.learnleadfast/settings.toml`
- `ConfigManager` class handles reading/writing settings
- Auto-creates config directory and file if missing
- Access settings via `config.settings` dictionary

**Logging (`mylog.py`)**
- Custom logging configuration
- Import with: `from mylog import get_logger; logger = get_logger(__name__)`

### Resource Loading

**Path Resolution (`utilities.py`)**
- `get_resource_path(relative_path)`: Returns correct paths for both development and compiled executables
- Handles differences between:
  - Development: Paths relative to script location
  - macOS app bundle: Resources in `.app/Contents/Resources/`
  - Other platforms: Resources alongside executable

### Alternative Implementations

**Development Files (`dev/` directory)**
- Contains experimental and alternative implementations
- Not part of main application

**Standalone Audio Player (`qaudio.py`)**
- Alternative entry point with simpler UI
- Used as build target for Nuitka compilation
- Demonstrates low-level `QAudioSink` usage

### Utility Scripts (`utils/` directory)

Audio processing utilities (not part of main app):
- `create_riff.py`: Generate musical riffs
- `disortion.py`: Apply distortion effects
- `generate_scale.py`: Generate scale patterns
- `pitch_shift.py`: Transpose audio
- `play_multiple_note.py`: Multi-note playback test
- `record.py`: Audio recording
- `truncate_notes.py`: Trim audio files
- `view_wav.py`: Visualize waveforms

## Key Technical Details

### PySide6 Signal/Slot Pattern
The app uses Qt's signal/slot mechanism for loose coupling:
- `MainWindow` emits signals when toolbar buttons are clicked
- `FretboardPlayer` connects to these signals to control playback
- `FretboardView` emits `view_loaded` signal when ready

### JavaScript Bridge
Communication between Python and the web-based fretboard:
- Python → JavaScript: `page().runJavaScript()` calls functions in `fretboard.html`
- Key JS functions: `displayNotes()`, `highlightNotes()`, `clearNoteHighlights()`
- Data passed as JSON strings

### Timing Precision
Critical for music applications:
- Uses `Qt.TimerType.PreciseTimer` for accurate timing
- Dynamic latency compensation calculates buffer fullness
- UI updates delayed by calculated latency to sync with audio

### Audio Format
- Sample rate: 44100 Hz
- Channels: Mono (1 channel)
- Sample format: 16-bit signed integer (Int16)
- Strum delay: 10ms between strings (`STRUM_DELAY_MS`)

## File Organization

```
/
├── main.py              # Main application entry point
├── qaudio.py            # Alternative entry point (used for builds)
├── ui/                  # UI components
│   ├── main_window.py   # Main window with toolbar
│   └── fretboard_view.py # Fretboard visualization
├── scales.py            # Scale definitions
├── triads.py            # Chord/triad definitions
├── constants.py         # Fretboard note mappings
├── settings.py          # Configuration management
├── mylog.py             # Logging setup
├── utilities.py         # Resource path helpers
├── wavfile.py           # WAV file I/O
├── fretboard.html       # Web-based fretboard display
├── main.js              # JavaScript for fretboard interaction
├── clean/               # Guitar note audio samples
├── icons/               # UI icons (SVG)
├── icon/                # Application icon resources
├── utils/               # Audio processing utilities
└── dev/                 # Experimental implementations
```

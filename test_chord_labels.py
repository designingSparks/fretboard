"""Tests for labelled rows, audio conversion, and Python/browser coordination."""

import json
import unittest
from types import SimpleNamespace
from PySide6.QtCore import QObject, Signal

from audio_engine import AudioEngine
from main import FretboardPlayer
from models.lesson_model import Part, Lesson
from models.sequence_step import parse_sequence_row
from ui.fretboard_view import FretboardView


class FakeView(QObject):
    view_loaded = Signal()

    def __init__(self):
        super().__init__()
        self.calls = []

    def isVisible(self):
        return True

    def display_notes(self, *args, **kwargs):
        self.calls.append(('display', kwargs['play_sequence']))
        self.caption = kwargs['chord_label_title']

    def set_playback_state(self, state):
        self.calls.append(('state', state))

    def highlight_sequence_step(self, index):
        self.calls.append(('step', index))


class FakeAudio(QObject):
    playback_started = Signal()
    playback_stopped = Signal()
    highlight_note_index = Signal(int)

    def __init__(self):
        super().__init__()
        self.is_playing = False

    def load_part(self, part):
        self.part = part

    def stop_playback(self):
        self.is_playing = False
        self.playback_stopped.emit()


class ChordLabelTests(unittest.TestCase):
    def test_g_c_d_bridge_marks_only_the_current_root_in_all_positions(self):
        from constants import FRETBOARD_NOTES_SHARP, STRING_ID
        from lessons.g_c_d_major_triads import lesson

        for part in lesson.parts:
            scripts = []
            view = SimpleNamespace(page=lambda: SimpleNamespace(runJavaScript=scripts.append))
            FretboardView.display_notes(
                view, part.notes_to_highlight, play_sequence=part.play_sequence,
                highlight_chord_root=part.highlight_chord_root,
            )
            args = json.loads('[' + scripts[0][len('displayNotes('):-2] + ']')
            for step in args[5]:
                with self.subTest(part=part.name, step=step):
                    roots = [note for note in step['notes'] if note.get('isRoot')]
                    self.assertEqual(len(roots), 1)
                    root = roots[0]
                    self.assertEqual(
                        FRETBOARD_NOTES_SHARP[STRING_ID.index(root['stringName'])][root['fret']],
                        step['chordName'][0],  # G/C/D root, independent of label subtext
                    )

    def test_legacy_and_labelled_rows_keep_notes_and_duration(self):
        notes = [('e', 3), ('B', 3), ('G', 4)]
        legacy = parse_sequence_row([*notes, 1000])
        labelled = parse_sequence_row([*notes, 'G', 1000])
        self.assertEqual(legacy.notes, labelled.notes)
        self.assertEqual(labelled.notes, tuple(notes))
        self.assertEqual(legacy.duration_ms, labelled.duration_ms)
        self.assertIsNone(legacy.chord_name)
        self.assertEqual(labelled.chord_name, 'G')
        self.assertEqual(parse_sequence_row([('B', 4), 'Ebmaj7', 500]).chord_name, 'Ebmaj7')
        part = Part('Chords', notes, [[*notes, 'G', 1000], [('e', 0), 500]])
        self.assertEqual(part.get_duration_ms(), 1500)

    def test_invalid_rows_fail_with_a_clear_validation_error(self):
        for row in ([], [('e', 3), 1000, 'G'], [('e', 3), '', 1000],
                    [('e', 3), 'G', 'C', 1000], [('x', 3), 1000],
                    [('e', 25), 1000], [('e', 3), True], [('e', 3), -1]):
            with self.subTest(row=row), self.assertRaises(ValueError):
                parse_sequence_row(row)

    def test_audio_labels_do_not_change_midi_or_timing(self):
        engine = SimpleNamespace()
        AudioEngine.init_midi(engine, [
            [('e', 3), ('B', 3), ('G', 4), 'G', 1000],
            [('e', 3), ('B', 5), ('G', 5), 'C', 1000],
            [('e', 5), ('B', 7), ('G', 7), 'D', 1000],
        ])
        self.assertEqual(engine.midi, [[67, 62, 59], [67, 64, 60], [69, 66, 62]])
        self.assertEqual(engine.note_duration, [1000, 1000, 1000])

    def test_rest_rows_keep_duration_and_index(self):
        engine = SimpleNamespace(samplerate=44100)
        AudioEngine.init_midi(engine, [[500]])
        AudioEngine.create_sound_list(engine)
        self.assertEqual(engine.midi, [[]])
        self.assertEqual(len(engine.sound_list[0]), 44100)
        self.assertFalse(any(engine.sound_list[0]))

    def test_stale_audio_callbacks_cannot_select_new_sequence(self):
        highlighted = []
        engine = SimpleNamespace(is_playing=True, _playback_generation=3,
                                 highlight_note_index=SimpleNamespace(emit=highlighted.append))
        AudioEngine._emit_highlight_signal(engine, 2, 1)
        self.assertEqual(highlighted, [])
        AudioEngine._emit_highlight_signal(engine, 0, 3)
        self.assertEqual(highlighted, [0])
        engine.is_playing = False
        AudioEngine._emit_highlight_signal(engine, 1, 3)
        self.assertEqual(highlighted, [0])

    def test_bridge_sends_labels_without_circles_and_renders_missing_notes(self):
        scripts = []
        view = SimpleNamespace(page=lambda: SimpleNamespace(runJavaScript=scripts.append))
        FretboardView.display_notes(view, [('e', 3)], chord_label_title='Chord selected', play_sequence=[
            [('e', 3), ('B', 3), ('G', 4), 'G', 1000],
            [('e', 3), ('B', 5), ('G', 5), 'C', 1000],
        ])
        args = json.loads('[' + scripts[0][len('displayNotes('):-2] + ']')
        self.assertEqual(args[1], [])
        self.assertEqual(len(json.loads(args[0])), 5)
        self.assertEqual([s['chordName'] for s in args[5]], ['G', 'C'])
        self.assertEqual(len(args[5][1]['notes']), 3)
        self.assertEqual(args[6], 'Chord selected')
        FretboardView.highlight_sequence_step(view, 1)
        FretboardView.set_playback_state(view, 'playing')
        self.assertEqual(scripts[-2:], ['highlightSequenceStep(1);', 'setChordPlaybackState("playing");'])

    def test_coordinator_start_step_stop_and_part_switch(self):
        view, audio = FakeView(), FakeAudio()
        player = FretboardPlayer(view, audio)
        first = Part('First', [('e', 3)], [[('e', 3), 'G', 1000]])
        second = Part('Second', [('e', 5)], [[('e', 5), 'D', 1000]])
        player.load_lesson(Lesson('Test', [first, second], chord_label_title='Chord selected'))
        self.assertEqual(view.caption, 'Chord selected')
        view.view_loaded.emit()
        self.assertEqual(view.caption, 'Chord selected')
        audio.is_playing = True
        audio.playback_started.emit()
        audio.highlight_note_index.emit(0)
        self.assertEqual(view.calls[-2:], [('state', 'playing'), ('step', 0)])
        audio.highlight_note_index.emit(-1)
        audio.highlight_note_index.emit(5)
        self.assertEqual(view.calls[-1], ('step', 0))
        player.next_part()
        self.assertFalse(audio.is_playing)
        self.assertEqual(view.calls[-2:], [('state', 'stopped'), ('display', second.play_sequence)])
        self.assertEqual(view.caption, 'Chord selected')


if __name__ == '__main__':
    unittest.main()

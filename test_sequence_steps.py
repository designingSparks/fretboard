"""Named-step authoring, validation, legacy compatibility, and generator tests."""

import importlib
import io
import unittest
from contextlib import redirect_stdout
from dataclasses import FrozenInstanceError
from unittest.mock import patch

import numpy as np

from audio_rendering import render_sequence
from lesson_utils.utils import (
    create_play_sequence, create_ascending_descending_sequence, repeat_sequence,
)
from models.lesson_model import Part
from models.lesson_loader import LessonLoader
from models.sequence_step import SequenceStep, parse_sequence_row
from tablature.tablature_parser import create_play_sequence_from_bars, print_lesson_code


class SequenceStepTests(unittest.TestCase):
    def test_named_fields_validate_and_freeze_note_positions(self):
        notes = [['e', 3], ['B', 3], ['G', 4]]
        step = SequenceStep(notes=notes, duration_ms=1000, chord_name=' G ',
                            shape='E', position_group=1)
        notes[0][1] = 8
        self.assertEqual(step.notes, (('e', 3), ('B', 3), ('G', 4)))
        self.assertEqual(step.chord_name, 'G')
        self.assertIs(parse_sequence_row(step), step)
        with self.assertRaises(FrozenInstanceError):
            step.duration_ms = 200
        for values in (
            {'duration_ms': -1}, {'duration_ms': True}, {'duration_ms': '500'},
            {'notes': [('e', 25)]}, {'notes': [('x', 0)]}, {'notes': 'e3'},
            {'notes': [('e', True)]}, {'chord_name': ''}, {'chord_name': 3},
            {'shape': ''}, {'shape': 2}, {'position_group': 0},
            {'position_group': True}, {'position_group': '1'},
        ):
            with self.subTest(values=values), self.assertRaises(ValueError):
                SequenceStep(**({'notes': (('e', 3),), 'duration_ms': 500} | values))

    def test_legacy_and_named_steps_can_share_a_part(self):
        step = SequenceStep(notes=(('e', 3), ('B', 3), ('G', 4)), duration_ms=1000,
                            chord_name='G', shape='E', position_group=1)
        part = Part(name='Mixed', background_notes=[('e', 3)],
                    play_sequence=[step, [('e', 0), 500], [250]])
        self.assertTrue(all(isinstance(row, SequenceStep) for row in part.play_sequence))
        self.assertIs(part.play_sequence[0], step)
        self.assertEqual(part.play_sequence[-1].notes, ())
        self.assertEqual(part.get_duration_ms(), 1750)
        with patch('audio_rendering.wavfile.read',
                   return_value=(1000, np.arange(1200, dtype=np.int16))):
            named_buffers = render_sequence(part.play_sequence, 'clean', 1000, 10)
            legacy_buffers = render_sequence([
                [('e', 3), ('B', 3), ('G', 4), 'G', 1000], [('e', 0), 500], [250],
            ], 'clean', 1000, 10)
        self.assertEqual(named_buffers, legacy_buffers)

    def test_all_lesson_constants_and_parts_use_named_steps(self):
        loader = LessonLoader()
        for filename in [*loader.get_available_lesson_files(), '_template']:
            with self.subTest(lesson=filename):
                module = importlib.import_module(f'lessons.{filename}')
                for name, value in vars(module).items():
                    if name.endswith(('_SEQUENCE', '_PLAY')):
                        self.assertTrue(all(isinstance(step, SequenceStep) for step in value), name)
                for part in module.lesson.parts:
                    self.assertTrue(all(isinstance(step, SequenceStep) for step in part.play_sequence))
        from lessons.g_c_d_major_triads import lesson
        for part in lesson.parts:
            self.assertEqual([step.position_group for step in part.play_sequence], [1]*3 + [2]*3 + [3]*3)
        self.assertEqual([step.shape for step in lesson.parts[0].play_sequence],
                         ['E', 'A', 'A', 'C/D', 'E', 'E', 'A', 'C/D', 'C/D'])

    def test_pattern_helpers_preserve_order_duration_and_repetitions(self):
        notes = [('E', 0), ('A', 2), ('D', 2)]
        ascending = create_play_sequence(notes, duration=300)
        self.assertEqual([step.notes for step in ascending], [(note,) for note in notes])
        self.assertEqual(create_play_sequence(notes, duration=300, ascending=False), ascending[::-1])
        self.assertEqual(create_ascending_descending_sequence(notes, duration=300), ascending + ascending[::-1])
        self.assertEqual(repeat_sequence(notes, duration=300, repetitions=3), ascending * 3)
        self.assertTrue(all(step.duration_ms == 300 for step in ascending))

    def test_tablature_generator_outputs_named_steps(self):
        bars = [['e|--3--5--|', 'B|--3-----|', 'G|--4-----|',
                 'D|--------|', 'A|--------|', 'E|--------|']]
        steps = create_play_sequence_from_bars(bars, [1], [1000, 500])
        self.assertEqual(steps, [
            SequenceStep(notes=(('e', 3), ('B', 3), ('G', 4)), duration_ms=1000),
            SequenceStep(notes=(('e', 5),), duration_ms=500),
        ])

    def test_generated_lesson_code_preserves_named_metadata(self):
        step = SequenceStep(notes=(('e', 3), ('B', 3), ('G', 4)), duration_ms=1000,
                            chord_name='G', shape='E', position_group=1)
        part = Part(name='Generated', background_notes=list(step.notes), play_sequence=[step])
        output = io.StringIO()
        with redirect_stdout(output):
            print_lesson_code([part], lesson_name='Generated lesson')
        namespace = {}
        exec(compile(output.getvalue(), '<generated lesson>', 'exec'), namespace)
        self.assertEqual(namespace['PART1_SEQUENCE'], [step])
        self.assertEqual(namespace['lesson'].parts[0].play_sequence, [step])


if __name__ == '__main__':
    unittest.main()

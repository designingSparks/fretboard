"""Audio preparation checks using tiny WAV fixtures; no Qt or audio device needed."""

import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

import numpy as np

import audio_rendering
from audio_rendering import render_sequence


class AudioRenderingTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.sample_directory = Path(directory.name)

    def write_sample(self, midi_note, values):
        path = self.sample_directory / f'clean_{midi_note}.wav'
        with wave.open(str(path), 'wb') as sample:
            sample.setnchannels(1)
            sample.setsampwidth(2)
            sample.setframerate(1000)
            sample.writeframes(np.array(values, dtype='<i2').tobytes())

    def test_single_note_normalizes_before_truncation(self):
        self.write_sample(40, [1000, -2000, 4000, -4000])
        buffers = render_sequence([[('E', 0), 2]], self.sample_directory, 1000, 10)
        self.assertEqual(len(buffers), 1)
        self.assertEqual(np.frombuffer(buffers[0], dtype=np.int16).tolist(), [7782, -15564])

    def test_chords_preserve_note_order_and_configured_strum_delay(self):
        self.write_sample(40, [1000, 1000, 1000])
        self.write_sample(45, [2000, 2000])
        for delay, expected in ((0, [31128, 31128, 10376]),
                                (1, [10376, 31128, 31128])):
            with self.subTest(delay=delay):
                buffers = render_sequence(
                    [[('E', 0), ('A', 0), 10]], self.sample_directory, 1000, delay,
                )
                self.assertEqual(np.frombuffer(buffers[0], dtype=np.int16).tolist(), expected)

    def test_short_samples_are_not_padded_and_rests_keep_their_index(self):
        self.write_sample(64, [1000, -1000])
        buffers = render_sequence(
            [[('e', 0), 10], [5], [('e', 0), 0], [0]], self.sample_directory, 1000, 10,
        )
        self.assertEqual([len(buffer) for buffer in buffers], [4, 10, 0, 0])
        self.assertEqual(buffers[1], bytes(10))

    def test_silent_samples_remain_silent(self):
        self.write_sample(40, [0, 0, 0])
        buffers = render_sequence([[('E', 0), 10]], self.sample_directory, 1000, 10)
        self.assertEqual(buffers, [bytes(6)])

    def test_empty_sequence_needs_no_samples(self):
        self.assertEqual(render_sequence([], self.sample_directory, 1000, 10), [])

    def test_relative_sample_directory_is_resolved_from_the_module(self):
        with patch('audio_rendering.wavfile.read',
                   return_value=(1000, np.ones(3, dtype=np.int16))) as read:
            render_sequence([[('E', 0), 1]], 'clean', 1000, 10)
        expected = Path(audio_rendering.__file__).resolve().parent / 'clean' / 'clean_40.wav'
        read.assert_called_once_with(str(expected))

    def test_all_rows_are_validated_before_loading_samples(self):
        with patch('audio_rendering.wavfile.read') as read:
            with self.assertRaises(ValueError):
                render_sequence([[('E', 0), 10], [('x', 0), 10]],
                                self.sample_directory, 1000, 10)
        read.assert_not_called()


if __name__ == '__main__':
    unittest.main()

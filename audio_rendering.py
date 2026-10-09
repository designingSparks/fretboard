"""Prepare guitar sequences as mono int16 PCM buffers, without Qt."""

from pathlib import Path

import numpy as np

import wavfile
from models.sequence_step import parse_sequence_row


_OPEN_STRING_MIDI = {'E': 40, 'A': 45, 'D': 50, 'G': 55, 'B': 59, 'e': 64}


def render_sequence(steps, sample_directory: str | Path, sample_rate: int,
                    strum_delay_ms: int) -> list[bytes]:
    """Render named steps or legacy rows, keeping one buffer per input step.

    Samples are expected to be mono int16 WAV files at sample_rate. Relative
    directories resolve beside this module, independently of the working directory.
    Chords retain the supplied note order and are normalized before truncation.
    Short samples are not extended; rests produce silence for their full duration.
    """
    steps = [parse_sequence_row(row) for row in steps]
    sample_directory = Path(__file__).resolve().parent / sample_directory
    buffers = []
    for step in steps:
        if not step.notes:
            sample_count = int(sample_rate * step.duration_ms / 1000)
            buffers.append(np.zeros(sample_count, dtype=np.int16).tobytes())
            continue

        samples = [
            _load_sample(sample_directory, _OPEN_STRING_MIDI[string] + fret)
            for string, fret in step.notes
        ]
        mixed = _mix_notes(samples, sample_rate, strum_delay_ms)
        sample_count = int(sample_rate * (step.duration_ms / 1000.0))
        buffers.append(mixed[:sample_count].tobytes())

    return buffers


def _load_sample(sample_directory: Path, midi_note: int) -> np.ndarray:
    filename = f"clean_{midi_note}.wav"
    try:
        _, data = wavfile.read(str(sample_directory / filename))
        return data
    except Exception as error:
        print(f"Error loading {filename}: {error}")
        return np.array([], dtype=np.int16)


def _mix_notes(samples: list[np.ndarray], sample_rate: int,
               strum_delay_ms: int) -> np.ndarray:
    """Stagger notes in sequence order and normalize the sum to 95% amplitude."""
    delay_samples = int(sample_rate * strum_delay_ms / 1000)
    strummed = [
        np.concatenate((np.zeros(index * delay_samples, dtype=data.dtype), data))
        for index, data in enumerate(samples)
    ]
    max_length = max(len(data) for data in strummed)
    padded = [np.pad(data, (0, max_length - len(data)), 'constant') for data in strummed]
    mixed = np.sum([data.astype(np.float32) for data in padded], axis=0)

    max_amplitude = np.max(np.abs(mixed))
    if max_amplitude > 0:
        mixed = mixed / max_amplitude * 0.95

    return (mixed * np.iinfo(np.int16).max).astype(np.int16)

"""Pure preparation of note data for the browser; no drawing or playback state."""

import re

from constants import FRETBOARD_NOTES_SHARP, FRETBOARD_NOTES_FLAT, STRING_ID
from models.sequence_step import parse_sequence_row


def calculate_hidden_notes(play_sequence, background_positions):
    """Unique playback positions absent from all resolved backgrounds.

    Pass the result of resolve_background_notes(), or its position keys, so both
    plain background notes and every colored layer are considered. Preserve the
    first occurrence in playback order, including the distinction between E/e.
    """
    seen = set(background_positions)
    hidden = []
    for row in play_sequence:
        for position in parse_sequence_row(row).notes:
            if position not in seen:
                hidden.append(position)
                seen.add(position)
    return hidden


def _note_data(position, highlight_classes, use_sharp):
    string, fret = position
    names = FRETBOARD_NOTES_SHARP if use_sharp else FRETBOARD_NOTES_FLAT
    name = names[STRING_ID.index(string)][fret]
    label = name.replace('#', '♯').replace('b', '♭')
    return {'stringName': string, 'fret': fret, 'noteName': label,
            'hasFlat': '♭' in label, 'highlight': highlight_classes.get(name)}


def prepare_background_notes(backgrounds, highlight_classes, use_sharp):
    """Format the visible markers without changing resolved layer precedence."""
    return [{**_note_data(position, highlight_classes, use_sharp),
             **appearance, 'isBackground': True}
            for position, appearance in backgrounds.items()]


def prepare_hidden_notes(positions, highlight_classes, use_sharp):
    """Format playback-only markers for creation in the hidden state."""
    return [{**_note_data(position, highlight_classes, use_sharp),
             'isBackground': False, 'backgroundColor': None, 'backgroundLayers': []}
            for position in positions]


def prepare_sequence_steps(play_sequence, highlight_chord_root):
    """Keep row order (including rests) and annotate each chord's root positions."""
    steps = []
    for row in play_sequence:
        step = parse_sequence_row(row)
        positions = dict.fromkeys(step.notes)
        notes = [{'stringName': string, 'fret': fret} for string, fret in positions]
        if highlight_chord_root and step.chord_name:
            root = re.match(r'^[A-G][#b]?', step.chord_name.replace('♯', '#').replace('♭', 'b'))
            if root:
                for note, (string, fret) in zip(notes, positions):
                    index = STRING_ID.index(string)
                    note['isRoot'] = root.group() in (
                        FRETBOARD_NOTES_SHARP[index][fret], FRETBOARD_NOTES_FLAT[index][fret])
        steps.append({'notes': notes, 'chordName': step.chord_name})
    return steps

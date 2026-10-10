"""Colored background positions, independent of playback highlighting."""

from dataclasses import dataclass
import re

from models.sequence_step import SequenceStep


@dataclass(frozen=True, kw_only=True)
class BackgroundLayer:
    """A set of background notes with a #RGB or #RRGGBB color.

    Part.background_layers is ordered: the FIRST layer containing a (string,
    fret) position determines its background color. Later layers never overwrite
    that color, even when they repeat the position. Plain background_notes only
    provide the default appearance for positions absent from all colored layers.
    """

    notes: tuple[tuple[str, int], ...]
    color: str

    def __post_init__(self):
        if not isinstance(self.color, str) or not re.fullmatch(
                r'#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?', self.color):
            raise ValueError('Background color must be #RGB or #RRGGBB')
        notes = SequenceStep(notes=self.notes, duration_ms=0).notes
        object.__setattr__(self, 'notes', tuple(dict.fromkeys(notes)))


def resolve_background_notes(background_notes, background_layers=()):
    """Return unique positions with their color and all layer memberships.

    First layer wins: use the first membership to assign color and never replace
    it for later layers. Uncolored background_notes are only a fallback.
    """
    positions = {tuple(note): {'backgroundColor': None, 'backgroundLayers': []}
                 for note in background_notes}
    for index, layer in enumerate(background_layers):
        for note in layer.notes:
            info = positions.setdefault(note, {'backgroundColor': None, 'backgroundLayers': []})
            if not info['backgroundLayers']:
                info['backgroundColor'] = layer.color
            info['backgroundLayers'].append(index)
    return positions

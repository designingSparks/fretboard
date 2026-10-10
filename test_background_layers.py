"""Background precedence, rendering metadata and lesson authoring round trips."""

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from fretboard_export import part_filename, visible_part_content
from models.background_layer import BackgroundLayer, resolve_background_notes
from models.lesson_model import Part
from tablature.tablature_parser import print_lesson_code
from ui.fretboard_view import FretboardView


class BackgroundLayerTests(unittest.TestCase):
    def test_first_layer_wins_and_plain_notes_are_only_a_fallback(self):
        first = BackgroundLayer(notes=[('e', 3), ('e', 3)], color='#123456')
        second = BackgroundLayer(notes=[('e', 3), ('B', 3)], color='#abc')
        notes = resolve_background_notes([('e', 3), ('G', 4)], [first, second])
        self.assertEqual(first.notes, (('e', 3),))
        self.assertEqual(notes[('e', 3)]['backgroundColor'], '#123456')
        self.assertEqual(notes[('e', 3)]['backgroundLayers'], [0, 1])
        self.assertEqual(notes[('B', 3)]['backgroundColor'], '#abc')
        self.assertIsNone(notes[('G', 4)]['backgroundColor'])
        reversed_layers = resolve_background_notes([], [second, first])
        self.assertEqual(reversed_layers[('e', 3)]['backgroundColor'], '#abc')
        # Layer identity is the exact string/fret, not the pitch name.
        separate_g = BackgroundLayer(notes=[('E', 3)], color='#fff')
        self.assertEqual(resolve_background_notes([], [first, separate_g])[('E', 3)]
                         ['backgroundColor'], '#fff')

    def test_validation_and_immutable_note_positions(self):
        source = [['e', 3]]
        layer = BackgroundLayer(notes=source, color='#aBc')
        source[0][1] = 5
        self.assertEqual(layer.notes, (('e', 3),))
        for color in ('red', '#12', '#12345g', 'url(x)', None):
            with self.subTest(color=color), self.assertRaises(ValueError):
                BackgroundLayer(notes=[('e', 3)], color=color)
        with self.assertRaises(ValueError):
            BackgroundLayer(notes=[('X', 3)], color='#fff')
        with self.assertRaises(ValueError):
            Part('Invalid', [], [[('e', 3), 1000]], background_layers=['red'])
        self.assertEqual(Part('Playback only', [], [[('e', 3), 1000]])
                         .get_background_positions(), [])

    def test_bridge_creates_unique_markers_with_background_and_playback_roles(self):
        scripts = []
        view = SimpleNamespace(page=lambda: SimpleNamespace(runJavaScript=scripts.append))
        layers = [BackgroundLayer(notes=[('G', 4), ('e', 3)], color='#abc'),
                  BackgroundLayer(notes=[('e', 3), ('B', 3)], color='#def')]
        FretboardView.display_notes(view, [('G', 4)], background_layers=layers,
                                   play_sequence=[[('e', 3), ('E', 7), 1000]])
        args = json.loads('[' + scripts[0][len('displayNotes('):-2] + ']')
        markers = json.loads(args[0])
        self.assertEqual(len(markers), 4)
        markers = {(n['stringName'], n['fret']): n for n in markers}
        self.assertEqual(markers[('e', 3)]['backgroundColor'], '#abc')
        self.assertEqual(markers[('e', 3)]['backgroundLayers'], [0, 1])
        self.assertTrue(markers[('B', 3)]['isBackground'])
        self.assertFalse(markers[('E', 7)]['isBackground'])
        self.assertIsNone(markers[('E', 7)]['backgroundColor'])

    def test_generator_preserves_layer_colors_and_order(self):
        part = Part('Colored', [], [[('e', 3), 1000]], background_layers=[
            BackgroundLayer(notes=[('e', 3)], color='#123'),
            BackgroundLayer(notes=[('e', 3), ('B', 3)], color='#456'),
        ])
        output = io.StringIO()
        with redirect_stdout(output):
            print_lesson_code([part])
        namespace = {}
        exec(compile(output.getvalue(), '<generated lesson>', 'exec'), namespace)
        restored = namespace['lesson'].parts[0]
        self.assertEqual(restored.background_layers, part.background_layers)
        self.assertEqual(restored.get_background_positions(), [('e', 3), ('B', 3)])

    def test_export_includes_layers_and_filters_out_of_range_positions(self):
        part = Part('Layers', [], [[('e', 3), 1000]], background_layers=[
            BackgroundLayer(notes=[('E', 3), ('B', 20)], color='#123'),
        ])
        self.assertEqual(part_filename('layers', part), 'layers_EBe')
        notes, steps = visible_part_content(part, 15)
        self.assertEqual(notes, [('E', 3)])
        self.assertEqual(steps, part.play_sequence)


if __name__ == '__main__':
    unittest.main()

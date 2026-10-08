// Run: node --test test_root_highlights.cjs
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

test('root color follows shared and open notes, clears on stop, and preserves fixed highlights', () => {
    const markers = new Map();
    function marker(string, fret, fixed = false) {
        const classes = new Set(['inactive', ...(fixed ? ['highlight1'] : [])]);
        const note = {dataset: {}, classList: {
            add: name => classes.add(name), remove: name => classes.delete(name),
            contains: name => classes.has(name),
        }};
        const selector = fret === 0
            ? `td.string-label[data-string="${string}"] .open-string-note`
            : `td.fret[data-string="${string}"][data-fret="${fret}"] .note`;
        markers.set(selector, note);
        return note;
    }
    const g = marker(0, 3), c = marker(2, 5), openG = marker(2, 0);
    const fixed = marker(1, 8, true);
    const window = {};
    const context = {
        window, console: {log() {}, error(message) { throw new Error(message); }},
        GUITAR_TUNING: ['e', 'B', 'G', 'D', 'A', 'E'].map(name => ({name})),
        clearChordSelection() {},
        document: {
            querySelector: selector => markers.get(selector),
            querySelectorAll: selector => [...markers.values()].filter(note =>
                selector !== '[data-chord-root]' || note.dataset.chordRoot),
        },
    };
    const source = fs.readFileSync(path.join(__dirname, 'main.js'), 'utf8');
    vm.runInNewContext(source.slice(source.indexOf('function clearChordRootHighlights()'),
        source.indexOf('// --- Animation Trigger ---')), context);
    const select = notes => window.highlightNotes(JSON.stringify(notes));
    select([{stringName: 'e', fret: 3, isRoot: true}]);
    assert.ok(g.classList.contains('highlight1'));
    select([{stringName: 'e', fret: 3, isRoot: false},
        {stringName: 'G', fret: 5, isRoot: true}]);
    assert.equal(g.classList.contains('highlight1'), false);
    assert.equal(g.classList.contains('inactive'), false);
    assert.ok(c.classList.contains('highlight1'));
    select([{stringName: 'G', fret: 0, isRoot: true}]);
    assert.equal(c.classList.contains('highlight1'), false);
    assert.ok(openG.classList.contains('highlight1'));
    window.clearNoteHighlights();
    assert.equal(openG.classList.contains('highlight1'), false);
    assert.ok([...markers.values()].every(note => note.classList.contains('inactive')));
    select([{stringName: 'B', fret: 8, isRoot: true}]);
    window.clearNoteHighlights();
    assert.ok(fixed.classList.contains('highlight1'));
});

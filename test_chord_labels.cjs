// Run: node --test test_chord_labels.cjs
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

function setup() {
    class Element {
        constructor() {
            this.children = []; this.attributes = {}; this.dataset = {}; this.listeners = {};
            this.disabled = false;
            const classes = new Set();
            this.classList = {
                toggle: (key, selected) => selected ? classes.add(key) : classes.delete(key),
                remove: key => classes.delete(key),
                contains: key => classes.has(key),
            };
        }
        replaceChildren() { this.children = []; }
        appendChild(child) { this.children.push(child); }
        setAttribute(name, value) { this.attributes[name] = value; }
        addEventListener(name, callback) { this.listeners[name] = callback; }
        click() { this.listeners.click(); }
    }
    const container = new Element();
    const panel = new Element();
    const caption = new Element();
    const selected = [];
    const window = {
        highlightNotes: json => { selected.splice(0, selected.length, ...JSON.parse(json)); },
        clearNoteHighlights: () => { selected.length = 0; window.clearChordSelection(); },
    };
    const elements = {'chord-labels': container, 'chord-panel': panel, 'chord-label-title': caption};
    const context = {window, document: {getElementById: id => elements[id], createElement: () => new Element()}};
    vm.runInNewContext(fs.readFileSync(path.join(__dirname, 'chord_labels.js'), 'utf8'), context);
    return {window, container, panel, caption, selected, pressed: () => container.children
        .flatMap((button, index) => button.classList.contains('selected') ? [index] : [])};
}

const n = (stringName, fret) => ({stringName, fret});
const steps = [
    {chordName: 'G', notes: [n('e', 3), n('B', 3), n('G', 4)]},
    {chordName: 'C', notes: [n('e', 3), n('B', 5), n('G', 5)]},
    {chordName: 'D', notes: [n('e', 5), n('B', 7), n('G', 7)]},
];

test('initial labels are neutral; clicks select only the matching triad including shared notes', () => {
    const app = setup();
    app.window.renderChordSequence(steps);
    assert.equal(app.container.hidden, false);
    assert.deepEqual(app.container.children.map(b => b.children[0].textContent), ['G', 'C', 'D']);
    assert.deepEqual(app.pressed(), []);
    assert.deepEqual(app.selected, []);
    app.container.children[0].click();
    assert.deepEqual(app.pressed(), [0]);
    assert.deepEqual(app.selected, steps[0].notes);
    app.container.children[1].click();
    assert.deepEqual(app.pressed(), [1]);
    assert.deepEqual(app.selected, steps[1].notes);
    assert.equal(app.container.children[0].attributes['aria-pressed'], 'false');
    assert.equal(app.container.children[1].attributes['aria-pressed'], 'true');
});

test('playback owns selection and stop clears both notes and labels', () => {
    const app = setup();
    app.window.renderChordSequence(steps);
    app.container.children[2].click();
    app.window.setChordPlaybackState('playing');
    assert.deepEqual(app.pressed(), []);
    assert.ok(app.container.children.every(b => b.disabled));
    app.window.highlightSequenceStep(0);
    app.container.children[2].click();
    assert.deepEqual(app.pressed(), [0]);
    assert.deepEqual(app.selected, steps[0].notes);
    app.window.highlightSequenceStep(2);
    assert.deepEqual(app.pressed(), [2]);
    assert.deepEqual(app.selected, steps[2].notes);
    app.window.setChordPlaybackState('stopped');
    app.window.highlightSequenceStep(1); // Late update must not revive stopped selection.
    assert.deepEqual(app.pressed(), []);
    assert.deepEqual(app.selected, []);
    assert.ok(app.container.children.every(b => !b.disabled));
});

test('duplicate names and unlabelled steps retain their original sequence indices', () => {
    const app = setup();
    const sequence = [steps[0], {notes: [n('e', 0)], chordName: null},
        {notes: [n('e', 7), n('B', 8), n('G', 7)], chordName: 'G'}];
    app.window.renderChordSequence(sequence);
    app.container.children[1].click();
    assert.deepEqual(app.selected, sequence[2].notes);
    assert.equal(app.container.children[1].attributes['aria-label'], 'G, step 3');
    app.window.setChordPlaybackState('playing');
    app.window.highlightSequenceStep(1);
    assert.deepEqual(app.pressed(), []);
    assert.deepEqual(app.selected, sequence[1].notes);
    app.window.highlightSequenceStep(2);
    assert.deepEqual(app.pressed(), [1]);
});

test('part switches reset selection and hide labels for legacy sequences', () => {
    const app = setup();
    app.window.renderChordSequence(steps);
    app.window.setChordPlaybackState('playing');
    app.window.highlightSequenceStep(1);
    app.window.renderChordSequence([{notes: [n('e', 0)], chordName: null}]);
    assert.equal(app.container.hidden, true);
    assert.equal(app.panel.hidden, true);
    assert.equal(app.container.children.length, 0);
    assert.deepEqual(app.selected, []);
    app.window.setChordPlaybackState('playing');
    app.window.highlightSequenceStep(0);
    assert.deepEqual(app.selected, [n('e', 0)]);
    app.window.highlightSequenceStep(-1);
    app.window.highlightSequenceStep(99);
    assert.deepEqual(app.selected, [n('e', 0)]);
});

test('lesson caption updates, can be hidden, and defaults on the next lesson', () => {
    const app = setup();
    app.window.renderChordSequence(steps, 'Chord <selected>');
    assert.equal(app.caption.textContent, 'Chord <selected>');
    assert.equal(app.caption.hidden, false);
    assert.equal(app.panel.hidden, false);
    assert.equal(app.container.attributes['aria-label'], 'Chord <selected>');
    app.window.renderChordSequence(steps, '');
    assert.equal(app.caption.hidden, true);
    assert.equal(app.panel.hidden, false);
    app.window.renderChordSequence(steps);
    assert.equal(app.caption.textContent, 'Triad playing');
    assert.equal(app.caption.hidden, false);
});

test('paused inspection preserves playback position for a resume state transition', () => {
    const app = setup();
    app.window.renderChordSequence(steps);
    app.window.setChordPlaybackState('playing');
    app.window.highlightSequenceStep(1);
    app.window.setChordPlaybackState('paused');
    assert.deepEqual(app.pressed(), [1]);
    app.container.children[2].click();
    assert.deepEqual(app.pressed(), [2]);
    app.window.setChordPlaybackState('playing');
    assert.deepEqual(app.pressed(), [1]);
    assert.deepEqual(app.selected, steps[1].notes);
});

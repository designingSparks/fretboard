// Run: node --test test_chord_labels.cjs
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

function setup(markerPositions = []) {
    let focused = null;
    class Element {
        constructor() {
            this.children = []; this.attributes = {}; this.dataset = {}; this.listeners = {};
            this.style = {setProperty(name, value) { this[name] = value; }};
            this.disabled = false;
            const classes = new Set();
            this.classList = {
                add: key => classes.add(key),
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
        focus(options) { focused = this; assert.equal(options.preventScroll, true); }
    }
    const container = new Element();
    const panel = new Element();
    const caption = new Element();
    const selected = [];
    const highlightHistory = [];
    const window = {
        highlightNotes: json => {
            selected.splice(0, selected.length, ...JSON.parse(json));
            highlightHistory.push([...selected]);
        },
        clearNoteHighlights: () => { selected.length = 0; window.clearChordSelection(); },
    };
    const elements = {'chord-labels': container, 'chord-panel': panel, 'chord-label-title': caption};
    const markers = new Map(markerPositions.map(([string, fret]) => {
        const note = new Element();
        note.classList.add('inactive');
        if (fret === 0) note.openStringLabel = {hidden: false};
        const selector = fret === 0
            ? `td.string-label[data-string="${string}"] .open-string-note`
            : `td.fret[data-string="${string}"][data-fret="${fret}"] .note`;
        return [selector, note];
    }));
    const listeners = {};
    const timers = new Map();
    let timerId = 0;
    const flushTimers = () => {
        for (const [id, callback] of [...timers]) {
            timers.delete(id);
            callback();
        }
    };
    const context = {window,
        console: {log() {}, error(message) { throw new Error(message); }},
        GUITAR_TUNING: ['e', 'B', 'G', 'D', 'A', 'E'].map(name => ({name})),
        clearChordSelection: () => window.clearChordSelection(),
        setTimeout: callback => { timers.set(++timerId, callback); return timerId; },
        clearTimeout: id => timers.delete(id),
        document: {
        getElementById: id => elements[id], createElement: () => new Element(),
        querySelector: selector => markers.get(selector),
        querySelectorAll: selector => [...markers.values()].filter(note =>
            selector !== '[data-chord-root]' || note.dataset.chordRoot),
        addEventListener: (name, handler) => { listeners[name] = handler; },
    }};
    vm.runInNewContext(fs.readFileSync(path.join(__dirname, 'chord_labels.js'), 'utf8'), context);
    const main = fs.readFileSync(path.join(__dirname, 'main.js'), 'utf8');
    vm.runInNewContext(main.slice(0, main.indexOf('// --- 1. Configuration ---')), context);
    if (markerPositions.length) {
        vm.runInNewContext(main.slice(main.indexOf('function clearChordRootHighlights()'),
            main.indexOf('// --- Animation Trigger ---')), context);
        [...markers.values()].forEach((marker, index) => {
            context.initializeNoteAppearance(marker, markerPositions[index][2] || {});
        });
    }
    const keydown = (key, options = {}) => {
        const event = new Event('keydown', {cancelable: true});
        Object.assign(event, {key, ...options});
        listeners.keydown(event);
        return event;
    };
    return {window, container, panel, caption, selected, keydown, flushTimers, highlightHistory, markers,
        focused: () => focused,
        pressed: () => container.children
        .flatMap((button, index) => button.classList.contains('selected') ? [index] : [])};
}

const n = (stringName, fret) => ({stringName, fret});
const steps = [
    {chordName: 'G', notes: [n('e', 3), n('B', 3), n('G', 4)]},
    {chordName: 'C', notes: [n('e', 3), n('B', 5), n('G', 5)]},
    {chordName: 'D', notes: [n('e', 5), n('B', 7), n('G', 7)]},
];

test('playback-only markers hide between steps, rests and previews; pause retains the current note', () => {
    const app = setup([
        [0, 3, {isBackground: true, backgroundColor: '#123456', backgroundLayers: [0, 1]}],
        [5, 7, {isBackground: false}],
        [2, 0, {isBackground: false}],
    ]);
    const [background, low, open] = [...app.markers.values()];
    const visible = marker => !marker.classList.contains('note-hidden');
    const sequence = [
        {chordName: 'G', notes: [{...n('e', 3), isRoot: true}]},
        {chordName: 'G', notes: [n('E', 7)]},
        {chordName: 'G', notes: [{...n('G', 0), isRoot: true}]},
        {notes: []},
    ];
    assert.equal(background.style['--background-note-color'], '#123456');
    assert.equal(background.style['--background-note-text'], '#fff');
    assert.equal(background.dataset.backgroundLayers, '[0,1]');
    assert.equal(visible(low), false);
    app.window.renderChordSequence(sequence);
    assert.ok(visible(background));
    app.container.children[1].listeners.mouseenter();
    assert.ok(visible(low));
    app.container.children[1].listeners.mouseleave();
    app.flushTimers();
    assert.equal(visible(low), false);
    app.window.setChordPlaybackState('playing');
    app.window.highlightSequenceStep(1);
    assert.ok(visible(low));
    app.window.highlightSequenceStep(2);
    assert.equal(visible(low), false);
    assert.ok(visible(open));
    assert.equal(open.openStringLabel.hidden, true);
    app.window.setChordPlaybackState('paused');
    assert.ok(visible(open));
    app.container.children[1].click();
    assert.ok(visible(low));
    assert.equal(visible(open), false);
    app.window.setChordPlaybackState('playing');
    assert.ok(visible(open));
    assert.equal(visible(low), false);
    app.window.highlightSequenceStep(3);
    assert.equal(visible(open), false);
    assert.equal(open.openStringLabel.hidden, false);
    assert.ok(visible(background));
    assert.ok(background.classList.contains('inactive'));
    assert.equal(background.classList.contains('highlight1'), false);
    assert.equal(background.style['--background-note-color'], '#123456');
    app.window.highlightNote('G', 0);
    assert.ok(visible(open));
    app.window.setChordPlaybackState('stopped');
    assert.equal(visible(open), false);
    assert.equal(open.openStringLabel.hidden, false);
    app.window.renderChordSequence([]);
    assert.equal(visible(low), false);
});

test('tutorial highlights only its three selected chord positions, including only that triad root', () => {
    // Markers in low E to high e order; all belong to the same barre chord.
    const app = setup([[5, 3], [4, 5], [3, 5], [2, 4], [1, 3], [0, 3]]);
    const markers = [...app.markers.values()];
    const selectedIndices = () => markers.flatMap((note, index) =>
        note.classList.contains('inactive') ? [] : [index]);
    const rootIndices = () => markers.flatMap((note, index) =>
        note.classList.contains('highlight1') ? [index] : []);
    const parts = [
        [n('G', 4), n('B', 3), {...n('e', 3), isRoot: true}],
        [{...n('D', 5), isRoot: true}, n('G', 4), n('B', 3)],
    ];
    for (const [index, notes] of parts.entries()) {
        app.window.renderChordSequence([{chordName: 'G', notes}], 'Selected triad');
        const expected = index === 0 ? [3, 4, 5] : [2, 3, 4];
        assert.deepEqual(selectedIndices(), expected);
        assert.deepEqual(rootIndices(), [index === 0 ? 5 : 2]);
        app.window.setChordPlaybackState('playing');
        app.window.highlightSequenceStep(0);
        assert.deepEqual(selectedIndices(), expected);
        app.window.setChordPlaybackState('stopped');
        assert.deepEqual(selectedIndices(), []);
        assert.deepEqual(rootIndices(), []);
        app.container.children[0].click();
        assert.deepEqual(selectedIndices(), expected);
        assert.deepEqual(rootIndices(), [index === 0 ? 5 : 2]);
    }
});

test('plain arrows move chord selection, notes and focus without scrolling', () => {
    const app = setup();
    const sequence = [steps[0], {notes: [n('e', 0)]}, steps[1], {...steps[2], chordName: 'G'}];
    app.window.renderChordSequence(sequence);
    const [first, second, third] = app.container.children;
    first.listeners.mouseenter();
    first.click();
    assert.equal(app.keydown('ArrowRight').defaultPrevented, true);
    assert.deepEqual(app.selected, sequence[2].notes);
    assert.deepEqual(app.pressed(), [1]);
    assert.equal(app.focused(), second);
    first.listeners.mouseleave();
    assert.deepEqual(app.pressed(), [1]);
    app.keydown('ArrowRight');
    app.keydown('ArrowRight');
    assert.deepEqual(app.selected, sequence[3].notes);
    assert.equal(app.focused(), third);
    app.keydown('ArrowLeft');
    assert.deepEqual(app.selected, sequence[2].notes);
    app.keydown('ArrowLeft');
    app.keydown('ArrowLeft');
    assert.deepEqual(app.selected, sequence[0].notes);
    assert.equal(app.focused(), first);
});

test('arrows initialize selection and respect modifiers and playback', () => {
    const app = setup();
    app.window.renderChordSequence(steps);
    app.window.clearNoteHighlights();
    app.keydown('ArrowRight');
    assert.deepEqual(app.selected, steps[0].notes);
    for (const modifier of ['ctrlKey', 'metaKey', 'altKey', 'shiftKey']) {
        app.keydown('ArrowRight', {[modifier]: true});
        assert.deepEqual(app.selected, steps[0].notes);
    }
    app.window.setChordPlaybackState('playing');
    app.window.highlightSequenceStep(1);
    app.keydown('ArrowRight');
    assert.deepEqual(app.selected, steps[1].notes);
    app.window.setChordPlaybackState('paused');
    app.keydown('ArrowRight');
    assert.deepEqual(app.selected, steps[2].notes);
    app.window.setChordPlaybackState('playing');
    assert.deepEqual(app.selected, steps[1].notes);
    app.window.renderChordSequence(steps);
    app.keydown('ArrowLeft');
    assert.deepEqual(app.selected, steps[0].notes);
    app.window.renderChordSequence([]);
    app.keydown('ArrowRight');
    assert.deepEqual(app.selected, []);
});

test('first chord is selected by default; clicks select the matching triad including shared notes', () => {
    const app = setup();
    app.window.renderChordSequence(steps);
    assert.equal(app.container.hidden, false);
    assert.deepEqual(app.container.children.map(b => b.children[0].textContent), ['G', 'C', 'D']);
    assert.deepEqual(app.pressed(), [0]);
    assert.deepEqual(app.selected, steps[0].notes);
    app.container.children[0].click();
    assert.deepEqual(app.pressed(), [0]);
    assert.deepEqual(app.selected, steps[0].notes);
    app.container.children[1].click();
    assert.deepEqual(app.pressed(), [1]);
    assert.deepEqual(app.selected, steps[1].notes);
    assert.equal(app.container.children[0].attributes['aria-pressed'], 'false');
    assert.equal(app.container.children[1].attributes['aria-pressed'], 'true');
});

test('braced labels render two lines and still select the exact sequence row', () => {
    const app = setup();
    const sequence = [
        {...steps[0], chordName: 'G_{3-4}'},
        {...steps[1], chordName: 'C_{3-5}'},
        {...steps[2], chordName: 'D_{5-7}'},
        {chordName: 'G_{7-8}', notes: [n('e', 7), n('B', 8), n('G', 7)]},
    ];
    app.window.renderChordSequence(sequence);
    assert.deepEqual(app.container.children.map(b => b.children.map(s => s.textContent)),
        [['G', '3-4'], ['C', '3-5'], ['D', '5-7'], ['G', '7-8']]);
    const first = app.container.children[0];
    assert.equal(first.children[0].className, 'chord-label-main');
    assert.equal(first.children[1].className, 'chord-label-subtext');
    assert.equal(first.dataset.label, 'G');
    assert.equal(first.dataset.subtext, '3-4');
    assert.equal(first.attributes['aria-label'], 'G, 3-4, step 1');
    app.container.children[3].click();
    assert.deepEqual(app.selected, sequence[3].notes);
    assert.deepEqual(app.pressed(), [3]);
    app.window.setChordPlaybackState('playing');
    app.window.highlightSequenceStep(0);
    assert.deepEqual(app.selected, sequence[0].notes);
    assert.deepEqual(app.pressed(), [0]);
    assert.equal(sequence[0].chordName, 'G_{3-4}');
});

test('brace text is literal, optional underscore is removed, and plain labels stay single-line', () => {
    const app = setup();
    const cases = [
        ['G', ['G']], ['C{8-9}', ['C', '8-9']], ['G_{}', ['G']],
        ['G_{3-4', ['G_{3-4']], ['G_{<b>3-4</b>}', ['G', '<b>3-4</b>']],
    ];
    for (const [name, expected] of cases) {
        app.window.renderChordSequence([{...steps[0], chordName: name}]);
        assert.deepEqual(app.container.children[0].children.map(s => s.textContent), expected);
    }
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

test('hover previews the exact labelled step and leaving restores the selection', () => {
    const app = setup();
    const sequence = [
        {...steps[0], chordName: 'G_{3-4}'},
        {chordName: null, notes: [n('e', 0)]},
        {chordName: 'G_{7-8}', notes: [n('e', 7), n('B', 8), n('G', 7)]},
    ];
    app.window.renderChordSequence(sequence);
    const [first, second] = app.container.children;
    first.listeners.mouseenter();
    assert.deepEqual(app.selected, sequence[0].notes);
    assert.deepEqual(app.pressed(), [0]);
    first.listeners.mouseleave();
    app.flushTimers();
    assert.deepEqual(app.selected, sequence[0].notes);
    assert.deepEqual(app.pressed(), [0]);
    first.click();
    second.listeners.mouseenter();
    assert.deepEqual(app.selected, sequence[2].notes);
    assert.deepEqual(app.pressed(), [1]);
    second.listeners.mouseleave();
    app.flushTimers();
    assert.deepEqual(app.selected, sequence[0].notes);
    assert.deepEqual(app.pressed(), [0]);
    second.listeners.mouseenter();
    second.click();
    second.listeners.mouseleave();
    app.flushTimers();
    assert.deepEqual(app.selected, sequence[2].notes);
});

test('hover cannot override playback, including when playback starts during a preview', () => {
    const app = setup();
    app.window.renderChordSequence(steps);
    const button = app.container.children[2];
    button.listeners.mouseenter();
    app.window.setChordPlaybackState('playing');
    app.window.highlightSequenceStep(1);
    button.listeners.mouseleave();
    button.listeners.mouseenter();
    assert.deepEqual(app.selected, steps[1].notes);
    assert.deepEqual(app.pressed(), [1]);
    app.window.setChordPlaybackState('paused');
    button.listeners.mouseenter();
    assert.deepEqual(app.selected, steps[2].notes);
    button.listeners.mouseleave();
    app.flushTimers();
    assert.deepEqual(app.selected, steps[1].notes);
    button.listeners.mouseenter();
    app.window.setChordPlaybackState('playing');
    button.listeners.mouseleave();
    assert.deepEqual(app.selected, steps[1].notes);
});

test('stopping or changing parts during a preview clears the previous selection', () => {
    const app = setup();
    app.window.renderChordSequence(steps);
    const [first, second] = app.container.children;
    first.click();
    second.listeners.mouseenter();
    app.window.setChordPlaybackState('stopped');
    second.listeners.mouseleave();
    assert.deepEqual(app.selected, []);
    first.click();
    second.listeners.mouseenter();
    app.window.renderChordSequence([steps[2]]);
    second.listeners.mouseleave();
    app.flushTimers();
    assert.deepEqual(app.selected, steps[2].notes);
    assert.deepEqual(app.pressed(), [0]);
});

test('moving across hover targets never flashes the clicked chord between previews', () => {
    const app = setup();
    app.window.renderChordSequence(steps);
    const [first, second, third] = app.container.children;
    first.click();
    app.highlightHistory.length = 0;
    second.listeners.mouseenter();
    second.listeners.mouseleave();
    assert.deepEqual(app.selected, steps[1].notes);
    third.listeners.mouseenter();
    app.flushTimers();
    assert.deepEqual(app.highlightHistory, [steps[1].notes, steps[2].notes]);
    third.listeners.mouseleave();
    app.flushTimers();
    assert.deepEqual(app.selected, steps[0].notes);
});

test('pending hover restoration cannot override navigation, playback or a new part', () => {
    for (const action of ['navigate', 'play', 'stop', 'part']) {
        const app = setup();
        app.window.renderChordSequence(steps);
        const button = app.container.children[2];
        button.listeners.mouseenter();
        button.listeners.mouseleave();
        if (action === 'navigate') app.keydown('ArrowRight');
        if (action === 'play') {
            app.window.setChordPlaybackState('playing');
            app.window.highlightSequenceStep(1);
        }
        if (action === 'stop') app.window.setChordPlaybackState('stopped');
        if (action === 'part') {
            app.window.renderChordSequence([{chordName: null, notes: [n('e', 0)]}, steps[1]]);
            assert.deepEqual(app.pressed(), [0]);
        }
        const historyLength = app.highlightHistory.length;
        app.flushTimers();
        assert.equal(app.highlightHistory.length, historyLength);
        assert.deepEqual(app.selected, action === 'stop' ? [] : steps[1].notes);
    }
});

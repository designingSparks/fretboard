// Exercise actual initialization, marker creation and selection without Qt.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function setup() {
    class Element {
        constructor() {
            this.children = []; this.dataset = {}; this.listeners = {}; this.attributes = {};
            this.style = {setProperty(name, value) { this[name] = value; }};
            this.classes = new Set();
            this.classList = {
                add: (...names) => names.forEach(name => this.classes.add(name)),
                remove: (...names) => names.forEach(name => this.classes.delete(name)),
                contains: name => this.classes.has(name),
                toggle: (name, enabled) => enabled ? this.classes.add(name) : this.classes.delete(name),
            };
        }
        set className(value) { this.classes = new Set(value.split(' ')); }
        set textContent(value) { this.text = value; this.children = []; }
        get textContent() { return this.text; }
        appendChild(child) { this.children.push(child); child.parentElement = this; }
        replaceChildren() { this.children = []; }
        remove() { this.parentElement.children = this.parentElement.children.filter(child => child !== this); }
        setAttribute(name, value) { this.attributes[name] = value; }
        addEventListener(name, handler) { this.listeners[name] = handler; }
    }
    const tuning = ['e', 'B', 'G', 'D', 'A', 'E'];
    const cells = new Map();
    tuning.forEach((_, string) => {
        cells.set(`td.string-label[data-string="${string}"]`, new Element());
        for (let fret = 1; fret <= 24; fret++)
            cells.set(`td.fret[data-string="${string}"][data-fret="${fret}"]`, new Element());
    });
    const labels = new Element(), panel = new Element(), caption = new Element();
    const markers = () => [...cells.values()].flatMap(cell => cell.children)
        .filter(child => child.classes.has('note') || child.classes.has('open-string-note'));
    const context = {
        console, setTimeout, clearTimeout,
        GUITAR_TUNING: tuning.map(name => ({name})), FLAT_SYMBOL_LETTER_SPACING: '-1px',
        setSequenceOutlines(groups) { context.groups = groups; }, drawStringsAsSVG() {},
        document: {
            getElementById: id => ({'chord-labels': labels, 'chord-panel': panel,
                'chord-label-title': caption})[id],
            createElement: () => new Element(),
            querySelector(selector) {
                const [cellSelector, classSelector] = selector.split(' ');
                const cell = cells.get(cellSelector);
                return classSelector ? cell?.children.find(child => child.classes.has(classSelector.slice(1))) : cell;
            },
            querySelectorAll: selector => markers().filter(note =>
                selector !== '[data-chord-root]' || note.dataset.chordRoot),
        },
    };
    context.window = context;
    vm.createContext(context);
    const main = fs.readFileSync(path.join(__dirname, 'main.js'), 'utf8');
    vm.runInContext(main.slice(main.indexOf('function clearPreviousPart()'),
        main.indexOf('/**\n * Highlights a specific scale position')), context);
    vm.runInContext(main.slice(main.indexOf('window.displayNotes ='),
        main.indexOf('// --- Animation Trigger ---')), context);
    vm.runInContext(fs.readFileSync(path.join(__dirname, 'chord_labels.js'), 'utf8'), context);
    return {context, markers, cells, labels};
}

const position = (stringName, fret) => ({stringName, fret});
const marker = (stringName, fret) => ({...position(stringName, fret), noteName: 'G'});

test('one initialization creates backgrounds and hidden markers before selecting a chord', () => {
    const app = setup();
    app.context.displayNotes({
        backgroundNotes: [{...marker('e', 3), backgroundColor: '#123456', backgroundLayers: [0, 1]}],
        hiddenNotes: [marker('E', 7), marker('G', 0)],
        sequenceSteps: [
            {notes: [position('e', 3), position('E', 7)], chordName: 'G'},
            {notes: [position('G', 0)], chordName: 'G'},
            {notes: []},
        ],
    });
    assert.equal(app.markers().length, 3);
    const [background] = app.markers().filter(note => note.classList.contains('background-colored'));
    const open = app.markers().find(note => note.classList.contains('open-string-note'));
    const low = app.markers().find(note => note.dataset.fret === 7);
    assert.equal(background.style['--background-note-color'], '#123456');
    assert.equal(background.classList.contains('inactive'), false);
    assert.equal(low.classList.contains('note-hidden'), false); // First chord selection.
    assert.equal(open.classList.contains('note-hidden'), true);
    assert.equal(open.openStringLabel.hidden, false);

    app.labels.children[1].listeners.click();
    assert.equal(open.classList.contains('note-hidden'), false);
    assert.equal(open.openStringLabel.hidden, true);
    assert.equal(low.classList.contains('note-hidden'), true);
    assert.equal(background.classList.contains('inactive'), true);
    app.context.setChordPlaybackState('playing');
    app.context.highlightSequenceStep(2); // Rest.
    assert.equal(open.classList.contains('note-hidden'), true);
    assert.equal(background.classList.contains('note-hidden'), false);

    app.context.displayNotes({backgroundNotes: [marker('B', 3)]});
    assert.equal(app.markers().length, 1);
    const openCell = app.cells.get('td.string-label[data-string="2"]');
    assert.equal(openCell.textContent, 'G');
    assert.equal(openCell.children.length, 0);
    assert.equal(app.labels.children.length, 0);
});

test('unlabelled playback-only parts start hidden and single-note playback reveals open strings', () => {
    const app = setup();
    app.context.displayNotes({hiddenNotes: [marker('e', 0)]});
    const [note] = app.markers();
    assert.equal(note.classList.contains('note-hidden'), true);
    app.context.highlightNote('e', 0);
    assert.equal(note.classList.contains('note-hidden'), false);
    assert.equal(note.openStringLabel.hidden, true);
    app.context.clearNoteHighlights();
    assert.equal(note.classList.contains('note-hidden'), true);
    assert.equal(note.openStringLabel.hidden, false);
});

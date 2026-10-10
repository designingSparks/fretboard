// Run with node --test Modular/test_fretboard_export.cjs
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

test('export URL selects 15 frets while the regular player defaults to 24', () => {
    const source = fs.readFileSync(path.join(__dirname, 'main.js'), 'utf8');
    const config = source.slice(source.indexOf('const requestedFrets'), source.indexOf('const GUITAR_TUNING'));
    for (const [query, expected] of [['?frets=15', 15], ['?frets=24', 24], ['', 24],
        ['?frets=0', 24], ['?frets=25', 24], ['?frets=15.5', 24], ['?frets=bad', 24]]) {
        assert.equal(vm.runInNewContext(`${config}\nNUM_FRETS`, {
            window: {location: {search: query}}, URLSearchParams,
        }), expected);
    }
});

function fixture() {
    class Element {
        constructor(tag, rect = {}, style = {}, classes = []) {
            this.tag = tag;
            this.attrs = {};
            this.children = [];
            this.style = style;
            this.rect = {left: 100, top: 50, width: 30, height: 30, ...rect};
            const classNames = new Set(classes);
            this.classList = {
                add: name => classNames.add(name), remove: name => classNames.delete(name),
                contains: name => classNames.has(name),
                toggle: (name, enabled) => enabled ? classNames.add(name) : classNames.delete(name),
            };
            this.textContent = '';
        }
        setAttribute(name, value) { this.attrs[name] = String(value); }
        getAttribute(name) { return this.attrs[name]; }
        appendChild(child) { this.children.push(child); }
        getBoundingClientRect() { return this.rect; }
        getPointAtLength() {
            const tokens = this.attrs.d.split(' ');
            return {x: Number(tokens[1]), y: Number(tokens[2])};
        }
        cloneNode() {
            const copy = new Element(this.tag, this.rect, this.style);
            copy.attrs = {...this.attrs};
            return copy;
        }
    }
    const header = new Element('div'), container = new Element('div');
    const diagram = new Element('div', {width: 1600, height: 260});
    const baseStyle = {color: 'rgb(0, 0, 0)', fontFamily: 'Arial', fontSize: '14px',
        fontWeight: '700', letterSpacing: 'normal'};
    const note = new Element('div', {left: 170, top: 70},
        {...baseStyle, backgroundColor: 'rgb(254, 193, 187)'});
    note.textContent = 'G';
    note.activeStyle = {...note.style, backgroundColor: 'rgb(231, 76, 60)', color: 'rgb(255, 255, 255)'};
    const open = new Element('div', {left: 105, top: 100},
        {...baseStyle, backgroundColor: 'rgb(188, 188, 188)'});
    open.textContent = 'B';
    open.activeStyle = {...open.style, backgroundColor: 'rgb(68, 68, 68)', color: 'rgb(255, 255, 255)'};
    const openCell = new Element('td', {}, baseStyle, ['string-label']);
    openCell.appendChild(open);
    openCell.textContent = 'B';
    const label = new Element('td', {}, baseStyle, ['string-label']);
    label.textContent = 'e';
    const footer = new Element('th', {left: 1660, top: 270, width: 30, height: 15}, baseStyle);
    footer.textContent = '24';
    const cell = new Element('td', {left: 145, top: 65, width: 80, height: 35}, {
        backgroundColor: 'rgb(255, 255, 255)',
        borderRightWidth: '1px', borderRightColor: '#525151',
        borderLeftWidth: '8px', borderLeftColor: '#333',
        borderTopWidth: '1px', borderTopColor: '#ccc',
        borderBottomWidth: '1px', borderBottomColor: '#ccc',
    }, ['nut']);
    const row = {};
    row.parentElement = {firstElementChild: row, lastElementChild: row};
    cell.parentElement = row;
    const dot = new Element('div', {left: 200, top: 120, width: 18, height: 18},
        {backgroundColor: '#e3e3e3'});
    const strings = new Element('svg', {width: 1600, height: 260});
    const string = new Element('path');
    string.setAttribute('d', 'M 40 35 L 5000 35');
    string.setAttribute('stroke', '#a9a9a9');
    string.setAttribute('stroke-width', '2.1');
    strings.appendChild(string);
    for (let index = 1; index < 6; index++) {
        const next = string.cloneNode();
        next.setAttribute('d', `M 40 ${35 + index * 35} L 5000 ${35 + index * 35}`);
        strings.appendChild(next);
    }
    const outlines = new Element('svg', {width: 1600, height: 260});
    const outline = new Element('path');
    outline.setAttribute('d', 'M 0 0 L 100 0 L 50 100 Z');
    outline.setAttribute('data-sequence-group', '0');
    outlines.appendChild(outline);
    diagram.querySelectorAll = selector => ({
        'td.fret': [cell], '.fret-marker-dot': [dot],
        '.note, .open-string-note': [note, open],
        '.note, .open-string-note, .open-string-label, .string-label, tfoot th': [note, open, openCell, label, footer],
    })[selector];
    let fontReady;
    const fonts = new Promise(resolve => { fontReady = resolve; });
    const frames = [];
    const serializable = node => ({tag: node.tag, attrs: node.attrs, text: node.textContent,
        children: node.children.map(serializable)});
    const context = {
        GUITAR_TUNING: ['e', 'B', 'G', 'D', 'A', 'E'].map(name => ({name})),
        window: {setNoteVisibility: (note, visible) => {
            note.classList.toggle('note-hidden', !visible);
            if (note.openStringLabel) note.openStringLabel.hidden = visible;
        }},
        document: {
            querySelectorAll: selector => diagram.querySelectorAll(selector),
            querySelector: selector => ({'.fretboard-header': header,
                '.fretboard-container': container, '.fretboard-diagram': diagram})[selector],
            getElementById: id => id === 'string-svg-container' ? strings : outlines,
            createElementNS: (_, tag) => new Element(tag),
            createRange: () => ({selectNodeContents(element) { this.element = element; },
                getBoundingClientRect() { return this.element.getBoundingClientRect(); }}),
            fonts: {ready: fonts},
        },
        getComputedStyle: element => ({
            ...(element.activeStyle && !element.classList.contains('inactive')
                ? element.activeStyle : element.style),
            ...(element.classList.contains('note-hidden') ? {visibility: 'hidden'} : {}),
        }),
        drawStringsAsSVG: () => {},
        requestAnimationFrame: callback => frames.push(callback),
        XMLSerializer: class {serializeToString(node) { return JSON.stringify(serializable(node)); }},
    };
    vm.runInNewContext(fs.readFileSync(path.join(__dirname, 'fretboard_export.js'), 'utf8'), context);
    context.window.initializeFretboardExport('Arial');
    return {api: context.window.fretboardExport, header, container, diagram, strings, note, open, outlines, frames,
        fontReady, frame: () => frames.splice(0).forEach(callback => callback())};
}

test('complete vector scene includes open strings, labels, outlines and finite strings in layer order', async () => {
    const f = fixture();
    f.api.prepare();
    f.fontReady();
    await Promise.resolve();
    for (let i = 0; i < 4; i++) f.frame();
    assert.equal(f.header.style.display, 'none');
    assert.equal(f.container.style.fontFamily, '"Arial"');
    const svg = JSON.parse(f.api.result.svg);
    assert.equal(svg.attrs.viewBox, '0 0 1600 260');
    assert.equal(svg.attrs.width, '1600');
    assert.deepEqual(JSON.parse(JSON.stringify(f.api.result.geometry)), {
        left: 45, right: 125, strings: Object.fromEntries(
            ['e', 'B', 'G', 'D', 'A', 'E'].map((name, index) => [name, {y: 35 + index * 35, width: 2.1}])),
    });
    const groups = svg.children.filter(node => node.tag === 'g');
    assert.equal(groups.length, 2);
    assert.equal(groups[0].children[0].attrs.d, 'M 40 35 L 1600 35');
    assert.equal(groups[1].children[0].attrs['data-sequence-group'], '0');
    const ellipses = svg.children.filter(node => node.tag === 'ellipse');
    assert.equal(ellipses.length, 3);
    assert.equal(ellipses[1].attrs.fill, 'rgb(254, 193, 187)');
    assert.ok(svg.children.indexOf(ellipses[0]) < svg.children.indexOf(groups[0]));
    assert.ok(svg.children.indexOf(ellipses[1]) > svg.children.indexOf(groups[1]));
    const texts = svg.children.filter(node => node.tag === 'text');
    assert.deepEqual(texts.map(node => node.text), ['G', 'B', 'e', '24']);
    assert.equal(texts[0].attrs.x, '85'); // Relative to diagram, not the viewport.
    assert.equal(texts.at(-1).attrs.y, '227.5'); // Uses actual text bounds.
});

test('active export includes open notes, preserves custom colors and can return to faded colors', async () => {
    const f = fixture();
    // A custom highlight class can supply purple instead of the default grey.
    f.open.activeStyle.backgroundColor = 'rgb(142, 68, 173)';
    f.fontReady();
    for (const active of [true, false]) {
        f.api.prepare(active);
        await Promise.resolve();
        for (let i = 0; i < 4; i++) f.frame();
        const svg = JSON.parse(f.api.result.svg);
        const notes = svg.children.filter(node => node.tag === 'ellipse').slice(1);
        assert.deepEqual(notes.map(node => node.attrs.fill), active
            ? ['rgb(231, 76, 60)', 'rgb(142, 68, 173)']
            : ['rgb(254, 193, 187)', 'rgb(188, 188, 188)']);
        const labels = svg.children.filter(node => node.tag === 'text').slice(0, 2);
        assert.ok(labels.every(node => node.attrs.fill === (active ? 'rgb(255, 255, 255)' : 'rgb(0, 0, 0)')));
    }
});

test('overview reveals playback notes; snapshots omit hidden markers and outlines', async () => {
    const f = fixture();
    f.note.classList.add('note-hidden');
    f.open.classList.add('note-hidden');
    f.open.openStringLabel = {hidden: false};
    f.note.style.backgroundColor = 'rgb(18, 52, 86)';
    f.api.prepare(false);
    assert.equal(f.note.classList.contains('note-hidden'), false);
    assert.equal(f.open.openStringLabel.hidden, true);
    // A marker hidden after preparation must not leak into the SVG snapshot.
    f.open.classList.add('note-hidden');
    f.outlines.children[0].style.visibility = 'hidden';
    f.fontReady();
    await Promise.resolve();
    for (let i = 0; i < 4; i++) f.frame();
    const svg = JSON.parse(f.api.result.svg);
    assert.equal(svg.children.filter(node => node.tag === 'ellipse').length, 2);
    assert.equal(svg.children.filter(node => node.tag === 'ellipse')[1].attrs.fill, 'rgb(18, 52, 86)');
    assert.equal(svg.children.filter(node => node.tag === 'g')[1].children.length, 0);
    assert.deepEqual(svg.children.filter(node => node.tag === 'text').map(node => node.text),
        ['G', 'e', '24']);
});

test('waits for fonts and stable geometry after asynchronous reflow', async () => {
    const f = fixture();
    f.api.prepare();
    assert.equal(f.frames.length, 0);
    assert.equal(f.api.result, null);
    f.fontReady();
    await Promise.resolve();
    f.frame();
    f.frame();
    f.diagram.rect.width = 1700;
    f.strings.rect.top += 8;
    f.note.rect.left += 20;
    f.frame();
    f.frame();
    f.frame();
    assert.equal(f.api.result, null);
    f.frame();
    const svg = JSON.parse(f.api.result.svg);
    assert.equal(svg.attrs.width, '1700');
    assert.equal(svg.children.find(node => node.tag === 'text').attrs.x, '105');
    assert.equal(f.api.result.geometry.strings.e.y, 43);
    assert.equal(f.api.result.geometry.strings.E.y, 218);
});

test('a new part cancels pending frames from the previous snapshot', async () => {
    const f = fixture();
    f.fontReady();
    f.api.prepare();
    await Promise.resolve();
    f.frame();
    f.api.prepare();
    f.note.textContent = 'D';
    await Promise.resolve();
    for (let i = 0; i < 4; i++) f.frame();
    const svg = JSON.parse(f.api.result.svg);
    assert.equal(svg.children.find(node => node.tag === 'text').text, 'D');
});

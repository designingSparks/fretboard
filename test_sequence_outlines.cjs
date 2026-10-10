// Run with: node --test test_sequence_outlines.cjs
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const {buildOutline, convexHull} = require('./sequence_outlines.js');

function setup() {
    class Element {
        constructor(tag) { this.tag = tag; this.attrs = {}; this.children = []; this.style = {}; }
        setAttribute(name, value) { this.attrs[name] = String(value); }
        appendChild(child) { this.children.push(child); }
        replaceChildren() { this.children = []; }
        getBoundingClientRect() { return {left: 100, top: 50}; }
    }
    const overlay = new Element('svg');
    const diagram = new Element('div');
    const markers = new Map();
    const callbacks = {};
    const frames = new Map();
    let frameId = 0;
    const context = {
        console,
        document: {
            createElementNS: (_, tag) => new Element(tag),
            getElementById: id => id === 'fretboard-table'
                ? {getBoundingClientRect: () => ({left: 100, top: 50, right: 1500, bottom: 450})} : overlay,
            querySelector: selector => selector === '.fretboard-diagram' ? diagram : markers.get(selector),
            fonts: {ready: {then: callback => { callbacks.fonts = callback; }}},
        },
        window: {addEventListener: (event, callback) => { callbacks[event] = callback; }},
        ResizeObserver: class { constructor(callback) { callbacks.observer = callback; } observe() {} },
        requestAnimationFrame: callback => { frames.set(++frameId, callback); return frameId; },
        cancelAnimationFrame: id => frames.delete(id),
    };
    vm.runInNewContext(fs.readFileSync(path.join(__dirname, 'sequence_outlines.js'), 'utf8'), context);
    return {
        overlay, diagram, callbacks, markers, refresh: context.window.refreshSequenceOutlines,
        note(stringName, fret, x, y) {
            const index = ['e', 'B', 'G', 'D', 'A', 'E'].indexOf(stringName);
            const selector = fret === 0
                ? `td.string-label[data-string="${index}"] .open-string-note`
                : `td.fret[data-string="${index}"][data-fret="${fret}"] .note`;
            const classes = new Set();
            markers.set(selector, {classList: {
                contains: name => classes.has(name),
                add: name => classes.add(name), remove: name => classes.delete(name),
            }, getBoundingClientRect: () => ({
                left: 100 + x - 15, top: 50 + y - 15, width: 30, height: 30,
            })});
            return {stringName, fret};
        },
        flush() { for (const [id, callback] of frames) { frames.delete(id); callback(); } },
        draw(groups, distance = 8, rounded = true, radius = 24) {
            context.window.setSequenceOutlines(groups, distance, rounded, radius); this.flush();
        },
    };
}

const note = (x, y) => ({x, y, radius: 15});

test('outlines containing hidden playback notes hide without changing geometry', () => {
    const board = setup();
    const triad = [board.note('e', 3, 100, 40), board.note('B', 3, 100, 75),
        board.note('G', 4, 170, 110)];
    board.draw([triad]);
    const path = board.overlay.children[0].attrs.d;
    const marker = [...board.markers.values()][0];
    marker.classList.add('note-hidden');
    board.refresh(); board.flush();
    assert.equal(board.overlay.children[0].style.visibility, 'hidden');
    assert.equal(board.overlay.children[0].attrs.d, path);
    marker.classList.remove('note-hidden');
    board.refresh(); board.flush();
    assert.notEqual(board.overlay.children[0].style.visibility, 'hidden');
    assert.equal(board.overlay.children[0].attrs.d, path);
});

// Sample the actual SVG path to verify convexity and note clearance, including arcs.
function samplePath(d) {
    const tokens = d.match(/[MLAZ]|[-+]?\d*\.?\d+(?:e[-+]?\d+)?/gi);
    const result = [];
    let current;
    while (tokens.length) {
        const command = tokens.shift();
        if (command === 'Z') break;
        if (command === 'M' || command === 'L') {
            current = {x: +tokens.shift(), y: +tokens.shift()};
            result.push(current);
        } else {
            assert.equal(command, 'A');
            const radius = +tokens.shift();
            assert.equal(+tokens.shift(), radius);
            tokens.shift();
            assert.equal(+tokens.shift(), 0);
            assert.equal(+tokens.shift(), 1);
            const end = {x: +tokens.shift(), y: +tokens.shift()};
            const dx = end.x - current.x, dy = end.y - current.y;
            const length = Math.hypot(dx, dy);
            const height = Math.sqrt(Math.max(0, radius * radius - length * length / 4));
            const center = {x: (current.x + end.x) / 2 - dy / length * height,
                y: (current.y + end.y) / 2 + dx / length * height};
            const start = Math.atan2(current.y - center.y, current.x - center.x);
            let finish = Math.atan2(end.y - center.y, end.x - center.x);
            while (finish <= start) finish += 2 * Math.PI;
            const steps = Math.ceil((finish - start) * 40);
            for (let i = 1; i <= steps; i++) {
                const angle = start + (finish - start) * i / steps;
                result.push({x: center.x + radius * Math.cos(angle), y: center.y + radius * Math.sin(angle)});
            }
            current = end;
        }
    }
    return result.filter((p, i) => !i || Math.hypot(p.x - result[i - 1].x, p.y - result[i - 1].y) > 1e-6);
}
function cross(a, b, c) { return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x); }
function assertEnclosed(polygon, point) {
    polygon.forEach((p, i) => assert.ok(cross(p, polygon[(i + 1) % polygon.length], point) >= -0.01,
        `Point ${JSON.stringify(point)} escaped outline`));
}

test('left and right screenshot groups have three-sided convex outlines with no V', () => {
    for (const points of [
        [note(30, 40), note(100, 75), note(30, 110)],
        [note(300, 40), note(360, 75), note(300, 110)],
    ]) {
        const shape = buildOutline(points, 8, true, 24);
        assert.equal(shape.hull.length, 3);
        assert.equal((shape.d.match(/A /g) || []).length, 3);
        const polygon = samplePath(shape.d);
        polygon.forEach((p, i) => assert.ok(cross(p, polygon[(i + 1) % polygon.length],
            polygon[(i + 2) % polygon.length]) >= -0.01));
        // Includes the closing third link's midpoint, previously omitted by the tree.
        assertEnclosed(polygon, {x: (points[0].x + points[1].x) / 2, y: (points[0].y + points[1].y) / 2});
        assert.equal(buildOutline([...points].reverse(), 8, true, 24).d, shape.d);
    }
});

test('marker clearance survives different fillets, acute triangles, and interior notes', () => {
    const groups = [
        [note(0, 0), note(140, 35), note(140, 70)],
        [note(0, 0), note(65, 0), note(65, 35)],
        [note(0, 0), note(1000, 35), note(0, 70)],
        [note(0, 0), note(100, 0), note(100, 100), note(0, 100), note(50, 50)],
    ];
    for (const points of groups) for (const radius of [0, 4, 12, 24, 1000]) {
        const shape = buildOutline(points, 8, true, radius);
        const polygon = samplePath(shape.d);
        for (const point of points) for (let i = 0; i < 24; i++) {
            const angle = i * Math.PI / 12;
            assertEnclosed(polygon, {x: point.x + 22.95 * Math.cos(angle), y: point.y + 22.95 * Math.sin(angle)});
        }
        assert.ok(!/NaN|Infinity/.test(shape.d));
        assert.ok(shape.fillet <= 23);
    }
});

test('filleting is optional and the requested radius controls circular arcs', () => {
    const points = [note(0, 0), note(80, 35), note(0, 70)];
    const sharp = buildOutline(points, 8, false, 12);
    assert.ok(!sharp.d.includes('A '));
    assert.equal(buildOutline(points, 8, true, 0).d, sharp.d);
    assert.ok(buildOutline(points, 8, true, 6).d.includes('A 6 6'));
    assert.ok(buildOutline(points, 8, true, 12).d.includes('A 12 12'));
});

test('near-collinear triads have bounded miters and retain full note clearance', () => {
    // Adjacent frets narrow progressively: 3/4/5 is almost a straight diagonal.
    // Previously this actual G-major shape produced a 14,127 px wide outline.
    const widths = Array.from({length: 15}, (_, i) => 80 * .97 ** i);
    const center = fret => 40 + widths.slice(0, fret - 1).reduce((a, b) => a + b, 0) + widths[fret - 1] / 2;
    for (const frets of [[3, 4, 5], [5, 4, 3], [9, 7, 5]]) {
        const points = frets.map((fret, index) => note(center(fret), 17.5 + index * 35));
        for (const radius of [0, 4, 12, 24]) {
            const shape = buildOutline(points, 8, radius > 0, radius);
            assert.ok(!/NaN|Infinity/.test(shape.d));
            const xs = points.map(p => p.x);
            // A clipped tip has a 4*padding axial component and at most padding
            // perpendicular to it. Include the 1px stroke on either side.
            const maxExtra = 2 * (Math.hypot(4, 1) * 23 + 1);
            assert.ok(shape.bounds.right - shape.bounds.left <= Math.max(...xs) - Math.min(...xs) + maxExtra);
            assert.ok(shape.bounds.bottom - shape.bounds.top <= 70 + maxExtra);
            const polygon = samplePath(shape.d);
            polygon.forEach((p, i) => assert.ok(cross(p, polygon[(i + 1) % polygon.length],
                polygon[(i + 2) % polygon.length]) >= -0.01));
            for (const point of points) for (let i = 0; i < 32; i++) {
                const angle = i * Math.PI / 16;
                assertEnclosed(polygon, {x: point.x + 22.95 * Math.cos(angle),
                    y: point.y + 22.95 * Math.sin(angle)});
            }
        }
    }
});

test('horizontal and diagonal collinear groups stay narrow, single notes remain circular', () => {
    const horizontal = [note(0, 0), note(450, 0), note(900, 0)];
    const shape = buildOutline(horizontal, 8, true, 24);
    assert.equal(shape.hull.length, 2);
    assert.equal(shape.bounds.bottom - shape.bounds.top, 48);
    assert.equal((shape.d.match(/A /g) || []).length, 2);
    const wider = buildOutline(horizontal, 20, true, 100);
    assert.equal(wider.bounds.bottom - wider.bounds.top, 72);
    assert.equal(convexHull([note(0, 0), note(100, 100), note(200, 200)]).length, 2);
    assert.equal(buildOutline([note(0, 0), note(0, 0)], 8, true, 24).hull.length, 1);
    assert.equal(buildOutline([], 8, true, 24), null);
});

test('rows stay separate, geometry responds to layout, and disabling clears outlines', () => {
    const board = setup();
    const a = board.note('e', 0, 30, 40), b = board.note('B', 1, 100, 75), c = board.note('G', 0, 30, 110);
    board.draw([[a, b, c], [c, b, a], [a, a]]);
    assert.equal(board.overlay.children.length, 3);
    assert.equal(board.overlay.children[0].attrs.d, board.overlay.children[1].attrs.d);
    assert.equal(board.overlay.children[2].attrs['data-note-count'], '1');
    const before = board.overlay.children[0].attrs.d;
    board.note('e', 0, 80, 40);
    board.callbacks.resize(); board.flush();
    assert.notEqual(board.overlay.children[0].attrs.d, before);
    board.callbacks.fonts(); board.callbacks.observer(); board.flush();
    assert.equal(board.overlay.children.length, 3);
    board.draw([[a, b, c]], 8, false);
    assert.ok(!board.overlay.children[0].attrs.d.includes('A '));
    board.draw([]);
    assert.equal(board.overlay.children.length, 0);
    assert.equal(board.diagram.style.padding, '0px');
});

test('a rounded GBe triad on the final fret reserves space for its right edge', () => {
    const board = setup();
    const triad = [board.note('e', 15, 1325, 20), board.note('B', 15, 1325, 55),
        board.note('G', 16, 1390, 90)];
    board.draw([triad]);
    assert.equal(board.overlay.children.length, 1);
    assert.ok(board.overlay.children[0].attrs.d.includes('A '));
    const shape = buildOutline([note(1325, 20), note(1325, 55), note(1390, 90)], 8, true, 24);
    const rightPadding = parseFloat(board.diagram.style.padding.split(' ')[1]);
    assert.ok(shape.bounds.right > 1400); // Table edge in this fixture.
    assert.ok(1400 + rightPadding >= shape.bounds.right + 2);
});

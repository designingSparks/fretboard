/* Loaded only by the export middleware. All measurements use CSS pixels. */
window.initializeFretboardExport = function(fontFamily) {
    const NS = 'http://www.w3.org/2000/svg';
    const header = document.querySelector('.fretboard-header');
    header.style.display = 'none';
    // Use a font installed in both Qt and the browser. The SVG outlines preserve
    // it for website visitors without requiring that font to be installed.
    document.querySelector('.fretboard-container').style.fontFamily = JSON.stringify(fontFamily);

    function snapshot() {
        const diagram = document.querySelector('.fretboard-diagram');
        const origin = diagram.getBoundingClientRect();
        const svg = document.createElementNS(NS, 'svg');
        const width = Math.ceil(origin.width), height = Math.ceil(origin.height);
        const add = (tag, attrs, parent = svg) => {
            const node = document.createElementNS(NS, tag);
            Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
            parent.appendChild(node);
            return node;
        };
        const bounds = element => {
            const r = element.getBoundingClientRect();
            return {x: r.left - origin.left, y: r.top - origin.top,
                    width: r.width, height: r.height};
        };
        svg.setAttribute('width', width);
        svg.setAttribute('height', height);
        svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
        svg.setAttribute('role', 'img');
        add('rect', {x: 0, y: 0, width, height, fill: '#fff'});

        // Cell backgrounds are below the collapsed table borders and inlays.
        const cells = [...diagram.querySelectorAll('td.fret')];
        const cellBounds = cells.map(bounds);
        const geometry = {
            left: Math.min(...cellBounds.map(r => r.x)),
            right: Math.max(...cellBounds.map(r => r.x + r.width)),
            strings: {},
        };
        cells.forEach(cell => add('rect', {...bounds(cell), fill: getComputedStyle(cell).backgroundColor}));
        cells.forEach(cell => {
            const r = bounds(cell), style = getComputedStyle(cell);
            const line = (side, x1, y1, x2, y2) => {
                const thickness = parseFloat(style[`border${side}Width`]);
                if (thickness) add('line', {x1, y1, x2, y2,
                    stroke: style[`border${side}Color`], 'stroke-width': thickness});
            };
            line('Right', r.x + r.width, r.y, r.x + r.width, r.y + r.height);
            if (cell.classList.contains('nut')) line('Left', r.x, r.y, r.x, r.y + r.height);
            if (cell.parentElement === cell.parentElement.parentElement.firstElementChild)
                line('Top', r.x, r.y, r.x + r.width, r.y);
            if (cell.parentElement === cell.parentElement.parentElement.lastElementChild)
                line('Bottom', r.x, r.y + r.height, r.x + r.width, r.y + r.height);
        });
        const circle = element => {
            const r = bounds(element);
            add('ellipse', {cx: r.x + r.width / 2, cy: r.y + r.height / 2,
                rx: r.width / 2, ry: r.height / 2, fill: getComputedStyle(element).backgroundColor});
        };
        diagram.querySelectorAll('.fret-marker-dot').forEach(circle);

        // The live strings extend to a virtual saddle. End static strings at
        // the viewport edge; this also works in Qt SVG, which ignores clipPath.
        for (const id of ['string-svg-container', 'sequence-outline-container']) {
            const overlay = document.getElementById(id), r = bounds(overlay);
            const group = add('g', {transform: `translate(${r.x} ${r.y})`});
            [...overlay.children].forEach((child, index) => {
                const copy = child.cloneNode(true);
                if (id === 'string-svg-container') {
                    const start = child.getPointAtLength(0);
                    copy.setAttribute('d', `M ${start.x} ${start.y} L ${r.width} ${start.y}`);
                    geometry.strings[GUITAR_TUNING[index].name] = {
                        y: r.y + start.y,
                        width: parseFloat(child.getAttribute('stroke-width')) || 0,
                    };
                }
                group.appendChild(copy);
            });
        }
        diagram.querySelectorAll('.note, .open-string-note').forEach(circle);

        // Measure text separately from its cell (notably the padded fret numbers).
        // Python replaces these temporary text nodes with portable glyph paths.
        diagram.querySelectorAll('.note, .open-string-note, .string-label, tfoot th').forEach(element => {
            if (element.classList.contains('string-label') && element.children.length) return;
            const range = document.createRange();
            range.selectNodeContents(element);
            const r = range.getBoundingClientRect(), style = getComputedStyle(element);
            const node = add('text', {
                x: r.left - origin.left + r.width / 2,
                y: r.top - origin.top + r.height / 2,
                fill: style.color, 'font-family': style.fontFamily,
                'font-size': parseFloat(style.fontSize), 'font-weight': style.fontWeight,
                'letter-spacing': style.letterSpacing,
            });
            node.textContent = element.textContent;
        });
        return {svg: new XMLSerializer().serializeToString(svg), geometry};
    }

    let generation = 0;
    window.fretboardExport = {
        result: null,
        prepare() {
            const current = ++generation;
            this.result = null;
            document.fonts.ready.then(() => {
                if (current !== generation) return;
                drawStringsAsSVG();
                let previous = '', stableFrames = 0;
                const settle = () => {
                    if (current !== generation) return;
                    try {
                        const scene = snapshot();
                        const serialized = JSON.stringify(scene);
                        stableFrames = serialized === previous ? stableFrames + 1 : 0;
                        previous = serialized;
                        // Includes the deferred outline pass and any padding reflow.
                        if (stableFrames >= 3) this.result = scene;
                        else requestAnimationFrame(settle);
                    } catch (error) {
                        this.result = {error: String(error)};
                    }
                };
                requestAnimationFrame(settle);
            }).catch(error => { this.result = {error: String(error)}; });
        },
    };
    return true;
};

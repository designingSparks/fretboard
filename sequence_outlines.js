/* Convex enclosing polygons with optional circular fillets. */
(() => {
    const SVG_NS = 'http://www.w3.org/2000/svg';
    const STROKE_WIDTH = 2;
    const EPSILON = 1e-7;
    const MITER_LIMIT = 4;
    const add = (a, b, scale = 1) => ({x: a.x + b.x * scale, y: a.y + b.y * scale});
    const cross = (a, b, c) => (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);

    function convexHull(points) {
        const sorted = [...points].sort((a, b) => a.x - b.x || a.y - b.y)
            .filter((p, i, all) => !i || p.x !== all[i - 1].x || p.y !== all[i - 1].y);
        if (sorted.length < 3) return sorted;
        const half = list => {
            const result = [];
            for (const point of list) {
                while (result.length > 1 && cross(result.at(-2), result.at(-1), point) <= EPSILON) {
                    result.pop();
                }
                result.push(point);
            }
            return result;
        };
        return [...half(sorted).slice(0, -1), ...half([...sorted].reverse()).slice(0, -1)];
    }

    function outwardNormals(polygon) {
        return polygon.map((point, i) => {
            const next = polygon[(i + 1) % polygon.length];
            const length = Math.hypot(next.x - point.x, next.y - point.y);
            return {x: (next.y - point.y) / length, y: (point.x - next.x) / length};
        });
    }

    // Offset supporting lines, clipping very acute miters before they can make
    // a nearly collinear triad thousands of pixels wide. The clip plane stays
    // outside the note clearance circle, unlike simply shortening the vertex.
    function offsetPolygon(polygon, distance) {
        if (distance < EPSILON) return polygon;
        const normals = outwardNormals(polygon);
        return polygon.flatMap((point, i) => {
            const previous = normals[(i + normals.length - 1) % normals.length];
            const next = normals[i];
            const sum = add(previous, next);
            const length = Math.hypot(sum.x, sum.y);
            const bisector = {x: sum.x / length, y: sum.y / length};
            const cosine = length / 2;
            if (cosine >= 1 / MITER_LIMIT) {
                return [add(point, bisector, distance / cosine)];
            }
            const limit = distance * MITER_LIMIT;
            const center = add(point, bisector, limit);
            const tangent = {x: -bisector.y, y: bisector.x};
            const halfWidth = (distance - limit * cosine) / Math.sqrt(1 - cosine * cosine);
            return [add(center, tangent, -halfWidth), add(center, tangent, halfWidth)];
        });
    }

    function buildOutline(points, wrappingDistance, filletCorners, requestedRadius) {
        if (!points.length) return null;
        const hull = convexHull(points);
        const padding = Math.max(...points.map(p => p.radius)) + wrappingDistance;
        // Larger fillets would cut into the required note clearance.
        const fillet = filletCorners ? Math.min(requestedRadius, padding) : 0;
        const commands = [];
        const extrema = [];
        let current;
        const move = point => { commands.push(`M ${point.x} ${point.y}`); current = point; extrema.push(point); };
        const line = point => { commands.push(`L ${point.x} ${point.y}`); current = point; extrema.push(point); };
        const arc = (center, radius, end) => {
            const startAngle = Math.atan2(current.y - center.y, current.x - center.x);
            let endAngle = Math.atan2(end.y - center.y, end.x - center.x);
            while (endAngle <= startAngle + EPSILON) endAngle += 2 * Math.PI;
            for (let angle = Math.ceil(startAngle / (Math.PI / 2)) * Math.PI / 2;
                angle <= endAngle + EPSILON; angle += Math.PI / 2) {
                extrema.push({x: center.x + radius * Math.cos(angle), y: center.y + radius * Math.sin(angle)});
            }
            commands.push(`A ${radius} ${radius} 0 ${endAngle - startAngle > Math.PI + EPSILON ? 1 : 0} 1 ${end.x} ${end.y}`);
            extrema.push(end);
            current = end;
        };
        const roundPolygon = (polygon, radius) => {
            if (radius < EPSILON) {
                move(polygon[0]);
                polygon.slice(1).forEach(line);
                return;
            }
            const normals = outwardNormals(polygon);
            move(add(polygon[0], normals.at(-1), radius));
            polygon.forEach((point, i) => {
                if (i) line(add(point, normals[i - 1], radius));
                arc(point, radius, add(point, normals[i], radius));
            });
        };

        if (hull.length === 1) {
            // An isolated note has no polygon corners to fillet.
            move(add(hull[0], {x: 1, y: 0}, padding));
            arc(hull[0], padding, add(hull[0], {x: -1, y: 0}, padding));
            arc(hull[0], padding, add(hull[0], {x: 1, y: 0}, padding));
        } else if (hull.length === 2) {
            const [a, b] = hull;
            const length = Math.hypot(b.x - a.x, b.y - a.y);
            const direction = {x: (b.x - a.x) / length, y: (b.y - a.y) / length};
            const normal = {x: direction.y, y: -direction.x};
            const inset = padding - fillet;
            if (inset < EPSILON) {
                // Collinear notes form a capsule, regardless of their separation.
                move(add(a, normal, padding));
                line(add(b, normal, padding));
                arc(b, padding, add(b, normal, -padding));
                line(add(a, normal, -padding));
                arc(a, padding, add(a, normal, padding));
            } else {
                roundPolygon([
                    add(add(a, direction, -inset), normal, inset),
                    add(add(b, direction, inset), normal, inset),
                    add(add(b, direction, inset), normal, -inset),
                    add(add(a, direction, -inset), normal, -inset),
                ], fillet);
            }
        } else {
            // Three non-collinear notes produce a triangle. Larger groups use
            // their convex hull; no internal links or inward notches are drawn.
            // Miter-offset first, then circular-offset: true tangent fillets of
            // the requested radius, preserving the same straight-edge clearance.
            roundPolygon(offsetPolygon(hull, padding - fillet), fillet);
        }
        commands.push('Z');
        const bounds = {
            left: Math.min(...extrema.map(p => p.x)) - STROKE_WIDTH / 2,
            top: Math.min(...extrema.map(p => p.y)) - STROKE_WIDTH / 2,
            right: Math.max(...extrema.map(p => p.x)) + STROKE_WIDTH / 2,
            bottom: Math.max(...extrema.map(p => p.y)) + STROKE_WIDTH / 2,
        };
        return {d: commands.join(' '), bounds, hull, fillet};
    }

    // Keep the geometry testable without starting Qt's embedded browser.
    if (typeof module !== 'undefined' && module.exports) module.exports = {buildOutline, convexHull};
    if (typeof document === 'undefined') return;

    let groups = [];
    let wrappingDistance = 8;
    let filletCorners = false;
    let filletRadius = 24;
    let pendingFrame = null;

    function measureGroup(group, origin) {
        const points = new Map();
        for (const note of group) {
            const stringIndex = ['e', 'B', 'G', 'D', 'A', 'E'].indexOf(note.stringName);
            const selector = note.fret === 0
                ? `td.string-label[data-string="${stringIndex}"] .open-string-note`
                : `td.fret[data-string="${stringIndex}"][data-fret="${note.fret}"] .note`;
            const marker = document.querySelector(selector);
            if (!marker) {
                console.warn('Cannot outline group: missing note marker', note);
                return [];
            }
            const bounds = marker.getBoundingClientRect();
            points.set(`${stringIndex}:${note.fret}`, {
                x: bounds.left - origin.left + bounds.width / 2,
                y: bounds.top - origin.top + bounds.height / 2,
                radius: Math.max(bounds.width, bounds.height) / 2,
            });
        }
        return [...points.values()];
    }

    function draw() {
        const overlay = document.getElementById('sequence-outline-container');
        const diagram = document.querySelector('.fretboard-diagram');
        const origin = diagram.getBoundingClientRect();
        const outlines = groups.map(group => {
            const points = measureGroup(group, origin);
            return {points, shape: buildOutline(points, wrappingDistance, filletCorners, filletRadius)};
        });
        overlay.replaceChildren();

        // A small or disabled fillet can leave an acute corner extending beyond
        // the note markers. Reserve its actual space, including open-string notes.
        const table = document.getElementById('fretboard-table').getBoundingClientRect();
        const bounds = outlines.filter(o => o.shape).map(o => o.shape.bounds);
        const space = bounds.length ? [
            Math.max(0, ...bounds.map(b => table.top - origin.top - b.top)) + 2,
            Math.max(0, ...bounds.map(b => b.right - (table.right - origin.left))) + 2,
            Math.max(0, ...bounds.map(b => b.bottom - (table.bottom - origin.top))) + 2,
            Math.max(0, ...bounds.map(b => table.left - origin.left - b.left)) + 2,
        ].map(n => `${Math.ceil(n)}px`).join(' ') : '0px';
        // CSS normalizes shorthand values; compare after assignment to avoid loops.
        const previousPadding = diagram.style.padding;
        diagram.style.padding = space;
        if (diagram.style.padding !== previousPadding) {
            scheduleDraw();
            if (typeof window.drawStringsAsSVG === 'function') window.drawStringsAsSVG();
            return;
        }
        outlines.forEach(({points, shape}, index) => {
            if (!shape) return;
            const path = document.createElementNS(SVG_NS, 'path');
            for (const [key, value] of Object.entries({
                d: shape.d, fill: 'none', stroke: '#527a8a', 'stroke-width': STROKE_WIDTH,
                'stroke-linejoin': 'round', 'data-sequence-group': index,
                'data-note-count': points.length, 'data-hull-count': shape.hull.length,
                'data-fillet-radius': shape.fillet,
            })) path.setAttribute(key, value);
            overlay.appendChild(path);
        });
    }

    function scheduleDraw() {
        if (pendingFrame !== null) cancelAnimationFrame(pendingFrame);
        pendingFrame = requestAnimationFrame(() => {
            pendingFrame = null;
            draw();
        });
    }

    window.setSequenceOutlines = function(nextGroups = [], distance = 8, rounded = false, radius = 24) {
        groups = nextGroups;
        wrappingDistance = distance;
        filletCorners = rounded;
        filletRadius = radius;
        document.getElementById('sequence-outline-container').replaceChildren();
        scheduleDraw();
    };

    new ResizeObserver(scheduleDraw).observe(document.querySelector('.fretboard-diagram'));
    window.addEventListener('resize', scheduleDraw);
    document.fonts.ready.then(scheduleDraw);
})();

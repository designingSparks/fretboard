import { cMajorPentatonic, gMajorPentatonic, aMinorPentatonic, cMajor } from './scales.js';

// --- 1. Configuration ---
const SHOW_DOTS = true; // Set to false to hide fret markers
const NUM_FRETS = 24;
const GUITAR_TUNING = [
    { name: 'e', openNote: 'E' }, { name: 'B', openNote: 'B' },
    { name: 'G', openNote: 'G' }, { name: 'D', openNote: 'D' },
    { name: 'A', openNote: 'A' }, { name: 'E', openNote: 'E' },
];

// Hardcoded notes for each string and fret for a standard tuning guitar.
// This replaces the dynamic findNote() function.
// Each inner array represents a string from high 'e' to low 'E'.
const FRETBOARD_NOTES = [
    // 0: High 'e' string
    ['E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E'],
    // 1: 'B' string
    ['B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],
    // 2: 'G' string
    ['G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G'],
    // 3: 'D' string
    ['D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D'],
    // 4: 'A' string
    ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A'],
    // 5: Low 'E' string
    ['E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E']
];

// Configuration for SVG strings, previously handled in CSS
const STRING_CONFIG = [
    { width: 2.1, color: '#a9a9a9' }, // High e
    { width: 2.4, color: '#a9a9a9' }, // B
    { width: 2.7, color: '#a9a9a9' }, // G
    { width: 3.0, color: '#a9a9a9' }, // D
    { width: 3.3, color: '#a9a9a9' }, // A
    { width: 3.6, color: '#a9a9a9' }  // Low E
];

// A virtual distance in pixels from the nut to the saddle.
// This is used to calculate the shape of the bent string. A larger number creates a more subtle angle.
const VIRTUAL_SCALE_LENGTH_PX = 5000;

// Factor determining when the secondary string starts moving during a double bend.
// A value of 0.5 means it starts when the primary bend is halfway; 0.25 means it starts at 25%.
// This creates a smoother, more realistic overlap.
const DOUBLE_BEND_OVERLAP_FACTOR = 0.3;

// This will be populated by drawStringsAsSVG with the coordinates for each string.
let STRING_GEOMETRY = [];

// --- New Data Structure for Positions ---
const pentatonicPositions = [
    { position: 1, frets: { min: 2, max: 5 } },
    { position: 2, frets: { min: 5, max: 8 } },
    { position: 3, frets: { min: 7, max: 10 } },
    { position: 4, frets: { min: 9, max: 12 } },
    { position: 5, frets: { min: 0, max: 3 } }
];

// A color map for our notes for easy access.
const HIGHLIGHT_COLORS = {
    root: '#e74c3c',   // Red
    third: '#ff8c00',  // Orange
    fifth: '#ffd700',  // Yellow
    default: '#444'    // Black / Dark Grey
};


// --- 2. Fretboard Generation ---
const fretboardBody = document.getElementById('fretboard-body');
const fretboardFooter = document.getElementById('fretboard-footer');
const FRET_WIDTH_BASE = 80; // The width of the first fret in pixels.
const FRET_WIDTH_MULTIPLIER = 0.97; // Each fret will be 93% of the width of the one before it.

/**
 * Calculates the width of each fret, making them progressively smaller.
 * @returns {number[]} An array of fret widths in pixels.
 */
function calculateFretWidths() {
    const widths = [];
    let currentWidth = FRET_WIDTH_BASE;
    for (let i = 0; i < NUM_FRETS; i++) {
        widths.push(currentWidth);
        currentWidth *= FRET_WIDTH_MULTIPLIER;
    }
    return widths;
}

/**
 * Draws the entire fretboard structure, including strings and fret numbers,
 * with realistic, graduated fret widths.
 */
function drawFretboard() {
    // Clear any existing content
    fretboardBody.innerHTML = '';
    fretboardFooter.innerHTML = '';

    const fretWidths = calculateFretWidths();

    // Create the fretboard body (the strings and frets)
    GUITAR_TUNING.forEach((stringInfo, index) => {
        const row = document.createElement('tr');
        const labelCell = document.createElement('td');
        labelCell.classList.add('string-label');
        labelCell.dataset.string = index;
        labelCell.textContent = stringInfo.name; // Set the string name here
        row.appendChild(labelCell);

        for (let i = 1; i <= NUM_FRETS; i++) {
            const fretCell = document.createElement('td');
            fretCell.classList.add('fret');
            if (i === 1) fretCell.classList.add('nut');
            fretCell.style.minWidth = `${fretWidths[i - 1]}px`; // Set individual fret width
            fretCell.dataset.string = index;
            fretCell.dataset.fret = i;
            row.appendChild(fretCell);
        }
        fretboardBody.appendChild(row);
    });

    // Create the fretboard footer (the fret numbers)
    const footerRow = document.createElement('tr');
    const cornerCell = document.createElement('th');
    cornerCell.textContent = '0';
    footerRow.appendChild(cornerCell);

    for (let i = 1; i <= NUM_FRETS; i++) {
        const header = document.createElement('th');
        header.textContent = i;
        header.style.minWidth = `${fretWidths[i - 1]}px`; // Match the fret width
        footerRow.appendChild(header);
    }
    fretboardFooter.appendChild(footerRow);
}

/**
 * Draws the fret marker dots (inlays) on the fretboard.
 */
function drawFretMarkers() {
    const singleDotFrets = [3, 5, 7, 9, 15, 17, 19, 21];
    const doubleDotFrets = [12, 24];

    for (let fret = 1; fret <= NUM_FRETS; fret++) {
        const fretInPattern = ((fret - 1) % 12) + 1;

        // --- Single Dots ---
        if (singleDotFrets.includes(fretInPattern)) {
            // Place the dot on the line between the 3rd (G) and 4th (D) strings.
            // We target the 4th string's cell (index 3) and position the dot at the top.
            const targetCell = document.querySelector(`.fret[data-string="3"][data-fret="${fret}"]`);
            if (targetCell) {
                const dot = document.createElement('div');
                dot.className = 'fret-marker-dot';
                dot.style.top = '0'; // Position at the top of the cell
                dot.style.transform = 'translate(-50%, -50%)';
                targetCell.appendChild(dot);
            }
        }

        // --- Double Dots ---
        if (doubleDotFrets.includes(fretInPattern)) {
            // Place first dot between the 1st (e) and 2nd (B) strings.
            // We target the 2nd string's cell (index 1) and position the dot at the top.
            const topCell = document.querySelector(`.fret[data-string="1"][data-fret="${fret}"]`);
            if (topCell) {
                const dot1 = document.createElement('div');
                dot1.className = 'fret-marker-dot';
                dot1.style.top = '0'; // Position at the top of the cell
                dot1.style.transform = 'translate(-50%, -50%)';
                topCell.appendChild(dot1);
            }
            // Place second dot between the 5th (A) and 6th (E) strings.
            // We target the 6th string's cell (index 5) and position the dot at the top.
            const bottomCell = document.querySelector(`.fret[data-string="5"][data-fret="${fret}"]`);
            if (bottomCell) {
                const dot2 = document.createElement('div');
                dot2.className = 'fret-marker-dot';
                dot2.style.top = '0'; // Position at the top of the cell
                dot2.style.transform = 'translate(-50%, -50%)';
                bottomCell.appendChild(dot2);
            }
        }
    }
}

function drawScale(scale) {
    // Clear only the notes, not the entire fretboard structure
    document.querySelectorAll('.note, .open-string-note').forEach(n => n.remove());
    
    // Draw the notes, iterating from the low E string up to the high e string.
    // This ensures that higher-pitched strings (which are higher on the screen)
    // are rendered on top of lower-pitched ones, which is crucial for the bend animation.
    for (let stringIndex = GUITAR_TUNING.length - 1; stringIndex >= 0; stringIndex--) {
        const stringInfo = GUITAR_TUNING[stringIndex];
        // Handle open strings
        const openNoteInfo = scale.notes[stringInfo.openNote];
        const labelCell = document.querySelector(`td.string-label[data-string="${stringIndex}"]`);
        if (openNoteInfo) {
            // Clear the plain text string name before adding the styled note div
            labelCell.textContent = '';
            const noteDiv = document.createElement('div');
            // Add the note's identity AND the default faded class
            noteDiv.classList.add('open-string-note', openNoteInfo.degree, 'inactive');
            noteDiv.textContent = stringInfo.name;
            noteDiv.dataset.fret = 0;
            labelCell.appendChild(noteDiv);
        } else {
             // The string name is now set during fretboard creation
        }

        // Handle fretted notes
        for (let fret = 1; fret <= NUM_FRETS; fret++) {
            const noteName = FRETBOARD_NOTES[stringIndex][fret];
            const scaleNoteInfo = scale.notes[noteName];
            if (scaleNoteInfo) {
                const cell = document.querySelector(`td.fret[data-string="${stringIndex}"][data-fret="${fret}"]`);
                const noteDiv = document.createElement('div');
                 // Add the note's identity AND the default faded class
                noteDiv.classList.add('note', scaleNoteInfo.degree, 'inactive');
                noteDiv.textContent = noteName;
                noteDiv.dataset.fret = fret;
                cell.appendChild(noteDiv);
            }
        }
    }
}

/**
 * Draws a specific scale pattern received from an external source (like Python).
 * This function only draws the notes specified in the pattern.
 * @param {Array<Object>} pattern - An array of note objects, e.g., [{stringName: 'E', fret: 3, duration: 500}, ...]
 */
function drawScalePattern(pattern) {
    // Clear any existing notes from the fretboard
    document.querySelectorAll('.note, .open-string-note').forEach(n => n.remove());

    // Create a mapping from string name to its index for quick lookups.
    const stringNameToIndex = GUITAR_TUNING.reduce((acc, stringInfo, index) => {
        acc[stringInfo.name] = index;
        return acc;
    }, {});

    pattern.forEach(noteInfo => {
        const stringIndex = stringNameToIndex[noteInfo.stringName];
        const fret = noteInfo.fret;

        if (stringIndex === undefined) {
            console.warn(`Unknown string name in pattern: ${noteInfo.stringName}`);
            return;
        }

        if (fret === 0) {
            // Handle open string notes (fret 0)
            const labelCell = document.querySelector(`td.string-label[data-string="${stringIndex}"]`);
            if (labelCell) {
                const stringName = GUITAR_TUNING[stringIndex].name;
                // Clear the plain text string name before adding the styled note div
                labelCell.textContent = '';
                const noteDiv = document.createElement('div');
                noteDiv.classList.add('open-string-note', 'inactive');
                noteDiv.textContent = stringName;
                noteDiv.dataset.fret = 0;
                noteDiv.dataset.duration = noteInfo.duration;
                labelCell.appendChild(noteDiv);
            }
        } else {
            // Handle fretted notes (fret > 0)
            const cell = document.querySelector(`td.fret[data-string="${stringIndex}"][data-fret="${fret}"]`);
            if (cell) {
                const noteName = FRETBOARD_NOTES[stringIndex][fret];
                const noteDiv = document.createElement('div');
                noteDiv.classList.add('note', 'inactive'); // Add default and inactive classes
                noteDiv.textContent = noteName;
                noteDiv.dataset.fret = fret;
                noteDiv.dataset.duration = noteInfo.duration; // Store duration for future use
                cell.appendChild(noteDiv);
            }
        }
    });
}


/**
 * Highlights a specific scale position by fading all notes,
 * then re-coloring only the notes within the specified position.
 * @param {Scale} scale - The scale object containing the position definitions.
 * @param {string} positionName - The name of the position to highlight (e.g., 'pos5').
 */
// In main.js

function highlightPosition(scale, positionName) {
    const position = scale.positions[positionName];
    if (!position) {
        console.error(`Position "${positionName}" not found on scale "${scale.name}".`);
        return;
    }

    const allNoteDivs = document.querySelectorAll('.note, .open-string-note');

    allNoteDivs.forEach(noteDiv => {
        // First, ensure every note is faded. This resets the board state.
        noteDiv.classList.add('inactive');

        // Now, check if this note is in the position to be displayed.
        const noteFret = parseInt(noteDiv.dataset.fret);
        const noteStringIndex = parseInt(noteDiv.parentElement.dataset.string);
        const noteStringName = GUITAR_TUNING[noteStringIndex].name;

        const fretsToHighlight = position.frets;
        const stringsToHighlight = position.strings;

        let isInPosition = false;
        if (fretsToHighlight.includes(noteFret)) {
            if (stringsToHighlight) {
                if (stringsToHighlight.includes(noteStringName)) {
                    isInPosition = true;
                }
            } else {
                isInPosition = true;
            }
        }

        // If it's in the position, simply remove the faded class.
        // The color from the CSS (.root, .third, etc.) will now appear.
        if (isInPosition) {
            noteDiv.classList.remove('inactive');
        }
    });
}

/** TO DELETE
 * Highlights multiple scale positions by fading all notes,
 * then re-coloring only the notes within the specified positions.
 * @param {Scale} scale - The scale object containing the position definitions.
 * @param {string[]} positionNames - An array of position names to highlight (e.g., ['pos5', 'pos_custom1']).
 */
function highlightPositions(scale, positionNames) {
    // Get all the valid position objects from the scale based on the names provided.
    const positions = positionNames
        .map(name => scale.positions[name])
        .filter(p => p); // Filter out any undefined positions

    if (positions.length === 0) {
        console.warn("No valid positions to highlight.");
        return;
    }

    const allNoteDivs = document.querySelectorAll('.note, .open-string-note');

    allNoteDivs.forEach(noteDiv => {
        // First, ensure every note is faded. This resets the board state.
        noteDiv.classList.add('inactive');

        const noteFret = parseInt(noteDiv.dataset.fret);
        const noteStringIndex = parseInt(noteDiv.parentElement.dataset.string);
        const noteStringName = GUITAR_TUNING[noteStringIndex].name;

        // Check if the note exists in ANY of the specified positions.
        const isInAnyPosition = positions.some(position => {
            const fretsMatch = position.frets.includes(noteFret);
            // If position.strings is not defined, we only need to check the fret.
            const stringsMatch = !position.strings || position.strings.includes(noteStringName);
            return fretsMatch && stringsMatch;
        });

        if (isInAnyPosition) {
            noteDiv.classList.remove('inactive');
        }
    });
}

/**
 * Renders guitar strings as SVG <line> elements over the fretboard table.
 * This allows for easier animation with libraries like GSAP.
 */
function drawStringsAsSVG() {
    const svgContainer = document.getElementById('string-svg-container');
    const fretboardDiagram = document.querySelector('.fretboard-diagram');
    if (!svgContainer || !fretboardDiagram) return;

    // Clear any existing strings
    svgContainer.innerHTML = '';

    // Get the bounding box of the entire fretboard diagram to calculate relative positions
    const diagramRect = fretboardDiagram.getBoundingClientRect();

    // Determine the horizontal start and end points for the strings
    const firstFretCell = document.querySelector('.fret[data-fret="1"]');
    const lastFretCell = document.querySelector(`.fret[data-fret="${NUM_FRETS}"]`);
    const x1 = firstFretCell.getBoundingClientRect().left - diagramRect.left;
    const x2 = lastFretCell.getBoundingClientRect().right - diagramRect.left;

    // The saddle is far to the right. We'll use our virtual scale length for this.
    const saddleX = x1 + VIRTUAL_SCALE_LENGTH_PX;

    // Clear any previous geometry data
    STRING_GEOMETRY = [];

    GUITAR_TUNING.forEach((stringInfo, index) => {
        const stringRow = document.querySelector(`td.string-label[data-string="${index}"]`).parentElement;
        const rowRect = stringRow.getBoundingClientRect();

        // Calculate the vertical center of the row relative to the diagram container
        const y = Math.round(rowRect.top - diagramRect.top + (rowRect.height / 2));

        // Store the calculated geometry for later use in animations
        STRING_GEOMETRY[index] = {
            nut: { x: x1, y: y },
            saddle: { x: saddleX, y: y }
        };

        // Use a <path> instead of a <line> to allow for bending
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        // The path starts at the nut (M x1 y), goes to the saddle (L saddleX y)
        path.setAttribute('d', `M ${STRING_GEOMETRY[index].nut.x} ${STRING_GEOMETRY[index].nut.y} L ${STRING_GEOMETRY[index].saddle.x} ${STRING_GEOMETRY[index].saddle.y}`);
        path.setAttribute('stroke', STRING_CONFIG[index].color);
        path.setAttribute('stroke-width', STRING_CONFIG[index].width);
        path.setAttribute('fill', 'none'); // Paths can be filled, we don't want that
        path.id = `string-${index}`; // Add an ID for easy selection

        svgContainer.appendChild(path);
    });
}

// --- 5. Animation ---

/**
 * Performs a string bend animation on a specific note using GSAP.
 * The note moves down by one string spacing, holds, and returns.
 * @param {number} stringIndex - The index of the string (0-5).
 * @param {number} fret - The fret number of the note to bend.
 */
function animateNoteBendHalfTone(stringIndex, fret) {
    // Bending is only possible towards the low E string (downwards on screen).
    // It's physically impossible to bend the lowest string (index 5) itself.
    if (stringIndex >= 5) {
        console.error(`Cannot bend the low E string (index ${stringIndex}). Bending is only possible on strings 0-4.`);
        return; // Exit the function, ignoring the animation.
    }

    // 1. Find the target note element
    const fretCellSelector = `td.fret[data-string="${stringIndex}"][data-fret="${fret}"]`;
    const fretCell = document.querySelector(fretCellSelector);
    if (!fretCell) {
        console.error(`Fret cell not found at string ${stringIndex}, fret ${fret}.`);
        return;
    }
    const noteToBend = fretCell.querySelector('.note');

    if (!noteToBend) {
        console.error(`Note not found at string ${stringIndex}, fret ${fret} to animate.`);
        return;
    }

    // 2. Find the string path to animate
    const stringPath = document.getElementById(`string-${stringIndex}`);
    if (!stringPath) {
        console.error(`String path not found for string index ${stringIndex}.`);
        return;
    }

    // 3. Calculate animation parameters
    const stringRow = document.querySelector('#fretboard-body tr');
    if (!stringRow) return;
    const bendDistance = stringRow.offsetHeight;

    const diagramRect = document.querySelector('.fretboard-diagram').getBoundingClientRect();
    const fretRect = fretCell.getBoundingClientRect();
    const stringRect = stringRow.getBoundingClientRect();

    // Get geometry from our pre-calculated data structure. This is more robust.
    const stringGeom = STRING_GEOMETRY[stringIndex];
    if (!stringGeom) {
        console.error(`String geometry not found for string index ${stringIndex}.`);
        return;
    }
    const { nut: { x: nutX, y: nutY }, saddle: { x: saddleX } } = stringGeom;

    // The point on the string we are "pushing"
    const bendPointX = fretRect.left - diagramRect.left + (fretRect.width / 2);

    // 4. Create a proxy object to animate. GSAP will tween the 'y' value of this object.
    let bendProxy = { y: nutY };

    // 5. Create the GSAP timeline
    const tl = gsap.timeline({
        onStart: () => {
            // Temporarily increase z-index to ensure the bending note is on top
            gsap.set(noteToBend, { zIndex: 3 });
        },
        onUpdate: () => {
            // On every frame of the animation, update the SVG path's 'd' attribute
            // This creates the "V" shape of the bent string.
            const newPath = `M ${nutX} ${nutY} L ${bendPointX} ${bendProxy.y} L ${saddleX} ${nutY}`;
            gsap.set(stringPath, { attr: { d: newPath } });
        },
        // After the animation completes, reset the path to a simple straight line.
        // This prevents issues on subsequent animations.
        onComplete: () => {
            const originalPath = `M ${nutX} ${nutY} L ${saddleX} ${nutY}`; // Use the stored nut/saddle X
            gsap.set(stringPath, { attr: { d: originalPath } });
            // Reset z-index to its original value
            gsap.set(noteToBend, { zIndex: 2 });
        }
    });

    // Animate the note and the proxy object separately on the same timeline.
    // The "<" at the start of the second .to() call makes it start at the same time as the previous one.
    // We get the note's initial Y position to ensure the animation is perfectly aligned with the string path.
    const startY = gsap.getProperty(noteToBend, "y");
    const endY = startY + bendDistance;

    tl.to(noteToBend, { y: endY, duration: 0.25, ease: "power1.out" }) // Bend note
      .to(bendProxy, { y: `+=${bendDistance}`, duration: 0.25, ease: "power1.out" }, "<") // Bend string path
      .to({}, { duration: 0.5 }) // Hold (empty tween for a delay)
      .to(noteToBend, { y: startY, duration: 0.25, ease: "power1.in" }) // Release note
      .to(bendProxy, { y: nutY, duration: 0.25, ease: "power1.in" }, "<"); // Release string path
}

/**
 * Performs a whole-tone (double) string bend animation.
 * The primary string bends by two string spacings. When it reaches the adjacent
 * string, that secondary string also starts bending to the final target position.
 * @param {number} stringIndex - The index of the string to bend (0-3).
 * @param {number} fret - The fret number of the note to bend.
 */
function animateNoteBendWholeTone(stringIndex, fret) {
    // A double bend is only physically possible on strings 0-3.
    if (stringIndex > 3) {
        console.error(`Cannot perform a double bend on string index ${stringIndex}. Only possible on strings 0-3.`);
        return;
    }

    // 1. Identify all elements involved in the animation
    const primaryFretCell = document.querySelector(`td.fret[data-string="${stringIndex}"][data-fret="${fret}"]`);
    const secondaryFretCell = document.querySelector(`td.fret[data-string="${stringIndex + 1}"][data-fret="${fret}"]`);
    const targetFretCell = document.querySelector(`td.fret[data-string="${stringIndex + 2}"][data-fret="${fret}"]`);

    const primaryNote = primaryFretCell?.querySelector('.note');
    const primaryStringPath = document.getElementById(`string-${stringIndex}`);

    // The secondary note and string (the one being pushed)
    const secondaryNote = secondaryFretCell?.querySelector('.note');
    const secondaryStringPath = document.getElementById(`string-${stringIndex + 1}`);

    // The note at the final destination, which will be hidden
    const targetNote = targetFretCell?.querySelector('.note');

    if (!primaryNote || !primaryStringPath || !secondaryStringPath) {
        console.error(`Required elements for double bend not found at string ${stringIndex}, fret ${fret}.`);
        return;
    }

    // 2. Calculate animation parameters
    const stringRow = document.querySelector('#fretboard-body tr');
    if (!stringRow) return;
    const bendDistance = stringRow.offsetHeight;
    const totalBendDistance = bendDistance * 2;

    const diagramRect = document.querySelector('.fretboard-diagram').getBoundingClientRect();
    const primaryFretRect = primaryFretCell.getBoundingClientRect();

    // 3. Get geometry and create proxy objects for both strings
    const primaryGeom = STRING_GEOMETRY[stringIndex];
    const secondaryGeom = STRING_GEOMETRY[stringIndex + 1];
    const { nut: { x: pNutX, y: pNutY }, saddle: { x: pSaddleX } } = primaryGeom;
    const { nut: { x: sNutX, y: sNutY }, saddle: { x: sSaddleX } } = secondaryGeom;

    const bendPointX = primaryFretRect.left - diagramRect.left + (primaryFretRect.width / 2);

    let primaryBendProxy = { y: pNutY };
    let secondaryBendProxy = { y: sNutY };

    // 4. Create the GSAP timeline
    const tl = gsap.timeline({
        onStart: () => {
            gsap.set([primaryNote, secondaryNote], { zIndex: 3 }); // Bring both moving notes to the top
        },
        onUpdate: () => {
            // Update both string paths on every frame
            const pPath = `M ${pNutX} ${pNutY} L ${bendPointX} ${primaryBendProxy.y} L ${pSaddleX} ${pNutY}`;
            const sPath = `M ${sNutX} ${sNutY} L ${bendPointX} ${secondaryBendProxy.y} L ${sSaddleX} ${sNutY}`;
            gsap.set(primaryStringPath, { attr: { d: pPath } });
            gsap.set(secondaryStringPath, { attr: { d: sPath } });
        },
        onComplete: () => {
            // Reset everything to its original state
            const pOriginalPath = `M ${pNutX} ${pNutY} L ${pSaddleX} ${pNutY}`;
            const sOriginalPath = `M ${sNutX} ${sNutY} L ${sSaddleX} ${sNutY}`;
            gsap.set(primaryStringPath, { attr: { d: pOriginalPath } });
            gsap.set(secondaryStringPath, { attr: { d: sOriginalPath } });
            gsap.set([primaryNote, secondaryNote], { zIndex: 2 });
        }
    });

    // 5. Define animation sequence
    const primaryStartY = gsap.getProperty(primaryNote, "y");
    const secondaryStartY = secondaryNote ? gsap.getProperty(secondaryNote, "y") : 0;

    const bendDuration = 0.25;
    const holdDuration = 0.5;

    // --- BEND ---
    // Primary note/string bends for the full duration
    tl.to(primaryNote, { y: primaryStartY + totalBendDistance, duration: bendDuration, ease: "power1.out" });
    tl.to(primaryBendProxy, { y: pNutY + totalBendDistance, duration: bendDuration, ease: "power1.out" }, "<");

    // To create a smoother, more realistic bend, the secondary string starts moving
    // before the primary string has traveled the full first string-spacing.
    // We'll start the secondary animation based on the overlap factor.
    const secondaryAnimationStartTime = bendDuration * DOUBLE_BEND_OVERLAP_FACTOR;
    // The duration is adjusted so it still finishes at the same time as the primary bend.
    const secondaryAnimationDuration = bendDuration - secondaryAnimationStartTime;
    if (secondaryNote) {
        tl.to(secondaryNote, { y: secondaryStartY + bendDistance, duration: secondaryAnimationDuration, ease: "power1.out" }, secondaryAnimationStartTime);
    }
    tl.to(secondaryBendProxy, { y: sNutY + bendDistance, duration: secondaryAnimationDuration, ease: "power1.out" }, secondaryAnimationStartTime);

    // --- HOLD ---
    tl.to({}, { duration: holdDuration });

    // --- RELEASE ---
    // The release is the reverse of the bend
    tl.to(primaryNote, { y: primaryStartY, duration: bendDuration, ease: "power1.in" });
    tl.to(primaryBendProxy, { y: pNutY, duration: bendDuration, ease: "power1.in" }, "<");

    if (secondaryNote) {
        tl.to(secondaryNote, { y: secondaryStartY, duration: secondaryAnimationDuration, ease: "power1.in" }, "<" + secondaryAnimationStartTime);
    }
    tl.to(secondaryBendProxy, { y: sNutY, duration: secondaryAnimationDuration, ease: "power1.in" }, "<" + secondaryAnimationStartTime);
}

// --- Execution ---
drawFretboard(); // 1. Draw the board structure first
if (SHOW_DOTS) {
    drawFretMarkers(); // 2. Add the fret marker dots
}
// drawScale(scaleToDraw); // Then draw the notes on top
drawStringsAsSVG();

// --- New Wrapper Function for Python Calls ---
/**
 * Receives a bend animation request from Python and dispatches to the appropriate JS function.
 * This function is exposed globally for PySide6's runJavaScript to call.
 * @param {number} stringIndex - The 0-based index of the string to bend.
 * @param {number} fret - The 1-based fret number.
 * @param {number} halftones - 1 for a half-tone bend, 2 for a whole-tone bend.
 */
window.handlePythonBendRequest = function(stringIndex, fret, halftones) {
    console.log(`Received bend request from Python: string=${stringIndex}, fret=${fret}, halftones=${halftones}`);
    if (halftones === 1) {
        animateNoteBendHalfTone(stringIndex, fret);
    } else if (halftones === 2) {
        animateNoteBendWholeTone(stringIndex, fret);
    } else {
        console.warn(`Unknown bend type requested from Python: ${halftones} halftones.`);
    }
};

/**
 * Receives a scale or lick pattern from Python, parses it, and draws it on the fretboard.
 * e.g. Cmaj. It prints all notes of the pattern in the inactive state initially.
 * @param {string} jsonData - A JSON string representing the scale pattern.
 */
window.loadScalePattern = function(jsonData) {
    console.log("Received scale pattern from Python.");
    try {
        const pattern = JSON.parse(jsonData);
        drawScalePattern(pattern);
    } catch (e) {
        console.error("Failed to parse scale pattern from Python:", e);
    }
};


/* Similar to highlightNote() but can highlight multiple notes
*/
window.highlightNotes = function(jsonData) {
    console.log("Received highlight request from Python.");
    
    // First, reset all notes on the fretboard to their inactive (faded) state.
    document.querySelectorAll('.note, .open-string-note').forEach(note => {
        note.classList.add('inactive');
    });
    
    //Cycle through jsonData and call highlight note
    try {
        const notesToHighlight = JSON.parse(jsonData);
        const stringNameToIndex = GUITAR_TUNING.reduce((acc, stringInfo, index) => {
            acc[stringInfo.name] = index;
            return acc;
        }, {});

        notesToHighlight.forEach(noteInfo => {
            const stringIndex = stringNameToIndex[noteInfo.stringName];
            const fret = noteInfo.fret;

            if (stringIndex !== undefined) {
                let noteSelector;
                if (fret === 0) {
                    // Selector for an open string note
                    noteSelector = `td.string-label[data-string="${stringIndex}"] .open-string-note`;
                } else {
                    // Selector for a fretted note
                    noteSelector = `td.fret[data-string="${stringIndex}"][data-fret="${fret}"] .note`;
                }
                const noteElement = document.querySelector(noteSelector);
                if (noteElement) {
                    noteElement.classList.remove('inactive');
                }
            }
        });
    } catch (e) {
        console.error("Failed to parse notes to highlight from Python:", e);
    }
};

/**
 * Called from python when a new note is being played.
 * Highlights a single note on the fretboard when called from Python during playback
 * @param {string} stringName - The name of the string (e.g., 'E', 'A', 'e').
 * @param {number} fret - The fret number of the note to highlight.
 */
window.highlightNote = function(stringName, fret) {
    // First, reset all notes on the fretboard to their inactive (faded) state.
    document.querySelectorAll('.note, .open-string-note').forEach(note => {
        note.classList.add('inactive');
    });

    // Create a mapping from string name to its index for quick lookups.
    // This could be a global constant if used frequently.
    const stringNameToIndex = GUITAR_TUNING.reduce((acc, stringInfo, index) => {
        acc[stringInfo.name] = index;
        return acc;
    }, {});

    const stringIndex = stringNameToIndex[stringName];

    if (stringIndex === undefined) {
        console.warn(`highlightNote: Unknown string name '${stringName}'`);
        return;
    }

    // Construct a selector to find the note div within the correct table cell
    const noteSelector = `td.fret[data-string="${stringIndex}"][data-fret="${fret}"] .note`;
    const noteElement = document.querySelector(noteSelector);

    if (noteElement) {
        // Now, remove the inactive class from only the current note to highlight it.
        noteElement.classList.remove('inactive');
    }
};

/**
 * Called from Python when playback is stopped. 
 */
window.clearNoteHighlights = function() {
    document.querySelectorAll('.note, .open-string-note').forEach(note => {
        note.classList.add('inactive');
    });
}



// --- Animation Trigger ---
document.getElementById('bend-note-button').addEventListener('click', () => {
    // Animate the 'A' note on the 10th fret of the 'B' string (string index 1)
    // animateNoteBendSingle(1, 10);
    // animateNoteBendSingle(2, 9);
    // Example of a double bend: Bending the G string at the 9th fret (E note) up a whole tone to F#.
    animateNoteBendWholeTone(2,9);
});

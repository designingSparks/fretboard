import { cMajorPentatonic, gMajorPentatonic, aMinorPentatonic, cMajor } from './scales.js';

// --- 1. Configuration ---
const NUM_FRETS = 15;
const GUITAR_TUNING = [
    { name: 'e', openNote: 'E' }, { name: 'B', openNote: 'B' },
    { name: 'G', openNote: 'G' }, { name: 'D', openNote: 'D' },
    { name: 'A', openNote: 'A' }, { name: 'E', openNote: 'E' },
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
const allNotes = ["E", "F", "F#", "G", "G#", "A", "A#", "B", "C", "C#", "D", "D#"];
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
    const singleDotFrets = [3, 5, 7, 9];
    const doubleDotFrets = [12];

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
            // Place first dot between B and G strings
            const topCell = document.querySelector(`.fret[data-string="1"][data-fret="${fret}"]`);
            if (topCell) {
                const dot1 = document.createElement('div');
                dot1.className = 'fret-marker-dot';
                dot1.style.top = '50%';
                dot1.style.transform = 'translate(-50%, -50%)';
                topCell.appendChild(dot1);
            }
            // Place second dot between D and A strings
            const bottomCell = document.querySelector(`.fret[data-string="3"][data-fret="${fret}"]`);
            if (bottomCell) {
                const dot2 = document.createElement('div');
                dot2.className = 'fret-marker-dot';
                dot2.style.top = '50%';
                dot2.style.transform = 'translate(-50%, -50%)';
                bottomCell.appendChild(dot2);
            }
        }
    }
}

function findNote(startNote, fret) {
    const startIndex = allNotes.indexOf(startNote);
    const noteIndex = (startIndex + fret) % 12;
    return allNotes[noteIndex];
}

function drawScale(scale) {
    // Clear only the notes, not the entire fretboard structure
    document.querySelectorAll('.note, .open-string-note').forEach(n => n.remove());
    
    // Draw the notes
    GUITAR_TUNING.forEach((stringInfo, stringIndex) => {
        // Handle open strings
        const openNoteInfo = scale.notes[stringInfo.openNote];
        const labelCell = document.querySelector(`td.string-label[data-string="${stringIndex}"]`);
        if (openNoteInfo) {
            // Clear the plain text string name before adding the styled note div
            labelCell.textContent = '';
            const noteDiv = document.createElement('div');
            // Add the note's identity AND the default faded class
            noteDiv.classList.add('open-string-note', openNoteInfo.degree, 'faded-note');
            noteDiv.textContent = stringInfo.name;
            noteDiv.dataset.fret = 0;
            labelCell.appendChild(noteDiv);
        } else {
             // The string name is now set during fretboard creation
        }

        // Handle fretted notes
        for (let fret = 1; fret <= NUM_FRETS; fret++) {
            const noteName = findNote(stringInfo.openNote, fret);
            const scaleNoteInfo = scale.notes[noteName];
            if (scaleNoteInfo) {
                const cell = document.querySelector(`td.fret[data-string="${stringIndex}"][data-fret="${fret}"]`);
                const noteDiv = document.createElement('div');
                 // Add the note's identity AND the default faded class
                noteDiv.classList.add('note', scaleNoteInfo.degree, 'faded-note');
                noteDiv.textContent = noteName;
                noteDiv.dataset.fret = fret;
                cell.appendChild(noteDiv);
            }
        }
    });
}

// function highlightPositions(positionsToHighlight) {
//     const allNoteDivs = document.querySelectorAll('.note, .open-string-note');
    
//     const highlightedRanges = pentatonicPositions
//         .filter(p => positionsToHighlight.includes(p.position))
//         .map(p => p.frets);

//     // If there are no positions to highlight, don't fade anything.
//     if (highlightedRanges.length === 0) {
//         return;
//     }

//     allNoteDivs.forEach(noteDiv => {
//         // Get the fret number from the note's dataset attribute.
//         // This works for both fretted notes and open-string notes.
//         const fret = parseInt(noteDiv.dataset.fret);
        
//         // Check if the note's fret falls within ANY of the highlighted ranges.
//         const isInHighlightedRange = highlightedRanges.some(range => fret >= range.min && fret <= range.max);

//         // If it's NOT in a highlighted range, fade it.
//         if (!isInHighlightedRange) {
//             noteDiv.classList.add('faded-note');
//         }
//     });
// }

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
        noteDiv.classList.add('faded-note');

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
            noteDiv.classList.remove('faded-note');
        }
    });
}

/**
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
        noteDiv.classList.add('faded-note');

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
            noteDiv.classList.remove('faded-note');
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

    GUITAR_TUNING.forEach((stringInfo, index) => {
        const stringRow = document.querySelector(`td.string-label[data-string="${index}"]`).parentElement;
        const rowRect = stringRow.getBoundingClientRect();

        // Calculate the vertical center of the row relative to the diagram container
        const y = rowRect.top - diagramRect.top + (rowRect.height / 2);

        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', x1);
        line.setAttribute('y1', y);
        line.setAttribute('x2', x2);
        line.setAttribute('y2', y);
        line.setAttribute('stroke', STRING_CONFIG[index].color);
        line.setAttribute('stroke-width', STRING_CONFIG[index].width);
        line.id = `string-${index}`; // Add an ID for easy selection with GSAP
        svgContainer.appendChild(line);
    });
}

// --- 4. Initial Drawing ---
// Choose which SCALE to draw
const scaleToDraw = cMajorPentatonic;


// --- Execution ---
drawFretboard();    // 1. Draw the board structure first
drawFretMarkers();  // 2. Add the fret marker dots
// drawScale(scaleToDraw); // Then draw the notes on top
drawStringsAsSVG();
// To highlight multiple positions, pass an array to the new function.
highlightPositions(scaleToDraw, ['p5a', 'p1a']);

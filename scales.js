// scales.js

class Scale {
    /**
     * Creates a new musical scale.
     * @param {string} name - The name of the scale.
     * @param {Object} notes - An object of note names and their metadata.
     * @param {Object} positions - An object defining scale positions.
     */
    constructor(name, notes, positions = {}) {
        this.name = name;
        this.notes = notes;
        this.positions = positions;
    }
}

// --- Define and Export Your Scales ---

// Pentatonic Scales
export const gMajorPentatonic = new Scale('G Major Pentatonic', {
    'G': { degree: 'root' }, 
    'A': { degree: 'second' },
    'B': { degree: 'third' }, 
    'D': { degree: 'fifth' },
    'E': { degree: 'sixth' }
}, {
    // A position defined only by a list of frets
    pos1: { frets: [2, 3, 4, 5]},
    pos2: { frets: [4, 5, 6, 7, 8]},
    pos3: { frets: [7, 8, 9, 10]},
    pos4: { frets: [9, 10, 11, 12]},
    pos5: {frets: [0, 1, 2, 3, 12, 13, 14, 15] },

    // A custom position defined by both frets AND strings
    // pos_custom1: {
    //     frets: [3, 4, 5],
    //     strings: ['G', 'B', 'e'] // Note: 'e' is the high e string
    // }
});

export const aMinorPentatonic = new Scale('A Minor Pentatonic', {
    'A': { degree: 'root' },
    'C': { degree: 'minorThird' },
    'D': { degree: 'fourth' },
    'E': { degree: 'fifth' },
    'G': { degree: 'minorSeventh' }
});

export const cMajorPentatonic = new Scale('C Major Pentatonic', {
    'C': { degree: 'root' },
    'D': { degree: 'second' },
    'E': { degree: 'third' },
    'G': { degree: 'fifth' },
    'A': { degree: 'sixth' }
}, {
    // Basic CAGED positions for C Major Pentatonic
    pos1: { frets: [7, 8, 9, 10] },      // E-shape
    pos2: { frets: [10, 11, 12] },     // D-shape
    pos3: { frets: [0, 1, 2, 3] },      // C-shape (open)
    pos4: { frets: [2, 3, 4, 5] },      // A-shape
    pos5: { frets: [5, 6, 7, 8] },       // G-shape
    pos_custom1: { //house of blues
        frets: [8, 9, 10],
        strings: ['G', 'B', 'e'] // Note: 'e' is the high e string
    },
    p5a: { //
        frets: [5, 6, 7, 8],
        strings: ['E', 'A', 'D', 'G'] // Note: 'e' is the high e string
    },
    p1a: { //
        frets: [8, 9, 10],
        strings: ['G', 'B', 'e'] // Note: 'e' is the high e string
    },

});

// Example of a full major scale
export const cMajor = new Scale('C Major', {
    'C': { degree: 'root' },
    'D': { degree: 'second' },
    'E': { degree: 'third' },
    'F': { degree: 'fourth' },
    'G': { degree: 'fifth' },
    'A': { degree: 'sixth' },
    'B': { degree: 'seventh' }
});
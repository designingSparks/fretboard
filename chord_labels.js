/* Clickable sequence labels, sharing note selection with timed playback. */
(() => {
    const container = document.getElementById('chord-labels');
    const panel = document.getElementById('chord-panel');
    const caption = document.getElementById('chord-label-title');
    let steps = [];
    let buttons = [];
    let playbackState = 'stopped';
    let playbackIndex = null;

    function selectStep(index) {
        if (!Number.isInteger(index) || index < 0 || index >= steps.length) return;
        buttons.forEach(({button, rowIndex}) => {
            const selected = rowIndex === index;
            button.classList.toggle('selected', selected);
            button.setAttribute('aria-pressed', String(selected));
        });
        // Update the notes and the corresponding label together, including shared notes.
        window.highlightNotes(JSON.stringify(steps[index].notes));
    }

    window.clearChordSelection = function() {
        buttons.forEach(({button}) => {
            button.classList.remove('selected');
            button.setAttribute('aria-pressed', 'false');
        });
    };

    window.renderChordSequence = function(sequence = [], title = 'Triad playing') {
        steps = sequence;
        playbackState = 'stopped';
        playbackIndex = null;
        buttons = [];
        container.replaceChildren();
        caption.textContent = title;
        caption.hidden = !title;
        container.setAttribute('aria-label', title || 'Chord sequence');
        steps.forEach((step, rowIndex) => {
            if (!step.chordName) return;
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'chord-label';
            button.dataset.label = step.chordName;
            button.setAttribute('aria-label', `${step.chordName}, step ${rowIndex + 1}`);
            button.setAttribute('aria-pressed', 'false');
            const label = document.createElement('span');
            label.textContent = step.chordName;
            button.appendChild(label);
            button.addEventListener('click', () => {
                if (playbackState !== 'playing') selectStep(rowIndex);
            });
            container.appendChild(button);
            buttons.push({button, rowIndex});
        });
        container.hidden = buttons.length === 0;
        panel.hidden = buttons.length === 0;
        window.clearNoteHighlights();
    };

    window.highlightSequenceStep = function(index) {
        if (playbackState !== 'playing' || !Number.isInteger(index)
                || index < 0 || index >= steps.length) return;
        playbackIndex = index;
        selectStep(index);
    };

    window.setChordPlaybackState = function(state) {
        if (!['playing', 'paused', 'stopped'].includes(state)) return;
        const previousState = playbackState;
        playbackState = state;
        buttons.forEach(({button}) => { button.disabled = state === 'playing'; });
        if (state === 'stopped') {
            playbackIndex = null;
            window.clearNoteHighlights();
        } else if (state === 'playing') {
            if (previousState === 'paused' && playbackIndex !== null) {
                selectStep(playbackIndex);
            } else if (previousState !== 'playing') {
                playbackIndex = null;
                window.clearNoteHighlights();
            }
        }
    };
})();

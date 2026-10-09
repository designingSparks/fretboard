/* Clickable sequence labels with hover previews, sharing notes with timed playback. */
(() => {
    const container = document.getElementById('chord-labels');
    const panel = document.getElementById('chord-panel');
    const caption = document.getElementById('chord-label-title');
    let steps = [];
    let buttons = [];
    let playbackState = 'stopped';
    let playbackIndex = null;
    let selectedIndex = null;
    let hoveredIndex = null;
    let hoverRestoreTimer = null;

    function cancelHoverRestore() {
        clearTimeout(hoverRestoreTimer);
        hoverRestoreTimer = null;
    }

    function splitLabel(chordName) {
        const subtext = [];
        const main = chordName.replace(/_?\{([^{}]*)\}/g, (_, text) => {
            subtext.push(text);
            return '';
        }).trim();
        return {main, subtext: subtext.join(' ').trim()};
    }

    function selectStep(index, preview = false) {
        if (!Number.isInteger(index) || index < 0 || index >= steps.length) return;
        cancelHoverRestore();
        if (!preview) selectedIndex = index;
        buttons.forEach(({button, rowIndex}) => {
            const selected = rowIndex === index;
            button.classList.toggle('selected', selected);
            button.setAttribute('aria-pressed', String(selected));
        });
        // Update the notes and the corresponding label together, including shared notes.
        window.highlightNotes(JSON.stringify(steps[index].notes));
    }

    window.clearChordSelection = function() {
        cancelHoverRestore();
        selectedIndex = null;
        hoveredIndex = null;
        buttons.forEach(({button}) => {
            button.classList.remove('selected');
            button.setAttribute('aria-pressed', 'false');
        });
    };

    window.moveChordSelection = function(direction) {
        if (playbackState === 'playing' || buttons.length === 0) return;
        const current = buttons.findIndex(({rowIndex}) =>
            rowIndex === (selectedIndex ?? hoveredIndex));
        const next = current === -1
            ? (direction > 0 ? 0 : buttons.length - 1)
            : Math.max(0, Math.min(buttons.length - 1, current + direction));
        hoveredIndex = null;
        const {button, rowIndex} = buttons[next];
        selectStep(rowIndex);
        button.focus({preventScroll: true});
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
            const text = splitLabel(step.chordName);
            button.type = 'button';
            button.className = 'chord-label';
            button.dataset.label = text.main;
            const accessibleLabel = [text.main, text.subtext].filter(Boolean).join(', ');
            button.setAttribute('aria-label', `${accessibleLabel}, step ${rowIndex + 1}`);
            button.setAttribute('aria-pressed', 'false');
            const label = document.createElement('span');
            label.className = 'chord-label-main';
            label.textContent = text.main;
            button.appendChild(label);
            if (text.subtext) {
                button.dataset.subtext = text.subtext;
                const subtext = document.createElement('span');
                subtext.className = 'chord-label-subtext';
                subtext.textContent = text.subtext;
                button.appendChild(subtext);
            }
            button.addEventListener('click', () => {
                if (playbackState !== 'playing') selectStep(rowIndex);
            });
            button.addEventListener('mouseenter', () => {
                if (playbackState === 'playing') return;
                hoveredIndex = rowIndex;
                selectStep(rowIndex, true);
            });
            button.addEventListener('mouseleave', () => {
                if (playbackState === 'playing' || hoveredIndex !== rowIndex) return;
                hoveredIndex = null;
                // Bridge the small gaps between labels without flashing the clicked chord.
                cancelHoverRestore();
                hoverRestoreTimer = setTimeout(() => {
                    hoverRestoreTimer = null;
                    if (selectedIndex !== null) selectStep(selectedIndex);
                    else window.clearNoteHighlights();
                }, 80);
            });
            container.appendChild(button);
            buttons.push({button, rowIndex});
        });
        container.hidden = buttons.length === 0;
        panel.hidden = buttons.length === 0;
        window.clearNoteHighlights();
        if (buttons.length) selectStep(buttons[0].rowIndex);
    };

    window.highlightSequenceStep = function(index) {
        if (playbackState !== 'playing' || !Number.isInteger(index)
                || index < 0 || index >= steps.length) return;
        playbackIndex = index;
        selectStep(index);
    };

    window.setChordPlaybackState = function(state) {
        if (!['playing', 'paused', 'stopped'].includes(state)) return;
        cancelHoverRestore();
        const previousState = playbackState;
        playbackState = state;
        hoveredIndex = null;
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

#Default play time for the note
TON = 500

#This is the entire scale
C_MAJOR_POS4_HIGHLIGHT = [
    ('e', 3),('e', 5), # High e string
    ('B', 3),('B', 5),('B', 6),
    ('G', 2),('G', 4),('G', 5),
    ('D', 2),('D', 3),('D', 5),
    ('A', 2),('A', 3),('A', 5),
    ('E', 3), ('E', 5), # Low E string
]

#This is the actual sequence that is played: C to C, i.e. a subset of the scale
C_MAJOR_POS4_PLAY = [
    [('A', 3), TON],
    [('A', 5), TON],
    # D string
    [('D', 2), TON],
    [('D', 3), TON],
    [('D', 5), TON],
    # G string
    [('G', 2), TON],
    [('G', 4), TON],
    [('G', 5), TON],
]

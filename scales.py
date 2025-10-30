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

C_MAJOR_POS5_HIGHLIGHT = [
    ('E', 5), ('E', 7), ('E', 8), # Low E string
    ('A', 5),('A', 7),('A', 8),
    ('D', 5),('D', 7),('D', 9),
    ('G', 5),('G', 7),
    ('B', 5),('B', 6),('B', 8),
    ('e', 5),('e', 7),('e', 8) # High e string
]

#This is the actual sequence that is played: C to C, i.e. a subset of the scale
C_MAJOR_POS5_PLAY = [
    #E string
    [('E', 8), TON],
    #A string
    [('A', 5), TON],
    [('A', 7), TON],
    [('A', 8), TON],
    # D string
    [('D', 5), TON],
    [('D', 7), TON],
    [('D', 9), TON],
    # G string
    [('G', 5), TON],
    # [('G', 4), TON],
    # [('G', 5), TON],
]
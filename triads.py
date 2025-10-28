TON = 1000

#All possible notes in the C major triads on the top 3 strings
C_MAJOR_TRIAD_HIGHLIGHT = [
    ('e', 0), ('e', 3), ('e', 8), ('e', 12), ('e', 15), ('e', 20), ('e', 24),
    ('B', 1), ('B', 5), ('B', 8), ('B', 13), ('B', 17), ('B', 20),
    ('G', 0), ('G', 5), ('G', 9), ('G', 12), ('G', 17), ('G', 21), ('G', 24)
]

C_MAJOR_TRIAD_SEQ = [
    [('e', 0), ('B', 1), ('G', 0), TON],
    [('e', 3), ('B', 5), ('G', 5), TON],
    [('e', 8), ('B', 8), ('G', 9), TON],
    [('e', 12), ('B', 13), ('G', 12), TON],
    # [('e', 15), ('B', 17), ('G', 17), TON],
    # [('e', 20), ('B', 20), ('G', 21), TON],
]
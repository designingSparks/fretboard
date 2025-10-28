STRING_ID = ['e', 'B', 'G', 'D', 'A', 'E']

#Contains all the possible notes of the fretboard.
FRETBOARD_NOTES_NAME = [
    # 0: High 'e' string
    ['E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E'],
    # 1: 'B' string
    ['B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],
    # 2: 'G' string
    ['G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G'],
    # 3: 'D' string
    ['D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D'],
    # 4: 'A' string
    ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A'],
    # 5: Low 'E' string
    ['E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E']
]

#Contains all the possible notes of the fretboard as MIDI notes
FRETBOARD_NOTES_MIDI = [
    # 0: High 'e' string (E4 = 64)
    [64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88],
    # 1: 'B' string (B3 = 59)
    [59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83],
    # 2: 'G' string (G3 = 55)
    [55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79],
    # 3: 'D' string (D3 = 50)
    [50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74],
    # 4: 'A' string (A2 = 45)
    [45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69],
    # 5: Low 'E' string (E2 = 40)
    [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64]
]

def create_tuple(string_list, note_list):
    tuple_list = []
    for note in note_list:
        for string_id in string_list:
            for i in range(len(FRETBOARD_NOTES_NAME[string_id])):
                if FRETBOARD_NOTES_NAME[string_id][i] == note:
                    tuple_list.append((string_id, i))

    # Sort the list of tuples. It will sort by the first element (string_id),
    # and then by the second element (fret number) for ties.
    tuple_list.sort()
    #Substitute the first tuple element for the string name, 'e' = 0 etc
    for i in range(len(tuple_list)):
        tuple_list[i] = (STRING_ID[tuple_list[i][0]], tuple_list[i][1])

    return tuple_list


def print_tuple(tuple_list):
    '''
    Print the items in tuple_list on the same line if the string id is the same.
    The output is formatted as a Python list of tuples.
    '''
    output_lines = {}

    for string_name, fret_number in tuple_list:
        if string_name not in output_lines:
            output_lines[string_name] = []
        output_lines[string_name].append(f"('{string_name}', {fret_number})")

    for string_name, tuple_strs in output_lines.items():
        line = ", ".join(tuple_strs) + ","
        print(f"    {line:<30}")


if __name__ == "__main__":
    from pprint import pprint
    notes = create_tuple([0,1,2], ['C', 'E', 'G'])
    print_tuple(notes)
'''
I want to create just the raw notes for pentatonic scales 1-5 in a given scale 
'''

from generate_scale import *

def remove_duplicates(notes):
    unique_notes = []
    for note in notes:
        if note not in unique_notes:
            unique_notes.append(note)
    return unique_notes

if __name__ == "__main__":
    scale = 'Gmaj'
    
    pattern1_notes = generate_pattern(scale, 1)
    pattern2_notes = generate_pattern(scale, 2)
    pattern3_notes = generate_pattern(scale, 3)
    pattern4_notes = generate_pattern(scale, 4)
    pattern5_notes = generate_pattern(scale, 5)

    all_notes = pattern1_notes + pattern2_notes + pattern3_notes + pattern4_notes + pattern5_notes
    all_notes = remove_duplicates(all_notes)

    print(all_notes)
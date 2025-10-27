#Shifts the pitch of the BASE_MIDI_NOTE to create the missing MIDI notes
#This is becuase the Kontakt instrument can't generate up to note 88.

import librosa
import soundfile as sf
import os

# --- Configuration ---
# The name of your source audio file (the highest note you can record)
base_note_file = 'note_79.wav' 
BASE_MIDI_NOTE = 79 # G5 is MIDI note 79

# Create a directory to store the new notes
output_dir = 'shifted_notes'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# --- Main Script ---
print(f"Loading base note file: {base_note_file}")
try:
    # Load the audio file
    y, sr = librosa.load(base_note_file, sr=None) # sr=None preserves original sample rate
except FileNotFoundError:
    print(f"Error: The file '{base_note_file}' was not found. Please make sure it's in the same directory.")
    exit()

print("Starting pitch shifting process...")

# Loop to create the 9 new notes you need (from +1 to +9 semitones)
for semitones_to_shift in range(1, 10):
    
    # Calculate the new MIDI note number
    new_midi_note = BASE_MIDI_NOTE + semitones_to_shift
    note_name = f"note_{new_midi_note}"
    
    print(f"  -> Shifting by {semitones_to_shift} semitones to create MIDI note {new_midi_note}...")

    # Perform the pitch shift ✨
    y_shifted = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=semitones_to_shift)
    
    # Define the output filename
    output_filename = os.path.join(output_dir, f"{note_name}.wav")
    
    # Save the new audio file
    sf.write(output_filename, y_shifted, sr)

print(f"\n✅ Success! Your 9 new notes have been saved in the '{output_dir}' folder.")
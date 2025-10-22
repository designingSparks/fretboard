import os
from pedalboard import Pedalboard, Distortion, Reverb, Gain, Limiter
from pedalboard.io import AudioFile

# --- Configuration ---
input_dir = '../notes'
output_dir = 'distortion' # This will be created in the same directory as the script

# --- Setup ---
# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created output directory: {output_dir}")

# --- Define Your Effect --- 
# Create a Pedalboard, which can hold one or more effects.
# This is defined once and reused for each file.
board = Pedalboard([
    Distortion(drive_db=30.0),
    Gain(gain_db=-20.0),
    # Limiter(threshold_db=-10.0, release_ms=50),
    # Reverb()
])

# --- Batch Processing Loop ---
print(f"Processing .wav files from '{input_dir}'...")

try:
    # Get a list of all .wav files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.wav'):
            input_file_path = os.path.join(input_dir, filename)
            output_file_path = os.path.join(output_dir, filename)
            
            print(f"  -> Processing {filename}...")
            
            # Process the file in chunks to be memory-efficient
            with AudioFile(input_file_path) as f:
                # Open an output file with the same samplerate and number of channels
                with AudioFile(output_file_path, 'w', f.samplerate, f.num_channels) as o:
                    # Read one second of audio at a time, until the file is empty:
                    while f.tell() < f.frames:
                        # Read a chunk of audio
                        chunk = f.read(f.samplerate)
                        
                        # Run the audio through our pedalboard
                        effected = board(chunk, f.samplerate, reset=False)
                        # effected = effected * 0.07
                        # Write the output to our output file
                        o.write(effected)

    print(f"\n✅ Success! Distorted notes have been saved in the '{output_dir}' folder.")

except FileNotFoundError:
    print(f"\n❌ Error: The input directory '{input_dir}' was not found. Please make sure the path is correct.")
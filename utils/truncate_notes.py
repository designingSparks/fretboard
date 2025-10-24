# I have a bunch of .wav files in ../notes. They are named note_n.wav, where n is a midi number.
# The notes need to be trimmed at the beginning. Convert the .wav file to a numpy array and find 
# the index, i, where the amplitude exceeds 1000 or -1000. Now create a new array with the first 0:i-100 points deleted.
# save the output to ../clean/clean_n.wav
import numpy as np
# import soundfile as sf
from scipy.io import wavfile
import os

# Define input and output directories
INPUT_DIR = 'notes'
OUTPUT_DIR = 'clean'
THRESHOLD = 1000  # Amplitude threshold to detect the start of the note
PRE_ROLL_SAMPLES = 100 # Number of samples to keep before the threshold is met

def truncate_and_save_note(input_filepath, output_filepath, threshold, pre_roll_samples):
    """
    Loads a WAV file, finds the start of the note based on an amplitude threshold,
    truncates the beginning, and saves the cleaned WAV file.

    Args:
        input_filepath (str): Path to the input WAV file.
        output_filepath (str): Path to save the cleaned WAV file.
        threshold (int): Amplitude threshold to detect the note's start.
        pre_roll_samples (int): Number of samples to keep before the detected start.
    """
    try:
        # data, samplerate = sf.read(input_filepath)
        samplerate, data = wavfile.read(input_filepath)

        # Ensure data is 1D (mono) for simpler thresholding if it's stereo
        if data.ndim > 1:
            data = data.mean(axis=1)

        # Set the first 0.05 seconds of data to zero to remove initial glitches
        glitch_samples = int(0.05 * samplerate)
        data[:glitch_samples] = 0

        # Find the first index where amplitude exceeds the threshold
        # np.where returns a tuple of arrays, we want the first element of the first array
        # np.abs is used to detect both positive and negative peaks
        onset_indices = np.where(np.abs(data) > threshold)[0]



        if len(onset_indices) == 0:
            print(f"Warning: No amplitude above threshold {threshold} found in {input_filepath}. Skipping.")
            return

        first_onset_idx = onset_indices[0]

        # Calculate the start index for truncation, ensuring it's not negative
        start_idx = max(0, first_onset_idx - pre_roll_samples)

        # Truncate the array
        cleaned_data = data[start_idx:]

        # Save the cleaned audio
        # sf.write(output_filepath, cleaned_data, samplerate)
        wavfile.write(output_filepath, samplerate, cleaned_data)

        print(f"Cleaned '{os.path.basename(input_filepath)}' and saved to '{output_filepath}'")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_filepath}")
    except Exception as e:
        print(f"An error occurred while processing {input_filepath}: {e}")

if __name__ == "__main__":
    # Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

    print(f"\nProcessing .wav files from '{INPUT_DIR}'...")

    if not os.path.isdir(INPUT_DIR):
        print(f"Error: Input directory '{INPUT_DIR}' not found. Exiting.")
    else:
        for filename in os.listdir(INPUT_DIR):
            if filename.endswith('.wav'):
                input_path = os.path.join(INPUT_DIR, filename)
                num = filename.split('_')[1].split('.')[0]
                output_path = os.path.join(OUTPUT_DIR, f"clean_{num}.wav")
                truncate_and_save_note(input_path, output_path, THRESHOLD, PRE_ROLL_SAMPLES)
        print("\nBatch truncation complete.")
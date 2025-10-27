# Cycle through all .wav files in the ./clean directory and convert them to numpy arrays, then save them to
# the same directory with the .npy extension.
# The samplerate is 44100

import numpy as np
from scipy.io import wavfile
import os

CLEAN_DIR = 'clean'

def convert_wav_to_npy(directory):
    """
    Cycles through all .wav files in the specified directory, converts them
    to NumPy arrays, and saves them as .npy files in the same directory.
    """
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' not found.")
        return

    print(f"Converting .wav files in '{directory}' to .npy...")

    for filename in os.listdir(directory):
        if filename.endswith('.wav'):
            wav_filepath = os.path.join(directory, filename)
            npy_filename = filename.replace('.wav', '.npy')
            npy_filepath = os.path.join(directory, npy_filename)

            try:
                samplerate, data = wavfile.read(wav_filepath)
                print('Samplerate: {}'.format(samplerate))

                # This will probably print 'int16'
                print(f"Original WAV data type: {data.dtype}")

                # For consistency, ensure data is float32, which is common for audio processing
                # and what librosa typically outputs.
                # if data.dtype != np.float32:
                #     data = data.astype(np.float32) / np.iinfo(data.dtype).max

                np.save(npy_filepath, data)
                print(f"Converted '{filename}' to '{npy_filename}'")

            except Exception as e:
                print(f"Error processing '{filename}': {e}")
    print("Conversion complete.")

if __name__ == "__main__":
    convert_wav_to_npy(CLEAN_DIR)

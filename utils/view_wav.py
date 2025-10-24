import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile

# # --- Create a dummy .wav file for this example ---
# # (In your real code, you would just have 'your_file.wav')
# sample_rate_dummy = 44100
# duration_dummy = 2  # seconds
# t_dummy = np.linspace(0., duration_dummy, int(sample_rate_dummy * duration_dummy), endpoint=False)
# # A 440 Hz (A4) sine wave
# amplitude_dummy = np.iinfo(np.int16).max * 0.7
# data_dummy = (amplitude_dummy * np.sin(2. * np.pi * 440. * t_dummy)).astype(np.int16)
# wavfile.write('example_A4_tone.wav', sample_rate_dummy, data_dummy)
# -------------------------------------------------

FNAME = '../notes/note_65.wav'

# 1. Read the .wav file
#    'samplerate' is samples per second (e.g., 44100)
#    'data' is a numpy array of the samples
try:
    samplerate, data = wavfile.read(FNAME)
    print(f"Sample rate: {samplerate} Hz")
    print(f"Data shape: {data.shape}")
    print(f"Data type: {data.dtype}")
    print(f"Duration: {len(data) / samplerate:.2f} seconds")

    # 2. Create a time axis
    #    The number of samples is len(data)
    #    The total time is len(data) / samplerate
    time = np.linspace(0., len(data) / samplerate, len(data))

    # 3. Plot the waveform(s)
    plt.figure(figsize=(12, 5))
    plt.title(f"Waveform of '{FNAME}'")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)

    if data.ndim > 1:
        print("File is stereo. Plotting both channels.")
        plt.plot(time, data[:, 0], label='Left Channel')
        plt.plot(time, data[:, 1], label='Right Channel')
        plt.legend()
    else:
        print("File is mono. Plotting single channel.")
        plt.plot(time, data, label='Mono Channel')
        plt.legend()
    plt.show()

    # --- Plot just a small slice to see the sine wave ---
    # Plotting millions of points (e.g., a 1-minute file)
    # can be slow and look like a solid block.
    # Let's zoom in on the first 500 samples.
    # plt.figure(figsize=(12, 5))
    # plt.plot(time[:500], data_to_plot[:500])
    # plt.title("Zoomed-in Waveform (First 500 Samples)")
    # plt.xlabel("Time (s)")
    # plt.ylabel("Amplitude")
    # plt.grid(True)
    # plt.show()

except FileNotFoundError:
    print("Error: The file was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
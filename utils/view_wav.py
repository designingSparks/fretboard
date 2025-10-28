import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile

#Relative to project directory
FNAME = './clean/clean_60.wav'

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

except FileNotFoundError:
    print("Error: The file was not found.")
    
except Exception as e:
    print(f"An error occurred: {e}")
import numpy as np
from scipy.io import wavfile

def delay_and_sum_beamforming(input_wav, theta, phi, radius, speed_of_sound=343):
    # Read the input wav file============================================
    sample_rate, data1 = wavfile.read(input_wav)


    #Standardization process=============================================
    # Ensure the data is in float format
    data1 = data1.astype(np.float32)
    # Calculate the RMS of each channel
    rms_per_channel = np.sqrt(np.mean(data1 ** 2, axis=0))
    # Calculate the average RMS across all channels
    average_rms = np.mean(rms_per_channel)
    # Normalize each channel to have the same RMS as the average RMS
    data = np.zeros_like(data1)
    for i in range(data.shape[1]):  # Iterate over each channel
        data[:, i] = data1[:, i] * (average_rms / rms_per_channel[i])


    # Number of channels and samples
    num_samples, num_channels = data.shape
    
    # Convert theta and phi to radians
    theta = np.deg2rad(theta)
    phi = np.deg2rad(phi)
    
    # Calculate the positions of the microphones========================
    N_MICS = num_channels
    N_MICS_EVEN = N_MICS-N_MICS%2
    mic_positions = np.array([
        [radius * np.cos(-2 * np.pi * i / N_MICS_EVEN), radius * np.sin(-2 * np.pi * i / N_MICS_EVEN), 0] #-ve sign because mics have been placed clockwise
        for i in range(N_MICS_EVEN)
    ])
    if N_MICS%2:
        mic_positions = np.vstack([mic_positions, [0, 0, 0]])  # Adding the last mic to center if odd number of mics are there.
    
    # Calculate the delays===============================================
    target_direction = np.array([
        np.sin(phi) * np.cos(theta),
        np.sin(phi) * np.sin(theta),
        np.cos(phi)
    ])
    
    delays = np.dot(mic_positions, target_direction) / speed_of_sound
    delays -= np.min(delays)  # Normalize delays so that the smallest delay is zero
    print(delays)
    # Apply the delays
    output = np.zeros(num_samples)
    print("data shape", np.shape(data[:,2]))
    print("output shape", np.shape(output))
    #print(num_channels)
    for channel in range(num_channels):
        delay_samples = int(sample_rate * delays[channel])
        print(delay_samples)
        if delay_samples < num_samples:
            
            #output[:num_samples-delay_samples] += data[channel, delay_samples:]
            #output[:num_samples-delay_samples] += data[delay_samples:,channel]
            output[delay_samples:] += data[:num_samples-delay_samples,channel]
    
    # Normalize output by the number of channels==========================
    output /= num_channels
    
    # Write the output wav file===========================================
    wavfile.write(input_wav[:-4]+f"_beamformed_{int(theta*180/np.pi)}_{int(phi*180/np.pi)}.wav", sample_rate, output.astype(np.int16))

# Example usage
file_path = "../../DSB_TEST_21_11_2024/wav/"
input_wav = 'DSB_TEST_BALLMILL_THETA_MINUS135_PHI_45_audio.wav'
theta = 45  # Target azimuth in degrees
phi = 85   # Target elevation in degrees
radius = 0.05  # Radius of the circular array in meters

delay_and_sum_beamforming(file_path+input_wav, theta, phi, radius)

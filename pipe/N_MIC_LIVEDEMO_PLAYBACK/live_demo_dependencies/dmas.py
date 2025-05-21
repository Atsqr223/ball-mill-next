import numpy as np
from scipy.io import wavfile
import scipy.signal as signal
from .BPF import *
def dmas(data1, sample_rate,theta, phi, radius, lowcut=None,highcut=None,speed_of_sound=343): #mic radius in meters
    # Read the input wav file============================================
    #sample_rate, data1 = wavfile.read(input_wav)


    #Standardization process=============================================
    # Ensure the data is in float format
    data1 = data1.astype(np.float32)
    data = data1
    '''# Calculate the RMS of each channel
    rms_per_channel = np.sqrt(np.mean(data1 ** 2, axis=0))
    # Calculate the average RMS across all channels
    average_rms = np.mean(rms_per_channel)
    # Normalize each channel to have the same RMS as the average RMS
    data = np.zeros_like(data1)
    for i in range(data.shape[1]):  # Iterate over each channel
        data[:, i] = data1[:, i] * (average_rms / rms_per_channel[i])'''
    


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
    #print(delays)

    #Multiplication======================================================
    #Step 1: Find the mic nearest to current theta.
    nearest_mic_index = int(np.round((-theta/(2*np.pi)*N_MICS_EVEN)%N_MICS_EVEN,0))
    #Step 2: DMAS
    #i=nearest_mic_index
    dmas_array = np.zeros(num_samples)
    #for i in [nearest_mic_index]:
    total_product_count = 0
    for i in [(nearest_mic_index-1)%N_MICS_EVEN,nearest_mic_index,(nearest_mic_index+1)%N_MICS_EVEN]:
        delay_i = int(sample_rate * delays[i])
        for j in range(N_MICS):
            if j!= i:
                delay_j = int(sample_rate * delays[j])
                if delay_j < num_samples and delay_i<num_samples:
                    current_product_array = np.append(np.array([0]*delay_i), data[:num_samples-delay_i,i]) #slide reference channel to the right
                    current_product_array[delay_j:] = np.multiply(current_product_array[delay_j:],data[:num_samples-delay_j,j]) #slide current channel to the right and multiply with ref channel.
                    current_product_array = np.multiply(np.sign(current_product_array),np.sqrt(np.abs(current_product_array))) #abs, square root, and give sign.
                    dmas_array = np.add(dmas_array,current_product_array) #accumulate the product array in dmas array.
                    total_product_count+=1
    dmas_array = np.divide(dmas_array,total_product_count) #divide by number of summations to preserve the original scale
    dmas_array = np.abs(signal.hilbert(dmas_array)) #find envelope
    
    if lowcut!=None:
        dmas_array=butter_bandpass_filter(dmas_array,lowcut = lowcut, highcut=lowcut, fs=sample_rate, order=5) #band pass filter

    return dmas_array
    # Write the output wav file===========================================
    

# Example usage
'''file_path = "E:/Office/ALL_DATA/DSB_TEST_21_11_2024/wav/"
input_wav = 'DSB_TEST_BALLMILL_THETA_MINUS135_PHI_45_audio.wav'
theta = 45 # Target azimuth in degrees 45
phi = 85   # Target elevation in degrees 85
radius = 0.05  # Radius of the circular array in meters
sample_rate, data1 = wavfile.read(file_path+input_wav)
dmas_array = dmas(data1,sample_rate, theta, phi, radius)
wavfile.write(file_path+input_wav[:-4]+f"_dmas_{int(theta)}_{int(phi)}.wav", sample_rate, dmas_array.astype(np.int16))'''

import numpy as np
from matplotlib import pyplot as plt

#generating bpfilt matrix
def generate_bpfilt(WINDOW_SIZE=1001,TOTAL_BANDS=40,R_b=48000,lower_freq=100,upper_freq=4000,tapered=True):
    T_b = 1/R_b
    bpFilt = []
    fc = np.linspace(lower_freq,upper_freq,TOTAL_BANDS)
    for i in range(WINDOW_SIZE):
        bpFilt.append([])
        
    for f in fc:
        for i in range(WINDOW_SIZE):
            if tapered:
                #bpFilt[i].append( np.sin(2*np.pi*f*i*T_b)*(0.55-0.45*np.cos(2*np.pi*i/WINDOW_SIZE)) )
                bpFilt[i].append( np.sin(2*np.pi*f*i*T_b)*(0.55-0.47*np.cos(2*np.pi*i/WINDOW_SIZE)) )
            else:
                bpFilt[i].append( np.sin(2*np.pi*f*i*T_b) )
    bpFilt = np.array(bpFilt)
    fc=np.array(fc)
    return fc,bpFilt

def generate_bpfilt_arange(WINDOW_SIZE=1001,BAND_DISTANCE=100,R_b=48000,lower_freq=100,upper_freq=4100,tapered=True):
    T_b = 1/R_b
    bpFilt = []
    fc = np.arange(lower_freq,upper_freq,BAND_DISTANCE)
    for i in range(WINDOW_SIZE):
        bpFilt.append([])
        
    for f in fc:
        for i in range(WINDOW_SIZE):
            if tapered:
                bpFilt[i].append( np.sin(2*np.pi*f*i*T_b)*(0.55-0.45*np.cos(2*np.pi*i/WINDOW_SIZE)) )
            else:
                bpFilt[i].append( np.sin(2*np.pi*f*i*T_b) )
    bpFilt = np.array(bpFilt)
    fc=np.array(fc)
    return fc,bpFilt

def generate_bpfilt_varyband(BAND_DISTANCE=200,R_b=48000,lower_freq=1000,upper_freq=7000,tapered=True):
    T_b = 1/R_b
    bpFilt = []
    fc = np.arange(lower_freq,upper_freq,BAND_DISTANCE)
    bw = BAND_DISTANCE
    fc=np.array(fc)
    return fc,bw

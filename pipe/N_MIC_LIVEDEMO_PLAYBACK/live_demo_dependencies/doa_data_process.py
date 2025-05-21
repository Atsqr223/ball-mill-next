from .glob_vars import *
from .DOA_supporting_functions import *
import numpy as np
from scipy.io import wavfile
import scipy.io as spio
import time

frequency = SAMPLING_RATE # Frequency of the input data

def data_process_plane_animated(entire_data,fc,bpFilt,FRAMES_PER_PLOT,ub=int(frequency*1+6000),magType='lin', theta_offset=180, PLANE_HEIGHT=55,filtering=False,normalization=False):
    global frequency,THETA_INTERVALS, PHI_INTERVALS, PLANE_LENGTH_INTERVALS


    #Plotting steps===================================================

    data = np.zeros((FRAMES_PER_PLOT,4),float)
    
    for k in range(0,4,1):
        print(k)
        data[:,k] = 1*entire_data[ub-FRAMES_PER_PLOT:ub:1,k]

    data = data.astype(float)

    #Normalize (mandatory)
    if filtering or normalization:
        for k in range(0,4,1):
            #filter
            if filtering:
                #data[:,k] = np.convolve(data[:,k], np.ones(moving_average_window_size) / moving_average_window_size, mode='same')
                data[:,k]=scipy.signal.savgol_filter(data[:,k], savitsky_window_length, savitsky_poly_order)
            #normalize
            if normalization:
                data[:,k] = data[:,k]/max(data[:,k])

    bands_id =    list(range(len(fc))) #detect_significant_bands(bpFilt, data) #changed
    print("significant band id's: ",bands_id)
    if magType == 'lin':
        p_music = np.ones((PLANE_LENGTH_INTERVALS,PLANE_LENGTH_INTERVALS),float) #2D array #changed from ones to zeros
    else:
        p_music = np.zeros((PLANE_LENGTH_INTERVALS,PLANE_LENGTH_INTERVALS),float) #2D array #changed from ones to zeros
    p_music_temp = np.ones((PLANE_LENGTH_INTERVALS,len(bands_id),PLANE_LENGTH_INTERVALS),float) #3d array
    
    len_bands_id=len(bands_id)
    for k in range(len_bands_id):

        p_music_temp[::,k] = estimate_music_spectrum_2D_plane(data,bpFilt,fc[bands_id[k]],
                                                              bands_id[k],
                                                              PLANE_HEIGHT,
                                                              theta_offset=theta_offset) #2d array (theta vs phi)

        temp1 = np.reshape(p_music_temp[::,k],(PLANE_LENGTH_INTERVALS,PLANE_LENGTH_INTERVALS)) #2d array (theta vs phi)
        if magType == "lin":
            p_music = p_music*(temp1/np.max(temp1)) #Normalization
        elif magType == "log":
            p_music = p_music+10*np.log10(temp1)/len_bands_id

        elif magType == "linadd":
            p_music = p_music+temp1/np.max(temp1)#len_bands_id
        elif magType == "linaddwithoutnorm":
            p_music = p_music+temp1#len_bands_id
        #p_music = p_music*(temp1)
        #p_music = p_music+temp1/(np.max(temp1)*len_bands_id) #Changed normalization

    return p_music

def data_process_pipe_animated(entire_data,fc,bpFilt,magType='linadd',theta_offset=180):
    global frequency,PIPE_LENGTH,PIPE_DIAMETER,PIPE_DISTANCE,PIPE_LENGTH_INTERVALS,PIPE_DIAMETER_INTERVALS


    #Plotting steps===================================================

    data = entire_data
    data = data.astype(float)
    #print(np.max(data),np.min(data))
    bands_id =    list(range(len(fc))) #detect_significant_bands(bpFilt, data) #changed
    print("significant band id's: ",bands_id)
    
    p_music = np.zeros((PIPE_LENGTH_INTERVALS,PIPE_DIAMETER_INTERVALS),float) #2D array #changed from ones to zeros
    p_music_temp = np.ones((PIPE_LENGTH_INTERVALS,len(bands_id),PIPE_DIAMETER_INTERVALS),float) #3d array
    
    len_bands_id=len(bands_id)
    for k in range(len_bands_id):

        p_music_temp[::,k] = estimate_music_spectrum_2D_pipe_another(data,bpFilt,fc[bands_id[k]],bands_id[k],theta_offset=theta_offset)

        temp1 = np.reshape(p_music_temp[::,k],(PIPE_LENGTH_INTERVALS,PIPE_DIAMETER_INTERVALS)) #2d array (theta vs phi)
        if magType == "lin":
            p_music = p_music*(temp1/np.max(temp1)) #Normalization
        elif magType == "log":
            p_music = p_music+10*np.log10(temp1)/len_bands_id

        elif magType == "linadd":
            p_music = p_music+temp1/np.max(temp1)#len_bands_id
        elif magType == "linaddwithoutnorm":
            p_music = p_music+temp1#len_bands_id

    return p_music

def data_process_pipe_animated_varyband(entire_data,fc,bw,magType='linadd',theta_offset=180):
    global frequency,PIPE_LENGTH,PIPE_DIAMETER,PIPE_DISTANCE,PIPE_LENGTH_INTERVALS,PIPE_DIAMETER_INTERVALS


    #Plotting steps===================================================

    data = entire_data
    data = data.astype(float)
    #print(np.max(data),np.min(data))
    bands_id =    list(range(len(fc))) #detect_significant_bands(bpFilt, data) #changed
    print("significant band id's: ",bands_id)
    
    p_music = np.zeros((PIPE_LENGTH_INTERVALS,PIPE_DIAMETER_INTERVALS),float) #2D array #changed from ones to zeros
    p_music_temp = np.ones((PIPE_LENGTH_INTERVALS,len(bands_id),PIPE_DIAMETER_INTERVALS),float) #3d array
    
    len_bands_id=len(bands_id)
    for k in range(len_bands_id):

        p_music_temp[::,k] = estimate_music_spectrum_2D_pipe_varyband(data,fc[bands_id[k]],bw,bands_id[k],theta_offset=theta_offset)

        temp1 = np.reshape(p_music_temp[::,k],(PIPE_LENGTH_INTERVALS,PIPE_DIAMETER_INTERVALS)) #2d array (theta vs phi)
        if magType == "lin":
            p_music = p_music*(temp1/np.max(temp1)) #Normalization
        elif magType == "log":
            p_music = p_music+10*np.log10(temp1)/len_bands_id

        elif magType == "linadd":
            p_music = p_music+temp1/np.max(temp1)#len_bands_id
        elif magType == "linaddwithoutnorm":
            p_music = p_music+temp1#len_bands_id

    return p_music

def data_process_pipe_animated_varyband_sfreqs(entire_data,fc,bw,magType='linadd',theta_offset=180):
    global frequency,PIPE_LENGTH,PIPE_DIAMETER,PIPE_DISTANCE,PIPE_LENGTH_INTERVALS,PIPE_DIAMETER_INTERVALS


    #Plotting steps===================================================

    data = entire_data
    data = data.astype(float)
    #print(np.max(data),np.min(data))
    bands_id =    list(range(len(fc))) #detect_significant_bands(bpFilt, data) #changed
    print("significant band id's: ",bands_id)
    
    p_music = np.zeros((PIPE_LENGTH_INTERVALS,PIPE_DIAMETER_INTERVALS),float) #2D array #changed from ones to zeros
    p_music_temp = np.ones((PIPE_LENGTH_INTERVALS,len(bands_id),PIPE_DIAMETER_INTERVALS),float) #3d array
    
    len_bands_id=len(bands_id)

    sfreq_maps_list=[]
    for k in range(len_bands_id):

        p_music_temp[::,k] = estimate_music_spectrum_2D_pipe_varyband(data,fc[bands_id[k]],bw,bands_id[k],theta_offset=theta_offset)

        temp1 = np.reshape(p_music_temp[::,k],(PIPE_LENGTH_INTERVALS,PIPE_DIAMETER_INTERVALS)) #2d array (theta vs phi)
        if magType == "lin":
            p_music = p_music*(temp1/np.max(temp1)) #Normalization
        elif magType == "log":
            p_music = p_music+10*np.log10(temp1)/len_bands_id

        elif magType == "linadd":
            p_music = p_music+temp1/np.max(temp1)#len_bands_id
        elif magType == "linaddwithoutnorm":
            p_music = p_music+temp1#len_bands_id

        tempmax = np.max(temp1)
        tempmin = np.min(temp1)
        sfreq_maps_list.append((temp1-tempmin)/(tempmax-tempmin))

    return p_music,sfreq_maps_list

def data_process_animated(entire_data,fc,bpFilt,magType='linadd',theta_offset=180):
    global frequency,THETA_INTERVALS,PHI_INTERVALS


    #Plotting steps===================================================

    data = entire_data
    data = data.astype(float)
    #print(np.max(data),np.min(data))
    
    bands_id =    list(range(len(fc))) #detect_significant_bands(bpFilt, data) #changed
    print("significant band id's: ",bands_id)
    
    p_music = np.zeros((THETA_INTERVALS,PHI_INTERVALS),float) #2D array #changed from ones to zeros
    p_music_temp = np.ones((THETA_INTERVALS,len(bands_id),PHI_INTERVALS),float) #3d array
    
    len_bands_id=len(bands_id)
    for k in range(len_bands_id):

        p_music_temp[::,k] = estimate_music_spectrum_2D(data,bpFilt,fc[bands_id[k]],bands_id[k],theta_offset=theta_offset)

        temp1 = np.reshape(p_music_temp[::,k],(THETA_INTERVALS,PHI_INTERVALS)) #2d array (theta vs phi)
        if magType == "lin":
            p_music = p_music*(temp1/np.max(temp1)) #Normalization
        elif magType == "log":
            p_music = p_music+10*np.log10(temp1)/len_bands_id

        elif magType == "linadd":
            p_music = p_music+temp1/np.max(temp1)#len_bands_id
        elif magType == "linaddwithoutnorm":
            p_music = p_music+temp1#len_bands_id

    return p_music

def data_process_plane_animated_2(entire_data,fc,bpFilt,magType='linadd',theta_offset=180):
    global frequency,PLANE_LENGTH,PLANE_HEIGHT,PLANE_LENGTH_INTERVALS


    #Plotting steps===================================================

    data = entire_data
    data = data.astype(float)
    #print(np.max(data),np.min(data))
    bands_id =    list(range(len(fc))) #detect_significant_bands(bpFilt, data) #changed
    print("significant band id's: ",bands_id)
    
    p_music = np.zeros((PLANE_LENGTH_INTERVALS,PLANE_LENGTH_INTERVALS),float) #2D array #changed from ones to zeros
    p_music_temp = np.ones((PLANE_LENGTH_INTERVALS,len(bands_id),PLANE_LENGTH_INTERVALS),float) #3d array
    
    len_bands_id=len(bands_id)
    for k in range(len_bands_id):

        p_music_temp[::,k] = estimate_music_spectrum_2D_plane_another(data,bpFilt,fc[bands_id[k]],bands_id[k],theta_offset=theta_offset)

        temp1 = np.reshape(p_music_temp[::,k],(PLANE_LENGTH_INTERVALS,PLANE_LENGTH_INTERVALS)) #2d array (theta vs phi)
        if magType == "lin":
            p_music = p_music*(temp1/np.max(temp1)) #Normalization
        elif magType == "log":
            p_music = p_music+10*np.log10(temp1)/len_bands_id

        elif magType == "linadd":
            p_music = p_music+temp1/np.max(temp1)#len_bands_id
        elif magType == "linaddwithoutnorm":
            p_music = p_music+temp1#len_bands_id

    return p_music

#Plane live================================================
def data_process_plane_animated_varyband_sfreqs(entire_data,fc,bw,magType='linadd',theta_offset=180):
    global frequency,PLANE_LENGTH,PLANE_HEIGHT,PLANE_LENGTH_INTERVALS


    #Plotting steps===================================================

    data = entire_data
    data = data.astype(float)
    #print(np.max(data),np.min(data))
    bands_id =    list(range(len(fc))) #detect_significant_bands(bpFilt, data) #changed
    print("significant band id's: ",bands_id)
    
    p_music = np.zeros((PLANE_LENGTH_INTERVALS,PLANE_LENGTH_INTERVALS),float) #2D array #changed from ones to zeros
    p_music_temp = np.ones((PLANE_LENGTH_INTERVALS,len(bands_id),PLANE_LENGTH_INTERVALS),float) #3d array
    
    len_bands_id=len(bands_id)

    sfreq_maps_list=[]
    for k in range(len_bands_id):

        p_music_temp[::,k] = estimate_music_spectrum_2D_plane_varyband(data,fc[bands_id[k]],bw,bands_id[k],theta_offset=theta_offset)

        temp1 = np.reshape(p_music_temp[::,k],(PLANE_LENGTH_INTERVALS,PLANE_LENGTH_INTERVALS)) #2d array (theta vs phi)
        if magType == "lin":
            p_music = p_music*(temp1/np.max(temp1)) #Normalization
        elif magType == "log":
            p_music = p_music+10*np.log10(temp1)/len_bands_id

        elif magType == "linadd":
            p_music = p_music+temp1/np.max(temp1)#len_bands_id
        elif magType == "linaddwithoutnorm":
            p_music = p_music+temp1#len_bands_id

        tempmax = np.max(temp1)
        tempmin = np.min(temp1)
        sfreq_maps_list.append((temp1-tempmin)/(tempmax-tempmin))

    return p_music,sfreq_maps_list

#Plane live nearfied===================================================
def data_process_plane_animated_varyband_sfreqs_nf(entire_data,fc,bw,magType='linadd',theta_offset=180):
    global frequency,PLANE_LENGTH,PLANE_HEIGHT,PLANE_LENGTH_INTERVALS


    #Plotting steps===================================================

    data = entire_data
    data = data.astype(float)
    #print(np.max(data),np.min(data))
    bands_id =    list(range(len(fc))) #detect_significant_bands(bpFilt, data) #changed
    print("significant band id's: ",bands_id)
    
    p_music = np.zeros((PLANE_LENGTH_INTERVALS,PLANE_LENGTH_INTERVALS),float) #2D array #changed from ones to zeros
    p_music_temp = np.ones((PLANE_LENGTH_INTERVALS,len(bands_id),PLANE_LENGTH_INTERVALS),float) #3d array
    
    len_bands_id=len(bands_id)

    sfreq_maps_list=[]
    for k in range(len_bands_id):

        p_music_temp[::,k] = estimate_music_spectrum_2D_plane_varyband_nf(data,fc[bands_id[k]],bw,bands_id[k],theta_offset=theta_offset)

        temp1 = np.reshape(p_music_temp[::,k],(PLANE_LENGTH_INTERVALS,PLANE_LENGTH_INTERVALS)) #2d array (theta vs phi)
        if magType == "lin":
            p_music = p_music*(temp1/np.max(temp1)) #Normalization
        elif magType == "log":
            p_music = p_music+10*np.log10(temp1)/len_bands_id

        elif magType == "linadd":
            p_music = p_music+temp1/np.max(temp1)#len_bands_id
        elif magType == "linaddwithoutnorm":
            p_music = p_music+temp1#len_bands_id

        tempmax = np.max(temp1)
        tempmin = np.min(temp1)
        sfreq_maps_list.append((temp1-tempmin)/(tempmax-tempmin))
        sfreq_maps_list.append(temp1)
    return p_music,sfreq_maps_list

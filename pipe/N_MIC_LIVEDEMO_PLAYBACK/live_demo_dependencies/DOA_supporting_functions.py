import numpy as np
from scipy.signal import lfilter
import scipy as sp
#import matlab.engine
from .glob_vars import *
from scipy import signal
from .BPF import *
'''def estimate_music_spectrum_2D_plane(data,bpFilt,fc,indx,PLANE_HEIGHT,theta_offset=0): #Here, fc is frequency of the band which was selected in the above function. indx is the corresponding band index.
    global MIC_RADIUS,THETA_INTERVALS,PHI_INTERVALS, PLANE_LENGTH_INTERVALS, PLANE_LENGTH
    
    tmp1 = sp.signal.filtfilt(bpFilt[:,0],1,data[:,0],padlen=0)
    temp_data = np.zeros((len(tmp1),4), float);
    temp_data1 = np.zeros((int(len(tmp1)/2),4), complex);
    for k in range(4):
        temp_data[:,k] = sp.signal.filtfilt(bpFilt[:,indx],1,data[:,k],padlen=0) 
        temp1 = np.fft.fft(temp_data[:,k])
        temp2 = temp1[0:int(len(temp1)/2):1]
        temp_data1[:,k] = temp2

    lambda1 = SPEED_OF_SOUND/fc
    #d = 5.72e-2
    rad = MIC_RADIUS #meters
    
    R = np.matmul(np.conjugate(np.transpose(temp_data1)),temp_data1)/len(temp_data1) #temp_data1^Hermitian . temp_data1
    #print(R)
    u, s, vh = np.linalg.svd(R, full_matrices=True)
    un = u.take(np.arange(2,4,1),axis=1)

    p_music = np.ones((PLANE_LENGTH_INTERVALS,PLANE_LENGTH_INTERVALS),float)

    x_index=0
    for x_val in np.linspace(-PLANE_LENGTH/2,PLANE_LENGTH/2,PLANE_LENGTH_INTERVALS):
        x=x_val
        z=PLANE_HEIGHT#always +ve
        
        y_index = 0
        for y_val in np.linspace(-PLANE_LENGTH/2,PLANE_LENGTH/2,PLANE_LENGTH_INTERVALS):
            
            r=np.sqrt(x**2+y_val**2+z**2) #to find phi only.
            theta = np.arctan(y_val/x)
            phi = np.arccos(z/r) #always +ve

            #theta winding
            if x>=0 and y_val>=0:
                theta=theta
            elif x<0 and y_val>=0: #2nd quadrant
                theta = np.pi+theta
            elif x<0 and y_val<0: #3rd quadrant
                theta = np.pi+theta
            elif x>=0 and y_val<0:
                theta = 2*np.pi+theta


            #final payload
            A_uca = Generate_manifoldmatrix_UCA_2D(rad,theta*180/np.pi, phi*180/np.pi, lambda1,theta_offset)
            temp1 = np.matmul(np.transpose(np.conjugate(A_uca)),un)
            temp2 = np.matmul(np.transpose(np.conjugate(un)),A_uca) 
            p_music[y_index][x_index] = abs(1/np.matmul(temp1,temp2))
            
            y_index+=1
            
        x_index+=1
        
    return p_music'''



def estimate_music_spectrum_2D_pipe_another(data,bpFilt,fc,indx,theta_offset=0): #Here, fc is frequency of the band which was selected in the above function. indx is the corresponding band index.
    global MIC_RADIUS, PIPE_LENGTH,PIPE_DIAMETER,PIPE_DISTANCE,PIPE_HEIGHT,PIPE_LENGTH_INTERVALS,PIPE_DIAMETER_INTERVALS,N_MICS
    
    tmp1 = sp.signal.filtfilt(bpFilt[:,0],1,data[:,0],padlen=0)
    temp_data = np.zeros((len(tmp1),N_MICS), float);
    temp_data1 = np.zeros((int(len(tmp1)/2),N_MICS), complex);
    for k in range(N_MICS):
        temp_data[:,k] = sp.signal.filtfilt(bpFilt[:,indx],1,data[:,k],padlen=0) 
        temp1 = np.fft.fft(temp_data[:,k])
        temp2 = temp1[0:int(len(temp1)/2):1]
        temp_data1[:,k] = temp2

    lambda1 = SPEED_OF_SOUND/fc
    #d = 5.72e-2
    rad = MIC_RADIUS #meters
    
    R = np.matmul(np.conjugate(np.transpose(temp_data1)),temp_data1)/len(temp_data1) #temp_data1^Hermitian . temp_data1
    #print(R)
    u, s, vh = np.linalg.svd(R, full_matrices=True)
    un = u.take(np.arange(2,N_MICS,1),axis=1) #was 2,4,1

    p_music = np.ones((PIPE_LENGTH_INTERVALS,PIPE_DIAMETER_INTERVALS),float)

    z_index=0
    for z in np.linspace(PIPE_HEIGHT-40,PIPE_HEIGHT+40,PIPE_DIAMETER_INTERVALS):
    #for z in np.linspace(0,1000,PIPE_DIAMETER_INTERVALS):
        y_index = 0
        for y_val in np.linspace(PIPE_LENGTH/2,-PIPE_LENGTH/2,PIPE_LENGTH_INTERVALS):
            
            x=PIPE_DISTANCE
            r=np.sqrt(x**2+y_val**2+z**2) #to find phi only.
            theta = np.arctan(y_val/x)
            phi = np.arccos(z/r) #always +ve

            #theta winding
            if x>=0 and y_val>=0:
                theta=theta
            elif x<0 and y_val>=0: #2nd quadrant
                theta = np.pi+theta
            elif x<0 and y_val<0: #3rd quadrant
                theta = np.pi+theta
            elif x>=0 and y_val<0:
                theta = 2*np.pi+theta


            #final payload
            A_uca = Generate_manifoldmatrix_UCA_2D(rad,theta*180/np.pi, phi*180/np.pi, lambda1,theta_offset)
            temp1 = np.matmul(np.transpose(np.conjugate(A_uca)),un)
            temp2 = np.matmul(np.transpose(np.conjugate(un)),A_uca) 
            p_music[y_index][z_index] = abs(1/np.matmul(temp1,temp2))
            
            y_index+=1
            
        z_index+=1
        
    return p_music

def estimate_music_spectrum_2D_pipe_varyband(data,fc,bw,indx,theta_offset=0): #Here, fc is frequency of the band which was selected in the above function. indx is the corresponding band index.
    global MIC_RADIUS, PIPE_LENGTH,PIPE_DIAMETER,PIPE_DISTANCE,PIPE_HEIGHT,PIPE_LENGTH_INTERVALS,PIPE_DIAMETER_INTERVALS,N_MICS
    tmp1 = butter_bandpass_filter(data[:,0],fc-bw/2, fc+bw/2, SAMPLING_RATE, order=5)
    temp_data = np.zeros((len(tmp1),N_MICS), float);
    temp_data1 = np.zeros((int(len(tmp1)/2),N_MICS), complex);
    for k in range(N_MICS):
        temp_data[:,k] = butter_bandpass_filter(data[:,k],fc-bw/2, fc+bw/2, SAMPLING_RATE, order=5)
        temp1 = np.fft.fft(temp_data[:,k])
        temp2 = temp1[0:int(len(temp1)/2):1]
        temp_data1[:,k] = temp2

    lambda1 = SPEED_OF_SOUND/fc
    #d = 5.72e-2
    rad = MIC_RADIUS #meters
    
    R = np.matmul(np.conjugate(np.transpose(temp_data1)),temp_data1)/len(temp_data1) #temp_data1^Hermitian . temp_data1
    #print(R)
    u, s, vh = np.linalg.svd(R, full_matrices=True)
    un = u.take(np.arange(2,N_MICS,1),axis=1) #was 2,4,1

    p_music = np.ones((PIPE_LENGTH_INTERVALS,PIPE_DIAMETER_INTERVALS),float)

    z_index=0
    for z in np.linspace(PIPE_HEIGHT+PIPE_DIAMETER/2,PIPE_HEIGHT-PIPE_DIAMETER/2,PIPE_DIAMETER_INTERVALS): #ALPHA
    #for z in np.linspace(0,1000,PIPE_DIAMETER_INTERVALS):
        y_index = 0
        for y_val in np.linspace(PIPE_LENGTH/2,-PIPE_LENGTH/2,PIPE_LENGTH_INTERVALS): #BETA
            
            x=PIPE_DISTANCE
            r=np.sqrt(x**2+y_val**2+z**2) #to find phi only.
            theta = np.arctan(y_val/x)
            phi = np.arccos(z/r) #always +ve

            #theta winding
            if x>=0 and y_val>=0:
                theta=theta
            elif x<0 and y_val>=0: #2nd quadrant
                theta = np.pi+theta
            elif x<0 and y_val<0: #3rd quadrant
                theta = np.pi+theta
            elif x>=0 and y_val<0:
                theta = 2*np.pi+theta


            #final payload
            A_uca = Generate_manifoldmatrix_UCA_2D(rad,theta*180/np.pi, phi*180/np.pi, lambda1,theta_offset)
            temp1 = np.matmul(np.transpose(np.conjugate(A_uca)),un)
            temp2 = np.matmul(np.transpose(np.conjugate(un)),A_uca) 
            p_music[y_index][z_index] = abs(1/np.matmul(temp1,temp2))
            
            y_index+=1
            
        z_index+=1
        
    return p_music

def estimate_music_spectrum_2D(data,bpFilt,fc,indx,theta_offset=0): #Here, fc is frequency of the band which was selected in the above function. indx is the corresponding band index.
    global THETA_INTERVALS,PHI_INTERVALS, MIC_RADIUS    
    tmp1 = sp.signal.filtfilt(bpFilt[:,0],1,data[:,0],padlen=0)
    temp_data = np.zeros((len(tmp1),N_MICS), float);
    temp_data1 = np.zeros((int(len(tmp1)/2),N_MICS), complex);
    for k in range(N_MICS):
        temp_data[:,k] = sp.signal.filtfilt(bpFilt[:,indx],1,data[:,k],padlen=0) 
        temp1 = np.fft.fft(temp_data[:,k])
        temp2 = temp1[0:int(len(temp1)/2):1]
        temp_data1[:,k] = temp2

    lambda1 = SPEED_OF_SOUND/fc
    #d = 5.72e-2
    rad = MIC_RADIUS #meters
    
    R = np.matmul(np.conjugate(np.transpose(temp_data1)),temp_data1)/len(temp_data1) #temp_data1^Hermitian . temp_data1
    #print(R)
    u, s, vh = np.linalg.svd(R, full_matrices=True)
    un = u.take(np.arange(2,N_MICS,1),axis=1)

    p_music = np.ones((THETA_INTERVALS,PHI_INTERVALS),float)
    
    #p_music_max=-np.inf
    theta_index= 0
    for theta in np.linspace(0,360,THETA_INTERVALS):
        phi_index = 0
        for phi in np.linspace(0,90,PHI_INTERVALS):
            A_uca = Generate_manifoldmatrix_UCA_2D(rad,theta, phi, lambda1,theta_offset)
            temp1 = np.matmul(np.transpose(np.conjugate(A_uca)),un)
            temp2 = np.matmul(np.transpose(np.conjugate(un)),A_uca) 
            p_music[theta_index][phi_index] = abs(1/np.matmul(temp1,temp2))

            #if p_music[theta_index][phi_index]>p_music_max: p_music_max=p_music[theta_index][phi_index]

            
            phi_index+=1
        theta_index+=1
        
    return p_music

def estimate_music_spectrum_2D_cylinder_nf(data,bpFilt,fc,indx,theta_offset=0): #Here, fc is frequency of the band which was selected in the above function. indx is the corresponding band index.
    global MIC_RADIUS,THETA_INTERVALS,PHI_INTERVALS, CYLINDER_Y_INTERVALS, CYLINDER_DELTA_INTERVALS, CYLINDER_HEIGHT, CYLINDER_RADIUS, CYLINDER_LENGTH, CYLINDER_CHI
    
    tmp1 = sp.signal.filtfilt(bpFilt[:,0],1,data[:,0],padlen=0)
    temp_data = np.zeros((len(tmp1),6), float);
    temp_data1 = np.zeros((int(len(tmp1)/2),6), complex);
    for k in range(6):
        temp_data[:,k] = sp.signal.filtfilt(bpFilt[:,indx],1,data[:,k],padlen=0) 
        temp1 = np.fft.fft(temp_data[:,k])
        temp2 = temp1[0:int(len(temp1)/2):1]
        temp_data1[:,k] = temp2

    lambda1 = SPEED_OF_SOUND/fc
    #d = 5.72e-2
    rad = MIC_RADIUS # radius is taken as 50mm 
    
    R = np.matmul(np.conjugate(np.transpose(temp_data1)),temp_data1)/len(temp_data1) #temp_data1^Hermitian . temp_data1
    #print(R)
    u, s, vh = np.linalg.svd(R, full_matrices=True)
    un = u.take(np.arange(2,6,1),axis=1)

    p_music = np.ones((CYLINDER_Y_INTERVALS,CYLINDER_DELTA_INTERVALS),float)

    for delta_index in range(CYLINDER_DELTA_INTERVALS):
        for y_index in range(CYLINDER_Y_INTERVALS):
            A_uca = Generate_manifoldmatrix_UCA_2D_cyl_nf(rad, y_index, delta_index, lambda1)
            temp1 = np.matmul(np.transpose(np.conjugate(A_uca)),un)
            temp2 = np.matmul(np.transpose(np.conjugate(un)),A_uca) 
            p_music[y_index][delta_index] = abs(1/np.matmul(temp1,temp2))
            
    return p_music

def Generate_manifoldmatrix_UCA_2D(R,theta, phi, lambda1, theta_offset=0):
    A=[]

    N_MICS_EVEN = N_MICS
    if N_MICS%2 != 0: #if odd mics
        N_MICS_EVEN= N_MICS-1

    for mic_index in range(N_MICS_EVEN):
        A.append( np.exp(1j*(2*np.pi/lambda1)*R*( np.cos((theta-theta_offset)*np.pi/180-(-2*np.pi*mic_index/N_MICS_EVEN) ) * np.sin(phi*np.pi/180) ) ) )

    if N_MICS_EVEN != N_MICS:
        A.append(1) #If odd mics, last mic is at centre. Therefore, its steering vector is unity.
    return np.array(A)

def Generate_manifoldmatrix_UCA_2D_cyl_nf(R, y_index, delta_index, lambda1):
    A=[]
    #reference_rad = CYL_NF_R_LUT[4][y_index][delta_index] #use instead of R
    reference_rad = MIC_CENTRE_R_LUT[y_index][delta_index] #use instead of R
    for mic_index in range(6):
        theta = CYL_NF_THETA_LUT[mic_index][y_index][delta_index]
        phi = CYL_NF_PHI_LUT[mic_index][y_index][delta_index]
        local_rad = CYL_NF_R_LUT[mic_index][y_index][delta_index] #use instead of R
        #A.append( np.exp(1j*(2*np.pi/lambda1)*   R   *( np.cos((theta))* np.sin(phi) ) ) ) #No near field assumptions except theta and phi
        A.append( reference_rad/local_rad*np.exp(1j*(2*np.pi/lambda1)*   (local_rad-reference_rad)   *( np.cos((theta))* np.sin(phi) ) ) ) #as per paper #attempt 1 folder
        #A.append( reference_rad/local_rad*np.exp(1j*(2*np.pi/lambda1)*   abs(local_rad-reference_rad)   *( np.cos((theta))* np.sin(phi) ) ) ) #abs of path difference
        #A.append( CYLINDER_HEIGHT_METERS/local_rad*np.exp(1j*(2*np.pi/lambda1)*   (local_rad-CYLINDER_HEIGHT_METERS)   *( np.cos((theta))* np.sin(phi) ) ) ) #something else which we will try #attempt 2 folder

    return np.array(A)

def estimate_music_spectrum_2D_plane_another(data,bpFilt,fc,indx,theta_offset=0): #Here, fc is frequency of the band which was selected in the above function. indx is the corresponding band index.
    global MIC_RADIUS, PLANE_LENGTH,PLANE_HEIGHT,PLANE_LENGTH_INTERVALS,N_MICS
    
    tmp1 = sp.signal.filtfilt(bpFilt[:,0],1,data[:,0],padlen=0)
    temp_data = np.zeros((len(tmp1),N_MICS), float);
    temp_data1 = np.zeros((int(len(tmp1)/2),N_MICS), complex);
    for k in range(N_MICS):
        temp_data[:,k] = sp.signal.filtfilt(bpFilt[:,indx],1,data[:,k],padlen=0) 
        temp1 = np.fft.fft(temp_data[:,k])
        temp2 = temp1[0:int(len(temp1)/2):1]
        temp_data1[:,k] = temp2

    lambda1 = SPEED_OF_SOUND/fc
    #d = 5.72e-2
    rad = MIC_RADIUS #meters
    
    R = np.matmul(np.conjugate(np.transpose(temp_data1)),temp_data1)/len(temp_data1) #temp_data1^Hermitian . temp_data1
    #print(R)
    u, s, vh = np.linalg.svd(R, full_matrices=True)
    un = u.take(np.arange(2,N_MICS,1),axis=1) #was 2,4,1

    p_music = np.ones((PLANE_LENGTH_INTERVALS,PLANE_LENGTH_INTERVALS),float)

    x_index=0
    for x_val in np.linspace(-PLANE_LENGTH/2,PLANE_LENGTH/2,PLANE_LENGTH_INTERVALS):
        x=x_val
        z=PLANE_HEIGHT#always +ve
        
        y_index = 0
        for y_val in np.linspace(-PLANE_LENGTH/2,PLANE_LENGTH/2,PLANE_LENGTH_INTERVALS):
            
            r=np.sqrt(x**2+y_val**2+z**2) #to find phi only.
            theta = np.arctan(y_val/x)
            phi = np.arccos(z/r) #always +ve

            #theta winding
            if x>=0 and y_val>=0:
                theta=theta
            elif x<0 and y_val>=0: #2nd quadrant
                theta = np.pi+theta
            elif x<0 and y_val<0: #3rd quadrant
                theta = np.pi+theta
            elif x>=0 and y_val<0:
                theta = 2*np.pi+theta


            #final payload
            A_uca = Generate_manifoldmatrix_UCA_2D(rad,theta*180/np.pi, phi*180/np.pi, lambda1,theta_offset)
            temp1 = np.matmul(np.transpose(np.conjugate(A_uca)),un)
            temp2 = np.matmul(np.transpose(np.conjugate(un)),A_uca) 
            p_music[y_index][x_index] = abs(1/np.matmul(temp1,temp2))
            
            y_index+=1
            
        x_index+=1
        
    return p_music

def estimate_music_spectrum_2D_plane_varyband(data,fc,bw,indx,theta_offset=0): #Here, fc is frequency of the band which was selected in the above function. indx is the corresponding band index.
    global MIC_RADIUS, PLANE_LENGTH,PLANE_HEIGHT,PLANE_LENGTH_INTERVALS,N_MICS
    tmp1 = butter_bandpass_filter(data[:,0],fc-bw/2, fc+bw/2, SAMPLING_RATE, order=5)
    temp_data = np.zeros((len(tmp1),N_MICS), float);
    temp_data1 = np.zeros((int(len(tmp1)/2),N_MICS), complex);
    for k in range(N_MICS):
        temp_data[:,k] = butter_bandpass_filter(data[:,k],fc-bw/2, fc+bw/2, SAMPLING_RATE, order=5)
        temp1 = np.fft.fft(temp_data[:,k])
        temp2 = temp1[0:int(len(temp1)/2):1]
        temp_data1[:,k] = temp2

    lambda1 = SPEED_OF_SOUND/fc
    #d = 5.72e-2
    rad = MIC_RADIUS #meters
    
    R = np.matmul(np.conjugate(np.transpose(temp_data1)),temp_data1)/len(temp_data1) #temp_data1^Hermitian . temp_data1
    #print(R)
    u, s, vh = np.linalg.svd(R, full_matrices=True)
    un = u.take(np.arange(2,N_MICS,1),axis=1) #was 2,4,1

    p_music = np.ones((PLANE_LENGTH_INTERVALS,PLANE_LENGTH_INTERVALS),float)

    x_index=0
    for x_val in np.linspace(-PLANE_LENGTH/2,PLANE_LENGTH/2,PLANE_LENGTH_INTERVALS):
        x=x_val
        z=PLANE_HEIGHT#always +ve
        
        y_index = 0
        for y_val in np.linspace(-PLANE_LENGTH/2,PLANE_LENGTH/2,PLANE_LENGTH_INTERVALS):
            
            r=np.sqrt(x**2+y_val**2+z**2) #to find phi only.
            theta = np.arctan(y_val/x)
            phi = np.arccos(z/r) #always +ve

            #theta winding
            if x>=0 and y_val>=0:
                theta=theta
            elif x<0 and y_val>=0: #2nd quadrant
                theta = np.pi+theta
            elif x<0 and y_val<0: #3rd quadrant
                theta = np.pi+theta
            elif x>=0 and y_val<0:
                theta = 2*np.pi+theta


            #final payload
            A_uca = Generate_manifoldmatrix_UCA_2D(rad,theta*180/np.pi, phi*180/np.pi, lambda1,theta_offset)
            temp1 = np.matmul(np.transpose(np.conjugate(A_uca)),un)
            temp2 = np.matmul(np.transpose(np.conjugate(un)),A_uca) 
            p_music[y_index][x_index] = abs(1/np.matmul(temp1,temp2))
            
            y_index+=1
            
        x_index+=1
        
    return p_music


#Near field plane==========================================================================
def Generate_manifoldmatrix_UCA_2D_plane_nf(R, y_index, x_index, lambda1):
    A=[]
    #reference_rad = CYL_NF_R_LUT[4][y_index][delta_index] #use instead of R
    reference_rad = PLANE_MIC_CENTRE_R_LUT[y_index][x_index] #use instead of R
    for mic_index in range(N_MICS):
        theta = PLANE_NF_THETA_LUT[mic_index][y_index][x_index]
        phi = PLANE_NF_PHI_LUT[mic_index][y_index][x_index]
        local_rad = PLANE_NF_R_LUT[mic_index][y_index][x_index] #use instead of R
        #A.append( np.exp(1j*(2*np.pi/lambda1)*   R   *( np.cos((theta))* np.sin(phi) ) ) ) #No near field assumptions except theta and phi
        #A.append( reference_rad/local_rad*np.exp(1j*(2*np.pi/lambda1)*   (local_rad-reference_rad)   *( np.cos((theta))* np.sin(phi) ) ) ) #as per paper #attempt 1 folder
        #A.append( reference_rad/local_rad*np.exp(1j*(2*np.pi/lambda1)*   abs(local_rad-reference_rad)   *( np.cos((theta))* np.sin(phi) ) ) ) #abs of path difference
        #A.append( CYLINDER_HEIGHT_METERS/local_rad*np.exp(1j*(2*np.pi/lambda1)*   (local_rad-CYLINDER_HEIGHT_METERS)   *( np.cos((theta))* np.sin(phi) ) ) ) #something else which we will try #attempt 2 folder
        A.append( np.exp(1j*(2*np.pi/lambda1)*   (reference_rad-local_rad) ) ) #as per paper #attempt 1 folder

        #print(reference_rad-local_rad)

    return np.array(A)


def estimate_music_spectrum_2D_plane_varyband_nf(data,fc,bw,indx,theta_offset=0): #Here, fc is frequency of the band which was selected in the above function. indx is the corresponding band index.
    global MIC_RADIUS, PLANE_LENGTH,PLANE_HEIGHT,PLANE_LENGTH_INTERVALS,N_MICS
    tmp1 = butter_bandpass_filter(data[:,0],fc-bw/2, fc+bw/2, SAMPLING_RATE, order=5)
    temp_data = np.zeros((len(tmp1),N_MICS), float);
    temp_data1 = np.zeros((int(len(tmp1)/2),N_MICS), complex);
    for k in range(N_MICS):
        temp_data[:,k] = butter_bandpass_filter(data[:,k],fc-bw/2, fc+bw/2, SAMPLING_RATE, order=5)
        temp1 = np.fft.fft(temp_data[:,k])
        temp2 = temp1[0:int(len(temp1)/2):1]
        temp_data1[:,k] = temp2

    lambda1 = SPEED_OF_SOUND/fc
    #d = 5.72e-2
    rad = MIC_RADIUS #meters
    
    R = np.matmul(np.conjugate(np.transpose(temp_data1)),temp_data1)/len(temp_data1) #temp_data1^Hermitian . temp_data1
    #print(R)
    u, s, vh = np.linalg.svd(R, full_matrices=True)
    un = u.take(np.arange(2,N_MICS,1),axis=1) #was 2,4,1

    p_music = np.ones((PLANE_LENGTH_INTERVALS,PLANE_LENGTH_INTERVALS),float)

    x_index=0
    for x_val in np.linspace(-PLANE_LENGTH/2,PLANE_LENGTH/2,PLANE_LENGTH_INTERVALS):
        x=x_val
        z=PLANE_HEIGHT#always +ve
        
        y_index = 0
        for y_val in np.linspace(-PLANE_LENGTH/2,PLANE_LENGTH/2,PLANE_LENGTH_INTERVALS):
            
            r=np.sqrt(x**2+y_val**2+z**2) #to find phi only.
            theta = np.arctan(y_val/x)
            phi = np.arccos(z/r) #always +ve

            #theta winding
            if x>=0 and y_val>=0:
                theta=theta
            elif x<0 and y_val>=0: #2nd quadrant
                theta = np.pi+theta
            elif x<0 and y_val<0: #3rd quadrant
                theta = np.pi+theta
            elif x>=0 and y_val<0:
                theta = 2*np.pi+theta


            #final payload
            A_uca = Generate_manifoldmatrix_UCA_2D_plane_nf(rad,y_index, x_index, lambda1)
            temp1 = np.matmul(np.transpose(np.conjugate(A_uca)),un)
            temp2 = np.matmul(np.transpose(np.conjugate(un)),A_uca) 
            p_music[y_index][x_index] = abs(1/np.matmul(temp1,temp2))
            
            y_index+=1
            
        x_index+=1
        
    return p_music

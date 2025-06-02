import numpy as np
from matplotlib import pyplot as plt
SAMPLING_RATE = 48000
MIC_RADIUS_CM = 5 #cm
N_MICS = 9#9
THETA_OFFSET = 180 #To correct any azimuth DC errors.
MIC_ROT=0 #Use this in case mic is rotated relative to its own frame of reference.

THETA_INTERVALS = 50#361 #361
PHI_INTERVALS = 30#91#91

#PLANE========================
PLANE_HEIGHT = 30#66 #66 for metal plate (mic aboe that cardboard box), 30 for ball mill
PLANE_LENGTH= 16#70#cm #16 for ball mill, 70 for metal plate, 90 for motor
PLANE_LENGTH_INTERVALS=30 #30#100 #30 for plane, 60 for motor, 30 for ball mill

#PIPE=========================
PIPE_LENGTH = 315 #cm 315
PIPE_DIAMETER = 400 #cm 20
PIPE_DISTANCE = 150#150#255,150
PIPE_HEIGHT = 46#cm 44.5
PIPE_LENGTH_INTERVALS = 50 #100real
PIPE_DIAMETER_INTERVALS = 5      #10real

#CYLINDER=====================
CYLINDER_HEIGHT = 12#12 cm #10cm for ball mill exp1, 28.5-4.5 for kgp ball mill jul24
CYLINDER_RADIUS = 7#cm #7cm for ball mill exp1, 33/2 for kgp ball mill jul24
CYLINDER_LENGTH = 25#19 #cm #19 for ball mill exp1, 45 for kgp ball mill exp2
CYLINDER_CHI = 45 #np.arccos(CYLINDER_RADIUS/(CYLINDER_RADIUS+CYLINDER_HEIGHT))
CYLINDER_X_OFFSET = -2 #cm #-2 for ball mill exp1, 0 for kgp ball mill exp2
CYLINDER_CHI_OFFSET= 45#CYLINDER_CHI #30*np.pi/180 

CYLINDER_Y_INTERVALS = 50
CYLINDER_DELTA_INTERVALS = 50
SPEED_OF_SOUND = 340 #ms-1


#ground to mic: 22.5cm
#ground to pipe: 67cm

#DO NOT CHANGE THESE=======================================================
#==========================================================================
MIC_RADIUS = MIC_RADIUS_CM/100 #meters
CYLINDER_HEIGHT_METERS = CYLINDER_HEIGHT/100#m
CYLINDER_RADIUS_METERS = CYLINDER_RADIUS/100 #m
CYLINDER_LENGTH_METERS = CYLINDER_LENGTH/100 #m

#TODO========================================================
#Near field LUT's for cylindrical surface
CYL_NF_THETA_LUT = np.ones((N_MICS,CYLINDER_Y_INTERVALS,CYLINDER_DELTA_INTERVALS),float)
CYL_NF_PHI_LUT = np.ones((N_MICS,CYLINDER_Y_INTERVALS,CYLINDER_DELTA_INTERVALS),float)
CYL_NF_R_LUT= np.ones((N_MICS,CYLINDER_Y_INTERVALS,CYLINDER_DELTA_INTERVALS),float)
MIC_CENTRE_R_LUT=np.ones((CYLINDER_Y_INTERVALS,CYLINDER_DELTA_INTERVALS),float)

for i in range(N_MICS): #i = mic index

    N_MICS_EVEN = N_MICS-1 if N_MICS%2 !=0 else N_MICS
    #Determine mic position
    mic_angle = -i/N_MICS_EVEN*np.pi*2 + MIC_ROT*np.pi/180 + THETA_OFFSET*np.pi/180#Mics are placed anti clockwise.
    mic_x = MIC_RADIUS*np.cos(mic_angle) if (N_MICS_EVEN == N_MICS and i== N_MICS-1) else 0
    mic_y = MIC_RADIUS*np.sin(mic_angle) if (N_MICS_EVEN == N_MICS and i== N_MICS-1) else 0

    #determine cylinder x,y,z from cylinder coordinates
    delta_index=0
    for delta_val in np.linspace(-np.pi/2-CYLINDER_CHI+CYLINDER_CHI_OFFSET,-np.pi/2+CYLINDER_CHI+CYLINDER_CHI_OFFSET,CYLINDER_DELTA_INTERVALS):
        cyl_x=CYLINDER_RADIUS_METERS*np.cos(delta_val) + CYLINDER_X_OFFSET#+-ve
        cyl_z=CYLINDER_HEIGHT_METERS+CYLINDER_RADIUS_METERS*(1+np.sin(delta_val)) #always +ve

        #Find relative cyl x,z
        x=cyl_x-mic_x
        z=cyl_z-0 #mic z is always 0
        
        y_index = 0
        for y_val in np.linspace(-CYLINDER_LENGTH_METERS/2,CYLINDER_LENGTH_METERS/2,CYLINDER_Y_INTERVALS):
            cyl_y=y_val

            #Find relative cyl_y
            y=cyl_y-mic_y
            
            r=np.sqrt(x**2+y**2+z**2) #to find phi only.
            theta = np.arctan(y/x)
            phi = np.arccos(z/r) #always +ve

            #theta winding
            if x>=0 and y>=0:
                theta=theta
            elif x<0 and y>=0: #2nd quadrant
                theta = np.pi+theta
            elif x<0 and y<0: #3rd quadrant
                theta = np.pi+theta
            elif x>=0 and y<0:
                theta = 2*np.pi+theta

            #Fill the LUT's
            CYL_NF_THETA_LUT[i][y_index][delta_index]=theta-mic_angle
            CYL_NF_PHI_LUT[i][y_index][delta_index]=phi
            CYL_NF_R_LUT[i][y_index][delta_index]=r
            if i==0:
                MIC_CENTRE_R_LUT[y_index][delta_index]=np.sqrt(cyl_x**2+cyl_y**2+cyl_z**2)
            y_index+=1
        delta_index+=1


#TODO========================================================
#Near field LUT's for plane surface
PLANE_NF_THETA_LUT = np.ones((N_MICS,PLANE_LENGTH_INTERVALS,PLANE_LENGTH_INTERVALS),float)
PLANE_NF_PHI_LUT = np.ones((N_MICS,PLANE_LENGTH_INTERVALS,PLANE_LENGTH_INTERVALS),float)
PLANE_NF_R_LUT= np.ones((N_MICS,PLANE_LENGTH_INTERVALS,PLANE_LENGTH_INTERVALS),float) #in meters
PLANE_MIC_CENTRE_R_LUT=np.ones((PLANE_LENGTH_INTERVALS,PLANE_LENGTH_INTERVALS),float) #in meters

PLANE_HEIGHT_METERS = PLANE_HEIGHT/100#meters
PLANE_LENGTH_METERS = PLANE_LENGTH/100 #meters

for i in range(N_MICS): #i = mic index

    N_MICS_EVEN = N_MICS-1 if N_MICS%2 !=0 else N_MICS
    #Determine mic position
    mic_angle = -i/N_MICS_EVEN*np.pi*2 + MIC_ROT*np.pi/180 + THETA_OFFSET*np.pi/180#Mics are placed anti clockwise.
    #If odd mics
    if N_MICS_EVEN != N_MICS:
        if i!=N_MICS-1:
            mic_x = MIC_RADIUS*np.cos(mic_angle)
            mic_y = MIC_RADIUS*np.sin(mic_angle)

        else:
            mic_x=0
            mic_y=0
    else:
        mic_x = MIC_RADIUS*np.cos(mic_angle)
        mic_y = MIC_RADIUS*np.sin(mic_angle)
    #mic_x = MIC_RADIUS*np.cos(mic_angle) if (N_MICS_EVEN != N_MICS and i< N_MICS-1) else 0
    #mic_y = MIC_RADIUS*np.sin(mic_angle) if (N_MICS_EVEN != N_MICS and i< N_MICS-1) else 0
    print(mic_x,mic_y)

    #determine cylinder x,y,z from cylinder coordinates
    x_index=0
    for x_val in np.linspace(-PLANE_LENGTH_METERS/2,PLANE_LENGTH_METERS/2,PLANE_LENGTH_INTERVALS):

        #Find relative cyl x,z
        x=x_val-mic_x
        z=PLANE_HEIGHT_METERS-0 #mic z is always 0
        
        y_index = 0
        for y_val in np.linspace(-PLANE_LENGTH_METERS/2,PLANE_LENGTH_METERS/2,PLANE_LENGTH_INTERVALS):

            y=y_val-mic_y
            
            r=np.sqrt(x**2+y**2+z**2) #to find phi only.
            theta = np.arctan(y/x)
            phi = np.arccos(z/r) #always +ve

            #theta winding
            if x>=0 and y>=0:
                theta=theta
            elif x<0 and y>=0: #2nd quadrant
                theta = np.pi+theta
            elif x<0 and y<0: #3rd quadrant
                theta = np.pi+theta
            elif x>=0 and y<0:
                theta = 2*np.pi+theta

            #Fill the LUT's
            PLANE_NF_THETA_LUT[i][y_index][x_index]=theta-mic_angle
            PLANE_NF_PHI_LUT[i][y_index][x_index]=phi
            PLANE_NF_R_LUT[i][y_index][x_index]=r
            if i==0:
                PLANE_MIC_CENTRE_R_LUT[y_index][x_index]=np.sqrt(x_val**2+y_val**2+PLANE_HEIGHT_METERS**2)
            y_index+=1
        x_index+=1

#plt.figure()
#plt.imshow(PLANE_NF_R_LUT[8])
#plt.figure()
#plt.imshow(PLANE_MIC_CENTRE_R_LUT)
#plt.show()

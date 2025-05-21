import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from numpy import random
from random import randrange
import numpy as np

import sounddevice as sd
import librosa
import threading
import time

from live_demo_dependencies.DOA_supporting_functions import *
from live_demo_dependencies.generate_bpfilt import *
from live_demo_dependencies.glob_vars import *
from live_demo_dependencies.doa_data_process import *
from live_demo_dependencies.BPF import *
from live_demo_dependencies.dmas import *
import pickle

#========================================
frequency= SAMPLING_RATE # Frequency of the input data
LOOP_LENGTH = 1 #Time length of a captured audio frame #seconds
AUDIO_SIZE_REDUCTION_FACTOR = 4 #By how much factor you want to slice the captured audio frame from the beginning, before further processing

current_freq=4500#Hz #5000 , #4500 for 1.5m, 5000 for 2m

BAND_DISTANCE = 400 #Hz #Band distance for wideband MUSIC
FREQUENCY_FILTERING_ON = True
RPI_INTERFACING_ENABLED = True
fc,bw = generate_bpfilt_varyband(BAND_DISTANCE=BAND_DISTANCE,R_b=SAMPLING_RATE,lower_freq=1000,upper_freq=7000,tapered=True)

#BAND_DISTANCE = 200 #Hz
#fc,bw = generate_bpfilt_varyband(BAND_DISTANCE=BAND_DISTANCE,R_b=SAMPLING_RATE,lower_freq=2000,upper_freq=5000,tapered=True)
#========================================


# Remote GPIO setup
rpi_ip='192.168.115.248'# Replace with your Raspberry Pi's IP address #If ip address on this system is 192.168.x.y , replace the third number of rpi_ip with x.
button_pins = [22, 27, 17]  # Pins at which solenoid valves have been connected.

if RPI_INTERFACING_ENABLED:

    from gpiozero import LED
    from gpiozero.pins.pigpio import PiGPIOFactory
    factory = PiGPIOFactory(host=rpi_ip)
    leds = [LED(pin, pin_factory=factory) for pin in button_pins]

'''def get_image_matrix():
    # Dummy function to generate random image matrix
    return np.random.rand(10, 100)'''

def get_angles_from_pixels_pipe(cursor_x,cursor_y):
    global PIPE_LENGTH, PIPE_LENGTH_INTERVALS, PIPE_DIAMETER, PIPE_DIAMETER_INTERVALS
    y_val = PIPE_LENGTH*(0.5-cursor_x/(PIPE_LENGTH_INTERVALS-1)) #change sign of PIPE_LENGTH if you flip the plot horizontally in DOA_supporting_functions.py comment BETA
    z = PIPE_HEIGHT-PIPE_DIAMETER*(cursor_y/(PIPE_DIAMETER_INTERVALS-1)-0.5) #change sign of PIPE_DIAMETER if you flip the plot vertically in DOA_supporting_functions.py comment ALPHA
    x = PIPE_DISTANCE

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

    return theta*180/np.pi,phi*180/np.pi

def get_image_matrix_sfreqs(audio_data):
    t=time.time()
    #find pmusic composite map and single frequency maps
    p_music,sfreq_maps=data_process_pipe_animated_varyband_sfreqs(audio_data,fc,bw,magType='linadd',theta_offset=180)
    print("pmusic time:",time.time()-t)

    #Normalize pmusic
    minval  = np.min(p_music)
    maxval= np.max(p_music)
    p_music = (p_music-minval)/(maxval-minval)
    
    return p_music.T, sfreq_maps

def get_audio_data():
    pkl_file = open('pickles/audio_file.pkl', 'rb') #Change pickle filename here. If live data capture is taking place, filename = audio_file.pkl
    #pkl_file = open('pickles/pipe_leak_and_motor.pkl', 'rb') #Change pickle filename here. If live data capture is taking place, filename = audio_file.pkl
    audio_data = pickle.load(pkl_file)
    pkl_file.close()

    #Shorten audio for better time complexity.
    size_reduction_factor = AUDIO_SIZE_REDUCTION_FACTOR
    audiolen_samples = len(audio_data[:,0])
    audio_data = audio_data[:int(audiolen_samples/size_reduction_factor)]

    return audio_data

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Live Demo")
        self.geometry("800x600")

        #Setting title
        self.title_label = ttk.Label(self, text="2D Beamforming Localization Live Demo v2.6", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        #Buttons for controlling solenoid valves
        self.buttons_frame = ttk.Frame(self)
        self.buttons_frame.pack(pady=20)

        self.buttons = []
        for i in range(3):
            button = ttk.Button(self.buttons_frame, text=f"Button {i+1}", command=lambda i=i: self.toggle_button(i))
            button.grid(row=0, column=i, padx=10)
            self.buttons.append(button)

        button = ttk.Button(self.buttons_frame, text=f"RANDOM", command=lambda i=3: self.toggle_button(i))
        button.grid(row=0, column=3, padx=10)
        self.buttons.append(button)

        # Image=============================================================
        self.default_image = Image.open("pipe_leakage/pipe_default.png")
        self.images = [Image.open(f"pipe_leakage/pipe_leak_{i+1}.png") for i in range(3)]
        self.current_image = ImageTk.PhotoImage(self.default_image)
        self.image_label = ttk.Label(self, image=self.current_image)
        self.image_label.pack(pady=20)

        #audio data========================================================
        self.audio_data = get_audio_data()

        #Audio playback management 
        self.audio_slice = self.audio_data[:,0]
        self.buffer = np.zeros(5*SAMPLING_RATE)
        
        # Plot============================================================
        self.fig, self.ax = plt.subplots()
        self.fig.set_size_inches(10, 80)  # New size in inches
        self.new_matrix,self.sfreq_maps = get_image_matrix_sfreqs(self.audio_data)
        
        self.music_image = self.ax.imshow(self.new_matrix, cmap='jet')
        #self.colorbar = plt.colorbar(self.music_image, ax=self.ax)

        # Set the figure background to transparent
        self.fig.patch.set_alpha(0.0)
        # Set the axes background to transparent
        self.ax.patch.set_alpha(0.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.mpl_connect('motion_notify_event', self.update_cursor)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=10)
        self.current_button = None

        #Mouse=============================================================
        #mouse coordinates
        self.cursor_x = -1
        self.cursor_y = -1
        #intensity of pmusic at given mouse coordinates.
        self.intensity = 1
        self.sfreqs_intensity = [1]*len(fc)

        
        #Audio thread======================================================

        self.audio_thread = threading.Thread(target=self.audio_playback, daemon=True)
        self.audio_thread.start()    

        self.update_plot()
        
    def toggle_button(self, index):
        # Toggle GPIO pin
        if index !=3:
            if RPI_INTERFACING_ENABLED:
                led = leds[index]
                led.toggle()

            # Toggle image
            if self.current_button == index:
                self.current_image = ImageTk.PhotoImage(self.default_image)
                self.current_button = None
            else:
                self.current_image = ImageTk.PhotoImage(self.images[index])
                self.current_button = index

            self.image_label.config(image=self.current_image)
        else:
            
            if self.current_button!=None:
                if RPI_INTERFACING_ENABLED:
                    led  = leds[self.current_button]
                    led.toggle()
                self.current_button = None
                self.current_image = ImageTk.PhotoImage(self.default_image)
            else:
                random_index = randrange(3)
                if RPI_INTERFACING_ENABLED:
                    led = leds[random_index]
                    led.toggle()
                self.current_button = random_index
                self.current_image = ImageTk.PhotoImage(self.images[random_index])
            self.image_label.config(image=self.current_image)

    def audio_callback(self,outdata, frames, time, status):

        try:
            self.audio_data = get_audio_data()
            
            
            if self.cursor_x == -1 or self.cursor_y == -1:
                self.audio_slice = self.audio_data[:,0]
                #self.audio_slice = butter_bandpass_filter(self.audio_slice,lowcut=1000, highcut=8000, fs=SAMPLING_RATE, order=5)
                
            else:
                #spatial filtering
                current_theta,current_phi=get_angles_from_pixels_pipe(self.cursor_x,self.cursor_y)
                self.audio_slice = dmas(self.audio_data, SAMPLING_RATE,current_theta, current_phi, radius=MIC_RADIUS)
                

                #Frequency filtering
                if FREQUENCY_FILTERING_ON:
                    accumulation_list = np.zeros_like(self.audio_slice)
                    for i in range(len(fc)):
                        #BPF the audio
                        nbf_audio =  butter_bandpass_filter(self.audio_slice,lowcut=fc[i]-bw/2, highcut=fc[i]+bw/2, fs=SAMPLING_RATE, order=5)
                        #multiply with the intensity of sfreq_map at current mouse coordinates.
                        nbf_audio = np.multiply(nbf_audio,self.sfreqs_intensity[i])
                        accumulation_list = np.add(accumulation_list,nbf_audio)

                    self.audio_slice = accumulation_list
                else:
                    self.audio_slice = butter_bandpass_filter(self.audio_slice,lowcut=1000, highcut=8000, fs=SAMPLING_RATE, order=5)
                    
                
        except (EOFError, pickle.UnpicklingError) as e:
            pass


        for i in range(frames):
            if self.cursor_x == -1 or self.cursor_y == -1:
                outdata[i] = self.audio_slice[i%len(self.audio_slice)]*0
            else:
                outdata[i] = self.audio_slice[i%len(self.audio_slice)]
        
    def audio_playback(self):

        stream = sd.OutputStream(callback = self.audio_callback ,
                                 samplerate = SAMPLING_RATE, channels = 1,
                                 dtype = 'float32',blocksize = int(LOOP_LENGTH*SAMPLING_RATE))
        with stream:
            sd.sleep(int(1e6))
        
    def update_plot(self):
        try:
            self.new_matrix,self.sfreq_maps = get_image_matrix_sfreqs(self.audio_data)
            self.music_image.set_data(self.new_matrix)
            self.music_image.set_clim(vmin=0,vmax=1)#(vmin=new_matrix.min(), vmax=new_matrix.max())
            #self.colorbar.remove()
            #self.colorbar = plt.colorbar(self.music_image, ax=self.ax, shrink = 0.2)
            self.canvas.draw()
        except:
            pass
        self.after(100, self.update_plot)

    def update_cursor(self,event):
        if event.inaxes is not None:
            self.cursor_x, self.cursor_y = int(event.xdata), int(event.ydata)
            self.intensity = self.new_matrix[self.cursor_y, self.cursor_x]
            self.sfreqs_intensity = [mat1[self.cursor_x, self.cursor_y] for mat1 in self.sfreq_maps]
            print(f"Cursor coordinates: ({self.cursor_x}, {self.cursor_y}), Intensity: {self.intensity}")
        else:
            self.cursor_x, self.cursor_y = -1, -1
            self.intensity = 0
            print("Cursor coordinates: (-1, -1)")

if __name__ == "__main__":
    app = App()
    app.mainloop()

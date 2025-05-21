import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import nidaqmx
from nidaqmx import constants
from nidaqmx.constants import AcquisitionType, READ_ALL_AVAILABLE, TerminalConfiguration
from nidaqmx import stream_readers
import numpy as np
import time as t
import pickle

from live_demo_dependencies.glob_vars import N_MICS
from live_demo_dependencies.glob_vars import SAMPLING_RATE

#IF PLOTTING, UNCOMMENT THESE---------------
#from matplotlib import pyplot as plt
#plt.ion

DATA_ACQ_ENABLED = True
DATA_EXPORT_ENABLED = True

output = open('pickles/audio_file.pkl', 'wb')
pickle.dump(1, output) #1 indicates file streaming not yet started
output.close()

def normalize(data):
    trace_mean = np.mean(data)
    data = [x-trace_mean for x in data]
    max_val = max(abs(min(data)), max(data))
    #print("MAXval:",max_val)
    #norm_trace= [x / max_val for x in data]
    norm_trace= [x*4 for x in data]
    return norm_trace

fs = SAMPLING_RATE
nSamples = 200
numChannels = N_MICS
totalTime = 1#0.2 #s


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DAQ acquisition")
        self.geometry("400x200")

        #Setting title
        self.title_label = ttk.Label(self, text="Data acquisition", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        #Buttons for controlling solenoid valves
        self.buttons_frame = ttk.Frame(self)
        self.buttons_frame.pack(pady=20)

        self.buttons = []
        button_name_list = ['DATA SAVE ON','DATA SAVE OFF']
        for i in range(2):
            button = ttk.Button(self.buttons_frame, text=button_name_list[i], command=lambda i=i: self.toggle_button(i))
            button.grid(row=0, column=i, padx=10)
            self.buttons.append(button)


        self.daq_thread = threading.Thread(target=self.daq_start, daemon=True)
        self.daq_thread.start()
        
    def toggle_button(self,index):
        global DATA_EXPORT_ENABLED
        # Toggle GPIO pin
        if index == 0:
            DATA_EXPORT_ENABLED = True
        else:
            DATA_EXPORT_ENABLED = False

    def daq_start(self):
        with nidaqmx.Task() as task:
            if DATA_ACQ_ENABLED:
                task.ai_channels.add_ai_voltage_chan(f"Dev17/ai1:{N_MICS}",terminal_config=TerminalConfiguration.RSE)
                task.timing.cfg_samp_clk_timing(rate=fs, sample_mode=AcquisitionType.CONTINUOUS,) #FINITE or CONTINUOUS try both
                in_stream = task.in_stream
                reader = stream_readers.AnalogMultiChannelReader(in_stream)
            while True:
            #for i in range(30):
                try:

                    ch_data_list=[]

                    #ACQUIRE-----------------
                    for i in range(N_MICS):
                        ch_data_list.append(np.array([]))
                    t_start = t.time()
                    while (t.time() - t_start <= totalTime):
                        buffer = np.zeros((numChannels, nSamples), dtype=np.float64)
                        
                        if DATA_ACQ_ENABLED:
                            reader.read_many_sample(buffer, nSamples, timeout=constants.WAIT_INFINITELY)
                            
                        for i in range(N_MICS):
                            ch_data_list[i] = np.append(ch_data_list[i], buffer[i])
                
                    #Normalize-------------------
                    for i in range(N_MICS):
                        ch_data_list[i] = normalize(ch_data_list[i])
                        
                    #COLLATE--------------
                    #data = np.array([ch1_data, ch2_data, ch3_data, ch4_data]).T
                    data = np.array(ch_data_list).T
                    
                    #PLOT TEST-------
                    #print(data[:,2])
                    '''plt.clf()
                    plt.plot(data[:,0])
                    plt.pause(0.01)'''

                    #PICKLE EXPORT------------------
                    if DATA_EXPORT_ENABLED:
                        output = open('pickles/audio_file.pkl', 'wb')
                        pickle.dump(data, output)
                        output.close()
                        print("saved",t.time()-t_start)
                except KeyboardInterrupt:
                    break

if __name__ == "__main__":
    app = App()
    app.mainloop()
    

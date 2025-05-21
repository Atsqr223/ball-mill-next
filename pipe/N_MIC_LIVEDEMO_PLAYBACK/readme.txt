%Set up------------------------
0) Turn on pump, and turn it off once indicator is at 12 o clock.
1) Turn on RPI and controller.
2) Turn on mobile hotspot and connect from this pc.
3) Connect NI DAQ and turn it on.

%Code edit----------------------
4) Set DEVICE_NAME in DAQEXPRESS_ACQ__BOYA_4MIC_LIVEDEMO.py
5) Set rpi_ip (IP address) in GUI_and_MUSIC_PLOT_LIVEDEMO.py 
	If ip address (ipconfig in terminal) on this system is 192.168.x.y , replace third number of rpi_ip with x.

%Mic array---------------------
6) Position mic array in the near markings of the pipe

%Run code-----------------------
7) Turn on all the mics
8) Run DAQEXPRESS_ACQ__BOYA_4MIC_LIVEDEMO.py. Ensure it runs.
9) Run GUI_and_MUSIC_PLOT_LIVEDEMO.py. Ensure live plot is shown and buttons work.
10) Once done, turn mics off.
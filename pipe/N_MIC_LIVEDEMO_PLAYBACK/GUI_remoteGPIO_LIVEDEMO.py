import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
from numpy import random
from random import randrange
# Remote GPIO setup
factory = PiGPIOFactory(host='192.168.170.248')  # Replace with your Raspberry Pi's IP address
button_pins = [22, 27, 17]  # Example GPIO pins for buttons
leds = [LED(pin, pin_factory=factory) for pin in button_pins]

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Live Demo")
        self.geometry("800x600")

        # Title
        self.title_label = ttk.Label(self, text="Pipeline Leakage Detection and Localization using Acoustic Beamforming", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Buttons
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


        # Image
        self.default_image = Image.open("pipe_leakage/pipe_default.png")
        self.images = [Image.open(f"pipe_leakage/pipe_leak_{i+1}.png") for i in range(3)]
        self.current_image = ImageTk.PhotoImage(self.default_image)
        self.image_label = ttk.Label(self, image=self.current_image)
        self.image_label.pack(pady=20)

        self.current_button = None

    def toggle_button(self, index):
        # Toggle GPIO pin
        if index !=3:
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
                led  = leds[self.current_button]
                led.toggle()
                self.current_button = None
                self.current_image = ImageTk.PhotoImage(self.default_image)
            else:
                random_index = randrange(3)
                led = leds[random_index]
                led.toggle()
                self.current_button = random_index
                self.current_image = ImageTk.PhotoImage(self.images[random_index])
            self.image_label.config(image=self.current_image)
            


if __name__ == "__main__":
    app = App()
    app.mainloop()

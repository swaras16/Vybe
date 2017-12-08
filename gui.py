###########################################################################################################################
# GUI- setting up Menu- File, Exit 
###########################################################################################################################
from tkinter import *
from tkinter import filedialog as fd

import pyaudio
import time
import sys
import numpy

import aubio
from aubio import source, pitch, notes

###########################################################################################################################
# global variables
###########################################################################################################################
flag = False
file = "" # default file

###########################################################################################################################
# setting up menu
###########################################################################################################################
class GUI():
    def __init__(self, frame):
        self.frame = frame
        self.menuBar = Menu(frame)
        frame.config(menu = self.menuBar)
        self.menu()

    def menu(self):
        fileMenu = Menu(self.menuBar, tearoff = 0)
        fileMenu.add_command(label = "Exit", command = self.exit)
        self.menuBar.add_cascade(label = "File", menu = fileMenu)

    def exit(self):
        flag = False
        pyaudio.PyAudio().terminate()
        self.frame.destroy()


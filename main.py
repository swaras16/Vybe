from __future__ import print_function
###########################################################################################################################
# Start here- run this (main file)- Has the global variables, audio, splash screen & data variables
###########################################################################################################################
from tkinter import *
from tkinter import filedialog as fd

import random
import math

import wave
import time
import sys
import numpy

import pyaudio

import aubio
from aubio import source, pitch, notes

import eyed3 # Song info (Meta data)

import os # for mp3 to wav conversion
from pydub import AudioSegment # for mp3 to wav conversion
 
# my own code files
from gui import *
from classic import *
from spirals import *

###########################################################################################################################
# setting up the global variables
###########################################################################################################################
flag = False
file = "" 
theme = "classic" # default theme
beats = 0
pitch = 0
onsets = 0
onsets2 = 0
# for equalizer
levels = []
values = []
nLevels = 15 # num of levels in equalizer
        
###########################################################################################################################
# Set up audio and controls- plays file, converts mp3 to wav, threads music with visuals and normalizes the equalizer
###########################################################################################################################
class Player():
    def __init__(self):
        global file, flag, chunk
        if file != "":
            self.initializeAudio()
            print("Player initialized", file)       
        # fft size
        self.win_s = 1024         
        # hop size       
        self.hop_s = self.win_s // 2 
    
    def initializeAudio(self):
        global file
        # opens file as wave file
        self.src = file + ".wav"
        samplerate = 0
        self.total_frames = 0
    
        # initialize aubio data
        self.a_source = aubio.source(self.src, samplerate, self.hop_s)
        self.samplerate = self.a_source.samplerate
        self.p = pyaudio.PyAudio()
        self.format = pyaudio.paFloat32
        self.frames = self.hop_s
        self.channels = 1
        self.p = pyaudio.PyAudio()
        
        self.a_tempo = aubio.tempo("default", self.win_s, self.hop_s, self.samplerate)
        self.pitch_o = aubio.pitch("yin", self.win_s, self.hop_s, self.samplerate)
        self.notes_o = aubio.notes("default", self.win_s, self.hop_s,self.samplerate)
        self.o = aubio.onset("default", self.win_s, self.hop_s, self.samplerate)
        self.o2 = aubio.onset("hfc", self.win_s, self.hop_s, self.samplerate)

        print("Audio set up for", file)

    def buttons(self, frame):
        global file, flag
        self.playButton = Button(frame, command = self.play)
        self.playButton.config(text = "play")
        self.playButton.pack(padx = 5, pady = 5, side = RIGHT)
        # Switch theme button
        self.themeButton = Button(frame, text = "Switch theme", command = self.setTheme)
        self.themeButton.pack(padx = 5, pady = 5, side = LEFT)
        # Select file button
        self.fileButton = Button(frame, text = "Select song", command = self.openFile)
        self.fileButton.pack(padx = 5, pady = 5, side = RIGHT)

    def openFile(self):
        global file
        fileName = fd.askopenfilename(filetypes = (("MP3 files", "*.mp3"), ("WAV Files","*.wav")))
        if fileName != None:
            temp = fileName.split('.')
            temp2 = temp[0].split('/')
            file = temp2[-1]

        # mp3 to wav file conversion
        wavFile = temp[0] + ".wav"
        mp3File = file + ".mp3"
        wavFile = file + ".wav"
        if not os.path.isfile(wavFile):
            AudioSegment.converter = "/usr/local/bin/ffmpeg"
            sound = AudioSegment.from_mp3(mp3File)
            sound.export(wavFile, format = "wav")
        # initialize audio
        self.initializeAudio()

    def setTheme(self):
        global theme
        if theme == "classic":
            theme = "fun"
        elif theme == "fun":
            theme = "classic"

    def play(self):
        global flag, file
        if file != "":
            flag = not flag
            if flag: 
                self.playButton.config(text = "pause")
            else: 
                self.playButton.config(text = "play")

            if flag:
                self.stream = self.p.open(format = self.format, channels = self.channels, rate = self.samplerate, input = False,
                                          output = True, frames_per_buffer = self.frames, stream_callback = self.pyaudio_callback)
                # start the stream (4)
                print("playing", file)
                self.stream.start_stream()
                # wait for stream to finish (5)
            else:
                self.stream.stop_stream()

    # pyaudio callback- my version of threading (non-blocking)
    # the def and return statement : 
        # cited from [https://people.csail.mit.edu/hubert/pyaudio/docs/#example-callback-mode-audio-i-o] 
    # all intermediary code is written by me.
    def pyaudio_callback(self, _in_data, _frame_count, _time_info, _status):
        global beats, pitch, onsets, levels, values
        samples, read = self.a_source()
        is_beat = self.a_tempo(samples)
        pitch = self.pitch_o(samples)[0]
        notes = self.notes_o(samples)

        if is_beat:
            beats = 1
        else: 
            beats = 0
        if self.o(samples): 
            onsets = 1
        else: 
            onsets = 0
        if self.o2(samples):
            onsets2 = 1
        else:
            onsets2 = 0
        # appends pitch values to list
        levels.append(pitch)
        avg = 1
        # removes oldest pitch value if length exceeds desired num of levels
        if len(levels) > nLevels:
           levels.remove(levels[0])
        if len(levels) >= nLevels:
            avg = sum(levels)/len(levels)
        values = []
        for i in range(len(levels)):
            values.append(min(50, 15 * levels[i] / avg)) 

        audiobuf = samples.tobytes()
        if read < self.hop_s:
            return (audiobuf, pyaudio.paComplete)
        return (audiobuf, pyaudio.paContinue)

###########################################################################################################################
# Logo- circles revolving around the centre
###########################################################################################################################
class Logo(object):
    def __init__(self, theta, data):
        self.theta = theta

    def drawLogo(self, canvas, data):
        global flag
        x = data.centreX + data.logoR * math.cos(self.theta)
        y = data.centreY + data.logoR * math.sin(self.theta)
        if theme == "fun":
            if not flag:
                i = random.randint(0, len(data.color) - 1)
                fill = data.color[i]
            else:
                fill = data.fill
        else:
            fill = data.fill
        (x0, y0, x1, y1) = getCircle(data.rLogo, x, y, data)
        canvas.create_oval(x0, y0, x1, y1, fill = fill, width = 0)

    def onTimerFired(self, data):
        dt = 0.001
        dtheta = data.omegaL * dt
        self.theta = self.theta + dtheta

###########################################################################################################################
# Splash/Home Screen- The spirals emanating from the logo
###########################################################################################################################
class Splash(object):
    def __init__(self, theta, radius, fill):
        self.theta = theta
        self.radius = radius
        self.dx = 0
        self.dy = 0
        self.fill = fill

    def drawSplash(self, canvas, data):
        x = data.centreX + data.splashR * math.cos(self.theta) + self.dx
        y = data.centreY + data.splashR * math.sin(self.theta) + self.dy
        (x0, y0, x1, y1) = getCircle(self.radius, x, y, data)
        if theme == "classic":
            fill = data.fill
        else:
            i = random.randint(0,len(data.color) - 1)
            fill = data.color[i]
        canvas.create_oval(x0, y0, x1, y1, fill=fill, outline = fill, width = 0)

    def onTimerFired(self, data):
        dt = 0.01
        self.dx += data.splashR * math.sin(-self.theta) * data.omegaSplash * dt
        self.dy += data.splashR * math.cos(-self.theta) * data.omegaSplash * dt
        self.radius += 0.02

###########################################################################################################################
# Initializing data variables
###########################################################################################################################
def init(data):
    data.wheel = []
    data.dots = []
    data.waves = []
    data.logo = []
    data.spiral = []
    data.spiral2 = []
    data.spiral3 = []
    data.spiral4 = []
    data.sine = []

    data.color = ["#5DA5DA", "#FAA43A", "#60BD68", "#D32F2F", "#F15854", "#FF4081", "#8E24AA", "#7C4DFF", "#F17CB0", 
                  "#3D5AFE", "#4DD0E1", "#B2FF59", "#FF6F00"]
    if theme == "classic":
         data.fill = data.color[random.randint(0,len(data.color) - 1)]
    else:
         data.fill = "#D32F2F"

    data.time = 0
    data.text = "play"

    # centre of the canvas
    data.centreX = data.width / 2
    data.centreY = data.height / 2

    # omega for wheel
    data.omegaW = 40
    # omega for logo
    data.omegaL = 40
    # omega for spiral
    data.omegaS = 3

    # counter for wheel
    data.counter = 0
    # counter for logo
    data.counterL = 0

    # Wheel
    data.wheelR = 0
    data.rWheel = 0
    # Dots
    data.dotsR = 8

    # Waves
    data.wavesR = 100
    data.wavesVel = 5

    # Logo circles
    data.logoR = 40
    data.rLogo = 8

    # Spiral
    data.spiralR = 50
    data.rSpiral = 5
    data.angleS = 0

    data.dt = 0.001
    
    # Splash screen
    data.splashR = data.logoR + 20
    data.rSplash = 4
    data.omegaSplash = 1
    data.splash = []
    data.angleSplash = 0
    data.mSplash = 30

def getEllipse(radius, x, y, factor, data):
    x0 = x - radius
    y0 = y + radius * factor
    x1 = x + radius
    y1 = y - radius * factor
    return (x0, y0, x1, y1)

def getCircle(radius, x, y, data):
    x0 = x - radius
    y0 = y + radius
    x1 = x + radius
    y1 = y - radius
    return (x0, y0, x1, y1)

def getMeta(canvas, data):
    global file, flag
    if file == "":
        i = random.randint(0,len(data.color) - 1)
        fill = data.color[i]
        if theme == "fun":
            canvas.create_text(0.5 * data.width, 0.05 * data.height, fill = fill, justify = "right", 
                               text = "Please Select Song to Continue", font = "Garamond 20 bold")
        else:
            canvas.create_text(0.5 * data.width, 0.05 * data.height, fill = data.fill, justify = "right", 
                               text = "Please Select Song to Continue", font = "Garamond 20 bold")
    if flag:
        try:
            song = eyed3.load(file + ".mp3")
            title = song.tag.title
            if title is None:
                title = "Unknown Song"
            artist = song.tag.artist
            if artist is None:
                artist = "Unknown Artist"
            album = song.tag.album
            if album is None:
                album = "Unknown Album"
            songText = "Now playing " + title + ", " + artist + ", " + album
        except OSError as err:
            songText = "Song info not available"
        except ValueError:
            songText = "Song info not available"
        except:
            songText = "Song info not available"
            raise
        canvas.create_text(0.5 * data.width, 0.05 * data.height, fill = data.fill, justify = "right", text = songText, 
                           font = "Garamond 15 bold")

def drawEqualizer(canvas, data):
    global values, theme
    if theme == "fun":
        fill = "black"
    elif theme == "classic":
        fill = "white"
    x0 = 10
    width = data.width/35
    # gap between rectangles (levels)
    sep = 2
    space = sep + width
    if len(values) >= nLevels:
        for i in range(nLevels - 1):
            if theme == "fun":
                i = random.randint(0,len(data.color) - 1)
                fill = data.color[i]
            else:
                fill = data.fill
            canvas.create_rectangle(x0 + i * space, data.height - values[i], x0 + i * space + width, data.height, 
                                    width = 1, outline = fill, fill = fill)


def redrawAll(canvas, data):
    global flag, theme
    if theme == "fun":
        i = random.randint(0, len(data.color) - 1)
        lineCol = data.color[i]
        # dotted line through the middle of the canvas
        canvas.create_line(0, data.centreY, data.width, data.centreY, fill = lineCol, width = 1, dash = (6,5,2,4))
    else:
        canvas.create_line(0, data.centreY, data.width, data.centreY, fill = data.fill, width = 1, dash = (6,5,2,4))

    if not flag:
        # Splash page animation
        for p in data.splash:
            p.drawSplash(canvas, data)

    # the following things are drawn only when music plays
    if flag:
        drawEqualizer(canvas, data)
        if theme == "classic":
            # draw waves
            for p in data.waves:
                p.drawWaves(canvas, data)

        if theme == "fun":
            # draw spirals
            for p in data.spiral:
                p.drawSpiral(canvas, data)
            for p in data.spiral2:
                p.drawSpiral(canvas, data)
            for p in data.spiral3:
                p.drawSpiral(canvas, data)
            for p in data.spiral4:
                p.drawSpiral(canvas, data)

        # draw circle of wheel
        (x0, y0, x1, y1) = getCircle(data.wheelR, data.centreX, data.centreY, data)
        # draws orbit that is the ring connects the circles
        if theme == "classic":
            canvas.create_oval(x0, y0, x1, y1, outline = data.fill, width = 3)
        else: 
            canvas.create_oval(x0, y0, x1, y1, outline = data.fill, width = 3)
        
        # draw dots
        for p in data.dots:
            p.drawDots(canvas, data)
        
        # draw wheel
        for p in data.wheel:
            p.drawWheel(canvas, data)
            
    # draw logo circles
    for p in data.logo:
        p.drawLogo(canvas, data)

    if theme == "fun":
        i = random.randint(0, len(data.color) - 1)
        textCol = data.color[i]
        # text for logo
        logo1 = canvas.create_text(0.85 * data.width, 0.95 * data.centreY, text = "vybe", fill = textCol, 
                                   font = "Didot 40 bold" )
        logo2 = canvas.create_text(0.85 * data.width, 1.05 * data.centreY, text = "see it. feel it", 
                                   fill = textCol, font = "Garamond 22 italic")
    else:
        logo1 = canvas.create_text(0.85 * data.width, 0.95 * data.centreY, text = "vybe", fill = data.fill, 
                                   font = "Didot 40 bold" )
        logo2 = canvas.create_text(0.85 * data.width, 1.05 * data.centreY, text = "see it. feel it", 
                                   fill = data.fill, font = "Garamond 22 italic")
    # displays meta data on screen (song info)
    getMeta(canvas, data)


def keyPressed(event, data):
    pass

def mousePressed(event, data):
    pass

def timerFired(data):
    global flag, beats, pitch, onsets
    data.time += data.timerDelay

    #Stop animations if song is paused
    if flag: 
        data.text = "pause"
    else: 
        data.text = "play"
    
    if flag:
        # setting baseline values
        data.wheelR = min(data.height // 2, pitch / 3 + data.logoR + 20)
        data.rWheel = 10

        nWheel = 30
        numDots = pitch
        nDots = 4
        nWaves = 20

        data.omegaW = pitch / 40
        data.omegaL = pitch / 20

        # for beats
        if beats > 0:
            data.rWheel = 15
            numDots = pitch * 50
            data.omegaW = pitch / 20
            nDots = 2
            nWheel = 20

        # for onsets 
        if onsets > 0:
            numDots = pitch * 70
            nDots = 1
            i = random.randint(0, len(data.color) - 1)
            data.fill = data.color[i]
            data.rWheel = 15

        # Wheel
        if data.counter < (1 + 360/nWheel):
            for angle in range(0, 360, nWheel):
                theta = (angle / 180) * math.pi
                data.wheel.append(Wheel(data.rWheel, theta, data))
                data.counter += 1

        for p in data.wheel:
            p.onTimerFired(data)

        # Generates Dots
        for angle in range(0, 360, nDots):
            theta = (angle / 180) * math.pi
            data.dots.append(Dots(data.dotsR, theta))
        if len(data.dots) > numDots:
            data.dots = []

        for p in data.dots:
            p.onTimerFired(data)

        # Generates waves
        if onsets > 0:
            data.wavesVel = -5
        k = int(data.wheelR)
        for r in range(0, k, 10):
            data.waves.append(Waves(r))
        if len(data.waves) > nWaves:
            data.waves = []

        for p in data.waves:
            p.onTimerFired(data)

        # Generate spiral
        if flag:
            data.spiralR = min(data.height // 5, pitch)
            numSpiral = pitch * 100
            data.angleS += 5

            # beats
            if beats > 0:
                data.omegaS = 3
                data.spiralR = min(data.height // 5, pitch)
                numSpiral = pitch * 300
                data.dt = 0.05

            # onsets
            if onsets > 0:
                data.omegaS = -9
                data.spiralR = min(data.height // 5, pitch)
                numSpiral = pitch * 200
                data.dt = 0.01

            radius = 8
            theta = (data.angleS / 180) * math.pi
            theta2 = ((data.angleS + 90) / 180) * math.pi
            theta3 = ((data.angleS + 180) / 180) * math.pi
            theta4 = ((data.angleS + 270) / 180) * math.pi

            data.spiral.append(Spiral(theta, radius, data.fill, data))
            data.spiral2.append(Spiral(theta2, radius, data.fill, data))
            data.spiral3.append(Spiral(theta3, radius, data.fill, data))
            data.spiral4.append(Spiral(theta4, radius, data.fill, data))

            if data.angleS >= 360:
                data.angleS = 0

            if len(data.spiral) > numSpiral:
                data.spiral = []
            if len(data.spiral2) > numSpiral:
                data.spiral2 = []
            if len(data.spiral3) > numSpiral:
                data.spiral3= []
            if len(data.spiral4) > numSpiral:
                data.spiral4 = []

            for p in data.spiral:
                p.onTimerFired(data)
            for p in data.spiral2:
                p.onTimerFired(data)
            for p in data.spiral3:
                p.onTimerFired(data)
            for p in data.spiral4:
                p.onTimerFired(data)

    # Generate logo
    if data.counterL < 8:
        for angle in range(0, 360, 45):
            theta = (angle / 180) * math.pi
            data.logo.append(Logo(theta, data))
            data.counterL += 1

    for p in data.logo:
        p.onTimerFired(data)

    # Generate Splash page spiral
    if not flag:
        i = random.randint(0, len(data.color) - 1)
        fill = data.color[i]
        numSplash = 200
        data.rSplash = 0
        data.angleSplash += data.mSplash
        data.rSplash = 1
        thetaSplash = (data.angleSplash / 180) * math.pi
        data.splash.append(Splash(thetaSplash, data.rSplash, fill))
        if data.angleSplash >= 360:
            data.angleSplash = 0
        # change spiral type each time data.splash is reset
        # changing data.mSplash changes type of spiral
        if len(data.splash) > numSplash:
            if data.mSplash == 15:
                data.mSplash = 30
            else:
                data.mSplash = 15
            data.splash = []
        for p in data.splash:
            p.onTimerFired(data)

###########################################################################################################################
# run function
###########################################################################################################################
def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        global theme
        if theme == "classic":
            fill = "black"
        elif theme == "fun":
            fill = "white"
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height, fill = fill, outline = fill, width = 0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)

    # Set up data and call init
    class Struct(object): 
        pass
    data = Struct()
    data.width = width
    data.height = height
    
    data.timerDelay = 1 # milliseconds
    
    init(data)
    # create the root and the canvas
    root = Tk()

    canvas = Canvas(root, width = data.width, height = data.height)
    canvas.pack(side=TOP)
    
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    
    # and launch the app
    #root.mainloop()  # blocks until window is closed
    GUI(root)
    app = Player().buttons(root)
    print("bye!")
    
run(1250, 750)

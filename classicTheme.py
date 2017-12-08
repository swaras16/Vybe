###########################################################################################################################
# Visuals- Draws the "Classic" theme visuals (Wheel, Dots, Waves)
###########################################################################################################################
from tkinter import *
from tkinter import filedialog as fd

import random
import math

import time
import sys

###########################################################################################################################
# setting up the global variables
###########################################################################################################################
flag = False
file = "" # default file
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
# creates Animations
###########################################################################################################################
def getCircle(radius, x, y, data):
    x0 = x - radius
    y0 = y + radius
    x1 = x + radius
    y1 = y - radius
    return (x0, y0, x1, y1)

###########################################################################################################################
# Wheel with circles- circles in an orbit connected by a ring
###########################################################################################################################
class Wheel(object):
    def __init__(self, radius, theta, data):
        self.radius = radius
        self.theta = theta
        
    def drawWheel(self, canvas, data):
        x = data.centreX + data.wheelR * math.cos(self.theta)
        y = data.centreY + data.wheelR * math.sin(self.theta)
        if theme == "fun":
            fill = data.fill
        else:
            fill = data.fill
        (x0, y0, x1, y1) = getCircle(self.radius, x, y, data)
        canvas.create_oval(x0, y0, x1, y1, fill = fill, outline = fill, width = 0)

    def onTimerFired(self, data):
        dt = 0.001
        dtheta = data.omegaW * dt
        self.theta = self.theta + dtheta

###########################################################################################################################
# Dots- circles emanating from the centre
###########################################################################################################################
class Dots(object):
    def __init__(self, radius, theta):
        self.centreX = 0
        self.centreY = 0
        self.radius = radius
        self.theta = theta
        self.gap = 15

    def drawDots(self, canvas, data):
        (x0, y0, x1, y1) = getCircle(self.radius, data.centreX + self. centreX, data.centreY + self.centreY, data)
        if theme == "fun":
            fill = data.fill
        else:
            fill = data.fill
        dots = canvas.create_oval(x0, y0, x1, y1, outline = fill)

    def onTimerFired(self, data):
        self.centreX += math.cos(self.theta) * self.gap
        self.centreY += math.sin(self.theta) * self.gap
        self.radius += 0.5

###########################################################################################################################
# Waves- concentric circles emanating from the center
###########################################################################################################################
class Waves(object):
    def __init__(self, radius):
        self.radius = radius

    def drawWaves(self, canvas, data):
        (x0, y0, x1, y1) = getCircle(self.radius, data.width/2, data.height/2, data)
        waves = canvas.create_oval(x0, y0, x1, y1, width = 1, outline = data.fill)

    def onTimerFired(self, data):
        self.radius -= 2 * data.wavesVel


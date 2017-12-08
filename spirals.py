###########################################################################################################################
# Visuals- Draws the Spirals for "Fun" theme
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
# Spiral
###########################################################################################################################
class Spiral(object):
    def __init__(self, theta, radius, fill, data):
        self.theta = theta
        self.radius = radius
        self.dx = 0
        self.dy = 0
        self.fill = fill

    def drawSpiral(self, canvas, data):
        x = data.centreX + data.spiralR * math.cos(self.theta) + self.dx
        y = data.centreY + data.spiralR * math.sin(self.theta) + self.dy
        (x0, y0, x1, y1) = getCircle(self.radius, x, y, data)
        canvas.create_oval(x0, y0, x1, y1, fill = self.fill, outline = self.fill, width = 0)

    def onTimerFired(self, data):
        dt = data.dt
        self.dx += data.spiralR * math.sin(-self.theta) * data.omegaS * dt
        self.dy += data.spiralR * math.cos(-self.theta) * data.omegaS * dt
        i = random.randint(0, len(data.color) - 1)
        data.fill = data.color[i]


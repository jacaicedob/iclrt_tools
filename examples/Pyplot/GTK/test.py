#!/usr/bin/env python

from gi.repository import Gtk
import PlotWindow as pltw
import numpy as np

t = np.arange(0,np.pi,np.pi/10000)

a = np.sin(2*np.pi*t)
b = np.cos(2*np.pi*t)

w1 = pltw.PlotWindow([t,a])
w2 = pltw.PlotWindow([t,b])

Gtk.main()        
        

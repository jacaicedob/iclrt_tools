#!/usr/bin/env python

from gi.repository import Gtk
import matplotlib as mpl
#~ mpl.use('GtkAgg')  # or 'GtkAgg'
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas

from numpy.random import random
import numpy as np
from matplotlib.widgets import SpanSelector
from matplotlib.figure import Figure
import dfplots as df

class PlotWindow(Gtk.Window):
    
    def __init__(self, data):
        Gtk.Window.__init__(self,title="Test plot window")
        self.set_default_size(800,600)
        
        self.connect("destroy", Gtk.main_quit)
        
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.LEFT)
        
        self.numCols = 10
        labels = []
        models = []
        views = []
        scrolled_windows = []
        vboxes = []
        self.canvass = []
        
        for i in xrange(len(data)):
            label = Gtk.Label(data[i][2])
            labels.append(label)
            
        for d in data:
            models.append(self.create_model(d[1]))
            
        for model in models:
            views.append(self.create_view(model))
            
        for view in views:
            scw = Gtk.ScrolledWindow()
            scw.add(view)
            scrolled_windows.append(scw)
            
        for i in xrange(len(scrolled_windows)):
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            
            try:
                x = data[i][0]
                y = data[i][1]
            
            except IndexError:
                raise
            
            fig = Figure(figsize=(6,4))
            self.canvass.append(FigureCanvas(fig))
            
            ax = fig.add_subplot(111)
            ax.plot(x, y)
            ax.set_title(data[i][2])

            p = df.plotdf(fig, ax)
            p.plot()
                        
            box.pack_start(scrolled_windows[i], True, True, 0)
            box.pack_start(self.canvass[i], True, True, 0)
            
            vboxes.append(box)
        #~ 
        #~ for i in xrange(len(figs)):
            #~ ps.append(df.plotdf(figs[i], axs[i]))
        
        for i in xrange(len(scrolled_windows)):
            
            self.notebook.append_page(vboxes[i], labels[i])
            
        self.add(self.notebook)
        
        #~ try:
            #~ self.x = data[0]
            #~ self.y = data[1]
        #~ 
        #~ except IndexError:
            #~ raise
        #~ 
        #~ self.fig = Figure(figsize=(6,4))
        #~ canvas = FigureCanvas(self.fig)
        #~ 
        #~ self.ax = self.fig.add_subplot(111)
        #~ self.ax.plot(self.x, self.y)
        #~ self.ax.set_title("Test")
        #~ 
        #~ self.p = df.plotdf(self.fig, self.ax)
        #~ self.p.plot()     
            #~ 
        #~ box = Gtk.Box()#orientation=Gtk.Orientation.VERTICAL)
        #~ 
        #~ box.pack_start(canvas, True, True, 0)
        #~ 
        #~ self.add(box)
        self.show_all()
       
    def create_model(self, y):
        types = [float]*self.numCols
        model = Gtk.ListStore(*types)
        
        numRows = y.shape[0] / self.numCols
        if numRows == 0:
            numRows = 1
            
        rows = np.split(y[:numRows*self.numCols], numRows)
        rows.append(y[numRows*self.numCols+1:])
        
        for row in rows:
            model.append(list(row))        
        
        return model
        
    def create_view(self, model):
        view = Gtk.TreeView(model)
        
        cell_renderer = Gtk.CellRendererText()
        cell_renderer.set_property("xalign", 0.5)
        
        for i in xrange(self.numCols):
            column = Gtk.TreeViewColumn(i, cell_renderer, text = i)
            view.append_column(column)
        
        return view

if __name__ == "__main__":
    
    time = np.arange(0,np.pi,np.pi/10000)
    sin = np.sin(2*np.pi*time)
    cos = np.cos(2*np.pi*time)
    
    data = [time, sin, 'Data!']
    data2 = [time, cos, 'Data 2!']
    
    try:
        win = PlotWindow([data, data2])
        #~ win2 = PlotWindow(data2)
        
    
        Gtk.main()
        
    except IndexError, e:
        print "Error: %s" % str(e)
        
        

#!/usr/bin/env python
"""
The SpanSelector is a mouse widget to select a xmin/xmax range and plot the
detail view of the selected region in the lower axes
"""

import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector, RectangleSelector
from matplotlib import cm, dates
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d import Axes3D
import datetime
import math
import pyart

import iclrt_tools.lma.lma as lma


def plot(x, y, **kwargs):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, y, **kwargs)

    p = Plot(fig, ax)
    p.plot()

    return p

class syncdf(object):
    """
    class to synchronize dfplots (when you zoom in on one graph, all of
    them do)
    """

    def __init__(self, plotdfs):
        self.plots = plotdfs
        
        for plot in self.plots:
            plot.synced = True
        
    def onselect(self, xmin, xmax):
        for plot in self.plots:
            plot.onselect(xmin, xmax)
            
    def plot_all(self):
        self.spans = []
        self.cids = []
        
        for plot in self.plots:
            self.spans.append(SpanSelector(plot.ax, self.onselect, 'horizontal', useblit=True,
                        rectprops=dict(alpha=0.5, facecolor='red') ))
                    
            self.cids.append(plot.fig.canvas.mpl_connect(\
                            'button_release_event', plot.onclick))
            
            plot.fig.canvas.mpl_connect('key_press_event', plot.onkeypress)

class Plot(object):
    """
    Plot graphs to mimic df32 program (written by Jaime Caicedo and Brian
    Hare)
    """
    def __init__(self, figure, ax, synced=False, max_points=1E9):
        self.fig = figure
        self.ax = ax
        self.max_points = max_points
        self.set_offset = False
        self.lines = ax.get_lines()

        for line in self.lines:
            thisx = line.get_xdata()
            thisy = line.get_ydata()

            # Down sample
            ds_rate = int(thisy.shape[0]/self.max_points)

            if ds_rate == 0:
                ds_rate = 1

            thisy = thisy[::ds_rate]
            thisx = thisx[::ds_rate]

            # Set line
            line.set_data(thisx, thisy)

        self.x_stack = []
        self.y_stack = []
        self.points = []  # Holds the points selected using the shortcut 'o'
        self.x_bounds = self.ax.get_xlim()
        self.y_bounds = self.ax.get_ylim()
        self.synced = synced
        self.sel_points = False
        self.sel_zero = False

        # Sett all matplotlib keyboard shortcuts to none
        mpl.rcParams['keymap.fullscreen'] = ''  # f
        mpl.rcParams['keymap.home'] = ''  # h, r, home
        mpl.rcParams['keymap.back'] = ''  # left, c, backspace
        mpl.rcParams['keymap.forward'] = ''  # right, v
        # mpl.rcParams['keymap.pan'] = ''  # p
        mpl.rcParams['keymap.zoom'] = ''  # o
        # mpl.rcParams['keymap.save'] = ''  # s
        # mpl.rcParams['keymap.quit'] = ''  # ctrl+w, cmd+w
        mpl.rcParams['keymap.grid'] = ''  # g
        mpl.rcParams['keymap.yscale'] = ''  # l
        mpl.rcParams['keymap.xscale'] = ''  # L, k
        mpl.rcParams['keymap.all_axes'] = ''  # a

        self.plot()

    def plot(self):
        self.span = SpanSelector(self.ax, self.onselect,
                                       'horizontal', useblit=True,
                                       rectprops=dict(alpha=0.2,
                                       facecolor='red'))

        self.span_v = SpanSelector(self.ax, self.onselect_v,
                                       'vertical', useblit=True,
                                       rectprops=dict(alpha=0.2,
                                       facecolor='red'))

        self.rect_sel = RectangleSelector(self.ax,
                                          self.onselect_rect,
                                          button=[1],
                                          drawtype='box',
                                          rectprops=dict(alpha=0.2,
                                                         facecolor='red',
                                                         edgecolor='red',
                                                         linewidth=2))

        self.fig.canvas.mpl_connect('button_release_event',
                                    self.onclick)
        self.fig.canvas.mpl_connect('key_press_event', self.onkeypress)
        self.fig.canvas.mpl_connect('key_release_event',
                                    self.onkeyrelease)

        self.span_v.visible = False
        self.rect_sel.set_active(False)

    def onselect(self, xmin, xmax):
        if xmin == xmax:
            return True

        # Save the current graph's limits
        xmin_old = self.ax.get_xlim()[0]
        xmax_old = self.ax.get_xlim()[1]

        ymin_old = self.ax.get_ylim()[0]
        ymax_old = self.ax.get_ylim()[1]

        self.x_stack.append([xmin_old, xmax_old])
        self.y_stack.append([ymin_old, ymax_old])

        self.x_bounds = [xmin, xmax]
        self.ax.set_xlim(self.x_bounds)

        self.fig.canvas.draw()

    def onselect_v(self, ymin, ymax):
        if ymin == ymax:
            return True

        # Save the current graph's limits
        xmin_old = self.ax.get_xlim()[0]
        xmax_old = self.ax.get_xlim()[1]

        ymin_old = self.ax.get_ylim()[0]
        ymax_old = self.ax.get_ylim()[1]

        self.x_stack.append([xmin_old, xmax_old])
        self.y_stack.append([ymin_old, ymax_old])

        self.y_bounds = [ymin, ymax]
        self.ax.set_ylim(self.y_bounds)

        self.fig.canvas.draw()

    def onselect_rect(self, eclick, erelease):
        xmin_old = self.ax.get_xlim()[0]
        xmax_old = self.ax.get_xlim()[1]

        ymin_old = self.ax.get_ylim()[0]
        ymax_old = self.ax.get_ylim()[1]

        self.x_stack.append([xmin_old, xmax_old])
        self.y_stack.append([ymin_old, ymax_old])

        x_start = eclick.xdata
        y_start = eclick.ydata

        x_end = erelease.xdata
        y_end = erelease.ydata

        if x_start == x_end or y_start == y_end:
            return True

        xmin = np.min([x_start, x_end])
        xmax = np.max([x_start, x_end])

        ymin = np.min([y_start, y_end])
        ymax = np.max([y_start, y_end])

        self.x_bounds = [xmin, xmax]
        self.ax.set_xlim(self.x_bounds)

        self.y_bounds = [ymin, ymax]
        self.ax.set_ylim(self.y_bounds)

        self.fig.canvas.draw()

    def onclick(self, event):
        if event.button == 3 and (event.inaxes is self.ax or self.synced):
            # On OSX, event.button == 2 is a right click

            if self.x_stack:
                # Get old limits from stacks
                xlims = self.x_stack.pop()
                xmin = xlims[0]
                xmax = xlims[1]

                ylims = self.y_stack.pop()
                ymin = ylims[0]
                ymax = ylims[1]

                self.x_bounds = [xmin, xmax]
                self.ax.set_xlim(self.x_bounds)

                self.y_bounds = [ymin, ymax]
                self.ax.set_ylim(self.y_bounds)

                self.fig.canvas.draw()

        elif event.button == 1 and (event.inaxes is self.ax):
            if self.sel_points:
                x = event.xdata
                y = event.ydata

                self.points.append([x, y])

                self.ax.scatter(x, y, marker='x', c='r', zorder=10, label='Selection')
                self.fig.canvas.draw()

            elif self.sel_zero:
                x = event.xdata
                l = np.array(self.ax.get_xticks().tolist())
                ind = np.searchsorted(l, x)
                l -= l[ind]

                self.ax.set_xticklabels(l.tolist())
                self.fig.canvas.draw()

    def onkeypress(self, event):
        if event.key == 'r':
            if self.x_stack:
                # Get initial limits from stacks
                xmin = self.x_stack[0][0]
                xmax = self.x_stack[0][1]

                ymin = self.y_stack[0][0]
                ymax = self.y_stack[0][1]

                self.x_stack = []
                self.y_stack = []

                self.x_bounds = [xmin, xmax]
                self.ax.set_xlim(self.x_bounds)

                self.y_bounds = [ymin, ymax]
                self.ax.set_ylim(self.y_bounds)

                self.fig.canvas.draw()

        elif event.key == 'y':
            self.span.visible = False
            self.span_v.visible = True
            self.rect_sel.set_active(False)

        elif event.key == 'o':
            self.span.visible = False
            self.span_v.visible = False
            self.rect_sel.visible = True
            self.rect_sel.set_active(True)

        elif event.key == 'a':
            self.span.visible = False
            self.span_v.visible = False
            self.rect_sel.set_active(False)
            self.sel_points = True

        elif event.key == 'z':
            self.span.visible = False
            self.span_v.visible = False
            self.rect_sel.set_active(False)
            self.sel_zero = True

        elif event.key == ' ' or event.key == 'escape':
            plt.close(self.fig)

    def onkeyrelease(self, event):
        if event.key == 'y':
            self.span.visible = True
            self.span_v.visible = False
            self.rect_sel.set_active(False)

        elif event.key == 'o':
            self.rect_sel.set_active(False)
            self.span.visible = True
            self.span_v.visible = False

        elif event.key == 'a':
            self.span.visible = True
            self.span_v.visible = False
            self.rect_sel.set_active(False)
            self.sel_points = False

        elif event.key == 'z':
            self.span.visible = True
            self.span_v.visible = False
            self.rect_sel.set_active(False)
            self.sel_zero = False


class pickerPlot(Plot):
    """
    This class enables the picker attribute of lines and sets up the
    environment to enable the movement of lines in the canvas.
    (written by Jaime Caicedo)
    """
      
    def __init__(self, fig, ax):
        super().__init__(fig, ax)
        self.move_flag = False
        self.selected_line = None

        maxx = 0
        minn = 0

        for line in self.lines:
            line.set_picker(5)  # Activate the picker property of the line

            # Update the min and max values
            if min(line.get_ydata()) < minn:
                minn = min(line.get_ydata())

            if max(line.get_ydata()) > maxx:
                maxx = max(line.get_ydata())

        # Find the largest magnitude (abs value) between the min and max of
        # all the lines and set the room between the top/bottom of the graph
        #  and the canvas lines to be 10% of this largest magnitude
        if abs(maxx) > abs(minn):
            room = 0.1 * abs(maxx)

        else:
            room = 0.1 * abs(minn)

        # Set the y limits so that there is the same space between the
        # top/bottom of the graph and the canvas lines
        self.ax.set_ylim([minn - room, maxx + room])

        # Activate the picker property of the axis
        self.ax.set_picker(5)
        self.fix_axis = False

    def plot(self):
        super().plot()
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.span.visible = False

    def onpick(self, event):
        if event.artist == self.ax:
            pass

        if event.artist in self.lines and event.mouseevent.button == 1:
            #~ print('Selected')
            self.move_flag = True
            self.selected_line = event.artist
            self.line_width = self.selected_line.get_linewidth()
            self.selected_line.set_linewidth(2*self.line_width)

        else:
            #~ print('De-Selected')
            self.move_flag = False

            if self.selected_line:
                self.selected_line.set_linewidth(self.line_width)
                self.selected_line = None

        self.fig.canvas.draw()
            
    def onkeypress(self, event):
        line = self.selected_line
        
        if line:
            dt = abs(np.diff(line.get_xdata())[0]/2)
            dy = (np.max(line.get_ydata()) - np.min(line.get_ydata()))/len(line.get_xdata())

            ylims = self.ax.get_ylim()

            if event.key == 'ctrl+left' and self.move_flag:
                #~ print('Moving left...')
                line.set_xdata(line.get_xdata() - 10*dt)
                
            elif event.key == 'left' and self.move_flag:
                #~ print('Moving left...')
                line.set_xdata(line.get_xdata() - dt)
                
            elif event.key == 'ctrl+right' and self.move_flag:
                #~ print('Moving right...')
                line.set_xdata(line.get_xdata() + 10*dt)
                
            elif event.key == 'right' and self.move_flag:
                #~ print('Moving right...')
                line.set_xdata(line.get_xdata() + dt)
                
            elif event.key == 'up' and self.move_flag:
                #~ print('Moving up...')
                line.set_ydata(line.get_ydata() + dy)

                if not(self.fix_axis):
                    self.ax.set_ylim([ylims[0] + dy, ylims[1] + dy])
            
            elif event.key == 'ctrl+up' and self.move_flag:
                #~ print('Moving up...')
                line.set_ydata(line.get_ydata() + 10*dy)

                if not(self.fix_axis):
                    self.ax.set_ylim([ylims[0] + 10*dy, ylims[1] + 10*dy])
            
            elif event.key == 'alt+up' and self.move_flag:
                #~ print('Moving up...')
                line.set_ydata(line.get_ydata() + 100*dy)

                if not(self.fix_axis):
                    self.ax.set_ylim([ylims[0] + 100*dy, ylims[1] + 100*dy])
                
            elif event.key == 'down' and self.move_flag:
                #~ print('Moving down...')
                line.set_ydata(line.get_ydata() - dy)

                if not(self.fix_axis):
                    self.ax.set_ylim([ylims[0] - dy, ylims[1] - dy])
            
            elif event.key == 'ctrl+down' and self.move_flag:
                #~ print('Moving down...')
                line.set_ydata(line.get_ydata() - 10*dy)

                if not(self.fix_axis):
                    self.ax.set_ylim([ylims[0] - 10*dy, ylims[1] - 10*dy])
            
            elif event.key == 'alt+down' and self.move_flag:
                #~ print('Moving down...')
                line.set_ydata(line.get_ydata() - 100*dy)

                if not(self.fix_axis):
                    self.ax.set_ylim([ylims[0] - 100*dy, ylims[1] - 100*dy])

            self.fig.canvas.draw()

        if event.key == 'x':
            self.span.visible = True
            self.span_v.visible = False
            self.rect_sel.set_active(False)

        elif event.key == 'f':
            self.fix_axis = not(self.fix_axis)

        else:
            super().onkeypress(event)

    def onkeyrelease(self, event):
        if event.key == 'x':
            self.span.visible = False
            self.span_v.visible = False
            self.rect_sel.set_active(False)

        elif event.key == 'y':
            self.span.visible = False
            self.span_v.visible = False
            self.rect_sel.set_active(False)

        elif event.key == 'a':
            self.span.visible = False
            self.span_v.visible = False
            self.rect_sel.set_active(False)

        else:
            super().onkeyrelease(event)


class RelativeTimePlot(object):
    """
    Plotter to generate graphs with relative time axes (written by Jaime
    Caicedo)
    """

    def __init__(self, x, y, max_points=10000, draw=True):    
        self.delta_t = np.diff(x)[0]
        self.zero_time = (x[-1] - x[0])/2
        self.zero_ind = int(self.zero_time/self.delta_t)
        self.max_points = max_points
        
        self.x = x
        self.y = y
        
        self.x_stack = []
        self.draw = draw
        
        if self.draw:
            self.fig = plt.figure()
            self.fig.suptitle('Please select the time zero (Press down \'n\' and left click).')
            self.ax = self.fig.add_subplot(111)
            self.data_line = self.ax.plot(x,y)[0]
            self.zero_line = self.ax.plot([self.zero_time, self.zero_time], [self.ax.get_ylim()[0], self.ax.get_ylim()[1]], 'r')[0]
        
            self.y_bounds = [self.ax.get_ylim()[0], self.ax.get_ylim()[1]]
        
            self.set_zero = False
                  
            # Down sample
            ds_rate = int(self.y.shape[0]/self.max_points)
        
            if ds_rate == 0:
                ds_rate = 1
            
            thisy = self.y[::ds_rate]
            thisx = self.x[::ds_rate]
        
            # Set line                    
            self.data_line.set_data(thisx, thisy)
            
        self.x_bounds = [x[0], x[-1]]     
        
    def onselect(self, xmin, xmax):
        if xmin == xmax:
            return True
            
        # Save the current graph's limits
        xmin_old = self.ax.get_xlim()[0]
        xmax_old = self.ax.get_xlim()[1]
        
        # Get new limits and redraw
        indmin, indmax = np.searchsorted(self.x, (xmin, xmax))
        indmax = min(len(self.x)-1, indmax)
        
        if (indmax - indmin) < 2:
            return True
        
        self.x_stack.append([xmin_old, xmax_old])
        
        thisx = self.x[indmin:indmax]
        self.ax.set_xlim(thisx[0], thisx[-1])
        self.x_bounds = [thisx[0], thisx[-1]]
        
        max_y = -np.inf
        min_y = np.inf
        
        thisy = self.y[indmin:indmax]
            
        # Down sample            
        ds_rate = int(thisy.shape[0]/self.max_points)
        
        if ds_rate == 0:
            ds_rate = 1
            
        thisy = thisy[::ds_rate]
        thisx = thisx[::ds_rate]
        
        # Set line
        self.data_line.set_data(thisx, thisy)
           
        mx_y = thisy.max()
        mn_y = thisy.min()   
                
        if mx_y > max_y:
            max_y = mx_y
        
        if mn_y < min_y:
            min_y = mn_y
        
        
        max_y = max_y + (max_y - min_y)*.1
        min_y = min_y - (max_y - min_y)*.1
        
        self.ax.set_ylim(min_y, max_y)
        
        self.fig.canvas.draw()

    def onclick(self, event):
        if event.button == 1 and (event.inaxes is self.ax):
            if self.set_zero:
                self.zero_time = event.xdata
                self.zero_ind = int((self.zero_time - self.x[0])/self.delta_t)

                ##redraw
                zero_x = [self.zero_time, self.zero_time]
                self.zero_line.set_data(zero_x, self.y_bounds)
                
                self.fig.canvas.draw()

        if event.button == 3 and (event.inaxes is self.ax):

            if self.x_stack:
                # Get old limits from stacks
                xmin = self.x_stack[-1][0]
                xmax = self.x_stack[-1][1]

                self.x_stack = self.x_stack[:-1]

                # Set new limits and redraw
                indmin, indmax = np.searchsorted(self.x, (xmin, xmax))
                indmax = min(len(self.x)-1, indmax)

                thisx = self.x[indmin:indmax]
                self.ax.set_xlim(thisx[0], thisx[-1])
                self.x_bounds = [thisx[0], thisx[-1]]

                ##set the data y
                thisy = self.y[indmin:indmax]

                # Down sample            
                ds_rate = int(thisy.shape[0]/self.max_points)
        
                if ds_rate == 0:
                    ds_rate = 1
            
                thisy = thisy[::ds_rate]
                thisx = thisx[::ds_rate]
        
                # Set line
                self.data_line.set_data(thisx, thisy)
                ##self.data_line.set_data(thisx, data_y)

                max_y = thisy.max()
                min_y = thisy.min()

                ##set the offset y
                ##offset_y = np.ones(len(thisx))*self.dc_offset
                ##self.offset_line.set_data(thisx, offset_y)

#~                 max_y = max(max_y, self.dc_offset)
#~                 min_y = min(min_y, self.dc_offset)

                ##draw
                self.ax.set_ylim(min_y-0.1*(max_y-min_y), max_y+0.1*(max_y-min_y))
                self.fig.canvas.draw()
        
        if event.button == 2 and (event.inaxes is self.ax):
            """
            On a Mac, event.button == 2 is a right-click
            """
            if self.x_stack:
                # Get old limits from stacks
                xmin = self.x_stack[-1][0]
                xmax = self.x_stack[-1][1]

                self.x_stack = self.x_stack[:-1]

                # Set new limits and redraw
                indmin, indmax = np.searchsorted(self.x, (xmin, xmax))
                indmax = min(len(self.x)-1, indmax)

                thisx = self.x[indmin:indmax]
                self.ax.set_xlim(thisx[0], thisx[-1])
                self.x_bounds = [thisx[0], thisx[-1]]

                ##set the data y
                thisy = self.y[indmin:indmax]

                # Down sample            
                ds_rate = int(thisy.shape[0]/self.max_points)
        
                if ds_rate == 0:
                    ds_rate = 1
            
                thisy = thisy[::ds_rate]
                thisx = thisx[::ds_rate]
        
                # Set line
                self.data_line.set_data(thisx, thisy)
                
                ##self.data_line.set_data(thisx, data_y)

                max_y = thisy.max()
                min_y = thisy.min()

                ##set the offset y
                ##offset_y = np.ones(len(thisx))*self.dc_offset
                ##self.offset_line.set_data(thisx, offset_y)

              #~   max_y = max(max_y, self.dc_offset)
#~                 min_y = min(min_y, self.dc_offset)

                ##draw
                self.ax.set_ylim(min_y-0.1*(max_y-min_y), max_y+0.1*(max_y-min_y))
                self.fig.canvas.draw()
    
    def onkeypress(self,event):
        if event.key == 'n':
            self.set_zero = True
            
        elif event.key == 'r':
            if self.x_stack:
                # Get initial limits from stacks
                xmin = self.x_stack[0][0]
                xmax = self.x_stack[0][1]
            
                self.x_stack = []
            
                # Set new limits and redraw
                indmin, indmax = np.searchsorted(self.x, (xmin, xmax))
                indmax = min(len(self.x)-1, indmax)

                thisx = self.x[indmin:indmax]
                self.ax.set_xlim(thisx[0], thisx[-1])
                self.x_bounds = [thisx[0], thisx[-1]]
                
                max_y = -np.inf
                min_y = np.inf
                
                thisy = self.y[indmin:indmax]
                
                # Down sample            
                ds_rate = int(thisy.shape[0]/self.max_points)
        
                if ds_rate == 0:
                    ds_rate = 1
            
                thisy = thisy[::ds_rate]
                thisx = thisx[::ds_rate]
                
                # Set line
                self.data_line.set_data(thisx, thisy)
           
                mx_y = thisy.max()
                mn_y = thisy.min()   
                
                if mx_y > max_y:
                    max_y = mx_y
        
                if mn_y < min_y:
                    min_y = mn_y
                        
                max_y = max_y + (max_y - min_y)*.1
                min_y = min_y - (max_y - min_y)*.1
                           
                self.ax.set_ylim(min_y, max_y)
                self.fig.canvas.draw()
        
        elif event.key == ' ' or event.key == 'escape':
            plt.close(self.fig)
        #~ else:
            #~ print(event.key)
    
    def onkeyrelease(self, event):
        if event.key == 'n':
            self.set_zero = False
    
    def relative_plot(self, mult, bounds=None, offset=False):
        delta_t = self.delta_t
        
        if bounds:
            lbound = self.zero_time - bounds[0]
            rbound = self.zero_time + bounds[-1]
        else:
            lbound = self.x_bounds[0]
            rbound = self.x_bounds[-1]

        t = np.arange(-self.zero_time+lbound, rbound-self.zero_time, delta_t) # seconds
        
        s = self.y[int((lbound - self.x[0])/delta_t):int((rbound - self.x[0])/delta_t)].shape[0]
        
        if t.shape[0] > s:
            t = t[0:s]
        #~ elif s > t.shape[0]:
            #~ s = s[0:t.shape[0]]
                
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        if offset:
            ax.plot(t*mult, self.y[int((lbound - self.x[0])/delta_t):int((rbound - self.x[0])/delta_t)] - self.y[self.zero_ind])
        else:
            ax.plot(t*mult, self.y[int((lbound - self.x[0])/delta_t):int((rbound - self.x[0])/delta_t)])
        
        ax.set_xlim(t[0]*mult, t[-1]*mult)
        
        return fig, ax
    
    def plot(self):
    
        if self.draw:

            self.span = SpanSelector(self.ax, self.onselect, 'horizontal', \
                                     useblit=True, rectprops=dict(alpha=0.5, \
                                     facecolor='red') )

            self.cid = self.fig.canvas.mpl_connect('button_release_event', \
                                                   self.onclick)
        
            self.kp = self.fig.canvas.mpl_connect('key_press_event', \
                                                  self.onkeypress)
        
            self.kr = self.fig.canvas.mpl_connect('key_release_event', \
                                                  self.onkeyrelease)


class ImagePlotter(object):
    def __init__(self, image_file, camera):
        self.image_file = image_file
        self.camera = camera


class RadarPlotter(object):
    def __init__(self, file_name):
        self.fileName = file_name
        self.radar = pyart.io.read(self.fileName)
        self.fields = self.radar.fields.keys()
        self.ICLRT_shift = (32e3, 61e3)  # Distance (x,y) in km from KJAX radar
        self.ICLRT_azimuth = 208.3  # Azimuth in degrees from KJAX radar
        self.display = None

    def setup_display(self, shift=None):
        if shift is None:
            shift = self.ICLRT_shift

        self.display = pyart.graph.RadarDisplay(self.radar, shift)

    def plot_ppi(self, field, sweep=0, fig=None, ax=None):
        if field in self.fields:
            if sweep <= self.radar.nsweeps:
                if self.display is None:
                    self.setup_display()

                self.display.plot_ppi(field, sweep=sweep, vmin=-25,
                                      vmax=75, fig=fig, ax=ax,
                                      title_flag=False,
                                      colorbar_label='dBZ',
                                      axislabels_flag=False)

    def plot_pseudo_rhi(self, field, azimuth=None, fig=None, ax=None):
        if azimuth is None:
            azimuth = self.ICLRT_azimuth

        if field in self.fields:
            if azimuth <= 360:
                if self.display is None:
                    self.setup_display()

                self.display.plot_azimuth_to_rhi(field, azimuth,
                                                 vmin=-25, vmax=75,
                                                 fig=fig, ax=ax,
                                                 title_flag=False,
                                                 colorbar_label='dBZ',
                                                 axislabels_flag=False)


class LMAPlotter(object):
    def __init__(self, lma_file):
        if not isinstance(lma_file, lma.LMAFile):
            lma_file = lma.LMAFile(lma_file)

        self.raw_data = lma_file.data
        self.filtered_data = self.raw_data

        self.cmap = cm.jet

        self.plot_data = {}
        self.plot_data_stack = []
        self.plot_x_stack = []
        self.plot_y_stack = []

        # Filter the data to default values
        self.filter_rc2()
        self.filter_num_stations()
        self.filter_alt()

        # Reset all default matplotlib figure keymaps
        mpl.rcParams['keymap.fullscreen'] = ''
        mpl.rcParams['keymap.back'] = ''
        mpl.rcParams['keymap.forward'] = ''
        mpl.rcParams['keymap.home'] = ''
        mpl.rcParams['keymap.zoom'] = ''

    def filter_rc2(self, rc2=5.0):
        """
        Filters the data to only show the points whose solution has the
        specified reduced chi squared value
        :param rc2:
        :return:
        """

        # Filter the data
        self.filtered_data = [s for s in self.filtered_data if s.rc2 <= rc2]

        # Update the plot data
        self.update_data()

    def filter_num_stations(self, num_stations=5.0):
        """
        Filters the data to only show the points whose solution is given by
        the specified number of stations.

        :param num_stations: number of stations that solutions must satisfy
        :return:
        """

        # Filter the data
        self.filtered_data = [s for s in self.filtered_data if
                              s.num_stations >= num_stations]

        # Update the plot data
        self.update_data()

    def filter_alt(self, alt=20E3):
        """
        Filters the data to only show the points that are below the specified
        altitude

        :param alt: maximum altitude for data
        :return:
        """

        # Filter the data
        self.filtered_data = [s for s in self.filtered_data if
                              s.xyz_coords[2] <= alt]

        # Update the plot data
        self.update_data()

    def filter_xy(self, xlims=[-20.0E3,20.0E3], ylims=[-20.0E3,20.0E3]):
        """
        Filters the data to only show the points that are within the specified
        limits xlims, ylims.

        :param xlims: a list with the limits for the x-axis
        :param ylims: a list with the limist for the y-axis
        :return:
        """
        # Get the order for xlims and ylims to be ascending
        xmin = min(xlims)
        xmax = max(xlims)
        xlims = [xmin, xmax]

        ymin = min(ylims)
        ymax = max(ylims)
        ylims = [ymin, ymax]

        # Filter the x axis
        self.filtered_data = [s for s in self.filtered_data if
                              s.xyz_coords[0] >= xlims[0]]

        self.filtered_data = [s for s in self.filtered_data if
                              s.xyz_coords[0] <= xlims[1]]

        # Filter the y axis
        self.filtered_data = [s for s in self.filtered_data if
                              s.xyz_coords[1] >= ylims[0]]

        self.filtered_data = [s for s in self.filtered_data if
                              s.xyz_coords[1] <= ylims[1]]

        # Update all other variables
        self.update_data()

    def filter_time(self, tlims):
        """
        Filters the data to only show the points that are within the specified
        time limits tlims.

        :param time: a list with the time limits as strings in the format
                     HH:MM:SS.SSSSSS
        :return:
        """
        # Convert the time limits to timedelta objects
        t0 = datetime.datetime.strptime(tlims[0], '%H:%M:%S.%f')
        dt0 = datetime.timedelta(hours=t0.hour, minutes=t0.minute,
                                seconds=t0.second, microseconds=t0.microsecond)

        t1 = datetime.datetime.strptime(tlims[1], '%H:%M:%S.%f')
        dt1 = datetime.timedelta(hours=t1.hour, minutes=t1.minute,
                                seconds=t1.second, microseconds=t1.microsecond)

        # Filter the data
        self.filtered_data = [s for s in self.filtered_data if
                              s.seconds_of_day >= dt0.total_seconds()]

        self.filtered_data = [s for s in self.filtered_data if
                              s.seconds_of_day <= dt1.total_seconds()]

        # Update all other variables
        self.update_data()

    def update_data(self):
        self.plot_data['t'] = np.array([s.time for s in self.filtered_data])
        self.plot_data['x'] = np.array([s.xyz_coords[0] for s in
                                        self.filtered_data])
        self.plot_data['y'] = np.array([s.xyz_coords[1] for s in
                                        self.filtered_data])
        self.plot_data['z'] = np.array([s.xyz_coords[2] for s in
                                        self.filtered_data])
        self.plot_data['seconds_of_day'] = np.array([s.seconds_of_day for s in
                                            self.filtered_data])

        # print('t shape', self.plot_data['t'].shape)
        # print('x shape', self.plot_data['x'].shape)
        # print('y shape', self.plot_data['y'].shape)
        # print('z shape', self.plot_data['z'].shape)
        # print('secs shape', self.plot_data['seconds_of_day'].shape)
        # print(' ')

    def scale_data(self, mult=1):
        self.plot_data['x'] *= mult
        self.plot_data['z'] *= mult
        self.plot_data['y'] *= mult

    def set_cmap(self, cmap):
        if cmap == 'jet':
            self.cmap = cm.jet
        elif cmap == 'grey':
            self.cmap = cm.gray

    def reset_filters(self):
        """
        Resets the data to the unfiltered raw data.
        :return:
        """
        self.filtered_data = self.raw_data
        self.plot_data = {}

    def sort_time(self):
        """
        Sorts all the plot_data arrays by time in ascending order
        :return:
        """
        indices = np.argsort(self.plot_data['seconds_of_day'])

        self.plot_data['t'] = self.plot_data['t'][indices]
        self.plot_data['x'] = self.plot_data['x'][indices]
        self.plot_data['y'] = self.plot_data['y'][indices]
        self.plot_data['z'] = self.plot_data['z'][indices]
        self.plot_data['seconds_of_day'] = self.plot_data['seconds_of_day'][indices]

    def alt_histogram(self):
        h = self.plot_data['z']
        bins = np.arange(np.min(h), np.max(h), 100)
        hist, bin_edges = np.histogram(h, bins)
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

        return hist, bin_centers, len(h)

    def date_format_major(self, x, pos=None):
        x = dates.num2date(x)

        if pos == 0 or pos==-1:
            fmt = '%H:%M:%S.%f'

        else:
            fmt = ':%S.%f'

        label = x.strftime(fmt)
        ind_dot = label.find('.')
        label = label[:ind_dot+5]
        label = label.rstrip('0')
        label = label.rstrip('.')

        return label

    def date_format_minor(self, x, pos=None):
        x = dates.num2date(x)

        fmt = ':%S.%f'

        label = x.strftime(fmt)
        ind_dot = label.find('.')
        label = label[:ind_dot+5]
        label = label.rstrip('0')
        label = label.rstrip('.')

        return label

    def get_eng_units(self, number):
        """
        Returns the factor and label of the precision of the number passed
        in engineering units. This is useful when modifying plot axis labels.

        Say you have a time array (units of seconds) and you are plotting
        only some fraction of that time. You don't want the axis ticks to be
        0.00XX but instead XX. Then you would use this and multiply your time
        array by 1/factor returned by this function.

        :param number: Number to be converted into engineering units
        :return: a tuple with the factor to convert the number into engineering
                 units and the text label for those units
        """
        units = {
            -12: 1E-12,  # pico
            -9: 1E-9,    # nano
            -6: 1E-6,    # micro
            -3: 1E-3,    # milli
             0: 1,       # unity
             3: 1E3,     # kilo
             6: 1E6}     # mega

        labels = {
            -12: 'p',
            -9: 'n',
            -6: '$\mu$',
            -3: 'm',
             0: '',
             3: 'k',
             6: 'M'
        }

        if number != 0:
            pow10 = int(math.floor(math.log10(number) / 3) * 3)
        else:
            pow10 = 0

        pow10 = min(pow10, max(units.keys()))
        pow10 = max(pow10, min(units.keys()))

        return units[pow10], labels[pow10]

    def get_date_format_major(self, time):
        tend = (time[-1] - time[0]).total_seconds()
        tend *= 1E2
        dt = 10
        maj_ticks = []
        min_ticks = []

        for i in range(int(tend)):
            value = (i+1) * dt
            if value % 100 == 0:
                maj_ticks.append(value)
            else:
                min_ticks.append(value)

        return maj_ticks, min_ticks

    def get_plot_data(self, x, y, x_old, x_new, y_old, y_new):
        """
        Gets the data for the current plot
        :param x: entire data for x
        :param y: entire data for y
        :param x_old: old limits
        :param x_new: new limits
        :param y_old: old limits
        :param y_new: new limits
        :return:
        """
        temp_x = x
        temp_y = y
        temp_t = self.plot_data['t']

        if x_old is not None:
            # Sort by x and get old x limits
            temp_t = temp_t[np.argsort(temp_x)]
            temp_y = temp_y[np.argsort(temp_x)]
            temp_x = temp_x[np.argsort(temp_x)]

            indmin, indmax = np.searchsorted(temp_x, x_old)
            indmax = min(len(temp_x)-1, indmax)

            temp_x = temp_x[indmin:indmax]
            temp_y = temp_y[indmin:indmax]
            temp_t = temp_t[indmin:indmax]

            # Sort by y and get old y limits
            temp_t = temp_t[np.argsort(temp_y)]
            temp_x = temp_x[np.argsort(temp_y)]
            temp_y = temp_y[np.argsort(temp_y)]

            indmin, indmax = np.searchsorted(temp_y, (y_old[0], y_old[1]))
            indmax = min(len(temp_y)-1, indmax)

            temp_x = temp_x[indmin:indmax]
            temp_y = temp_y[indmin:indmax]
            temp_t = temp_t[indmin:indmax]

        # Sort by x and get new  x limits
        temp_t = temp_t[np.argsort(temp_x)]
        temp_y = temp_y[np.argsort(temp_x)]
        temp_x = temp_x[np.argsort(temp_x)]

        indmin, indmax = np.searchsorted(temp_x, x_new)
        indmax = min(len(temp_x)-1, indmax)

        temp_x = temp_x[indmin:indmax]
        temp_y = temp_y[indmin:indmax]
        temp_t = temp_t[indmin:indmax]

        # Sort by y and get new y limits
        temp_t = temp_t[np.argsort(temp_y)]
        temp_x = temp_x[np.argsort(temp_y)]
        temp_y = temp_y[np.argsort(temp_y)]

        indmin, indmax = np.searchsorted(temp_y, (y_new[0], y_new[1]))
        indmax = min(len(temp_y)-1, indmax)

        temp_x = temp_x[indmin:indmax]
        temp_y = temp_y[indmin:indmax]
        temp_t = temp_t[indmin:indmax]

        try:
            if isinstance(temp_x[0], datetime.datetime):
                for i in range(len(temp_x)):
                    temp_x[i] = dates.date2num(temp_x[i])

        except IndexError:
            raise

        # Sort by time one last time
        temp_y = temp_y[np.argsort(temp_t)]
        temp_x = temp_x[np.argsort(temp_t)]
        temp_t = temp_t[np.argsort(temp_t)]

        return temp_x, temp_y, temp_t

    def plot_alt_t(self, lims=[0, 20e3]):
        self.plot_x_stack = []
        self.plot_y_stack = []

        lims = [lims[0]*1e-3, lims[-1]*1e-3]

        self.fig_alt_t = plt.figure()
        self.ax_alt_t = self.fig_alt_t.add_subplot(111)

        colors = self.cmap(np.linspace(0, 1, len(self.plot_data['t'])))
        self.scat_alt_t = self.ax_alt_t.scatter(self.plot_data['t'],
                              self.plot_data['z']*1E-3,
                              marker='.', c=colors,
                              s=30, lw=0)

        self.ax_alt_t.set_ylabel('Altitude (km)')
        self.ax_alt_t.set_xlabel('Time (s)')

        self.ax_alt_t.set_ylim(lims)
        self.ax_alt_t.set_xlim([self.plot_data['t'][0],
                                self.plot_data['t'][-1]])

        self.ax_alt_t.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))
        self.ax_alt_t.xaxis.set_minor_formatter(mpl.ticker.FuncFormatter(self.date_format_minor))

        self.ax_alt_t.xaxis.set_major_locator(mpl.ticker.LinearLocator(5))
        self.ax_alt_t.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(self.date_format_major))

        # for label in self.ax_alt_t.xaxis.get_ticklabels(minor=True):
        #     label.set_rotation(30)
        #
        # for label in self.ax_alt_t.xaxis.get_ticklabels(minor=False):
        #     label.set_rotation(30)

        # Define event handlers
        self.span_alt_t = SpanSelector(self.ax_alt_t, self.onselect_alt_t,
                                       'horizontal', useblit=True,
                                       rectprops=dict(alpha=0.2,
                                       facecolor='red'))
        self.span_alt_t_v = SpanSelector(self.ax_alt_t, self.onselect_alt_t_v,
                                       'vertical', useblit=True,
                                       rectprops=dict(alpha=0.2,
                                       facecolor='red'))

        self.span_alt_t_v.visible = False

        self.cid_alt_t = self.fig_alt_t.canvas.mpl_connect(
                                                    'button_release_event',
                                                    self.onclick_alt_t)

        self.kp_alt_t = self.fig_alt_t.canvas.mpl_connect('key_press_event',
                                                       self.onkeypress_alt_t)

        self.kr_alt_t = self.fig_alt_t.canvas.mpl_connect('key_release_event',
                                                       self.onkeyrelease_alt_t)

    def onselect_alt_t(self, xmin, xmax):
        if xmin == xmax:
            return True

        # Epoch time, used for num2date
        t = datetime.datetime(1970, 1, 1)

        # Save the current graph's limits
        xmin_old = self.ax_alt_t.get_xlim()[0]
        xmax_old = self.ax_alt_t.get_xlim()[1]

        ymin_old = self.ax_alt_t.get_ylim()[0]
        ymax_old = self.ax_alt_t.get_ylim()[1]

        # Convert xmin_old to datetime
        a = dates.num2date(xmin_old)
        xmin_old = datetime.datetime(a.year, a.month, a.day, a.hour, a.minute,
            a.second, a.microsecond)

        # Convert xmax_old to datetime
        a = dates.num2date(xmax_old)
        xmax_old = datetime.datetime(a.year, a.month, a.day, a.hour, a.minute,
            a.second, a.microsecond)

        # Get new limits and redraw
        # Convert xmin to datetime
        a = dates.num2date(xmin)
        xmin = datetime.datetime(a.year, a.month, a.day, a.hour, a.minute,
            a.second, a.microsecond)

        # Convert xmax to datetime
        a = dates.num2date(xmax)
        xmax = datetime.datetime(a.year, a.month, a.day, a.hour, a.minute,
            a.second, a.microsecond)

        # if not self.plot_x_stack:
        #     indmin, indmax = np.searchsorted(self.plot_data['t'], (xmin_old, xmax_old))
        #     temp_t = self.plot_data['t'][indmin:indmax]
        #
        # else:
        #     temp_t = self.plot_data['t']
        #
        # if not self.plot_y_stack:
        #     indmin, indmax = np.searchsorted(self.plot_data['z'], (ymin_old, ymax_old))
        #     temp_z = self.plot_data['z'][indmin:indmax]
        #
        # else:
        #     temp_z = self.plot_data['z']
        #
        # # Find the indices for xmin, xmax
        # indmin, indmax = np.searchsorted(temp_t, (xmin, xmax))
        # indmax = min(len(self.plot_data['t'])-1, indmax)
        #
        # if (indmax - indmin) < 2:
        #     return True
        #
        # thisx = temp_t[indmin:indmax]
        # thisy = temp_z[indmin:indmax]

        try:
            if not self.plot_x_stack:
                thisx, thisy, thist = self.get_plot_data(self.plot_data['t'], self.plot_data['z'], None, [xmin, xmax], None, [ymin_old*1e3, ymax_old*1e3])
            else:
                thisx, thisy, thist = self.get_plot_data(self.plot_data['t'], self.plot_data['z'], self.plot_x_stack[-1], [xmin, xmax], [self.plot_y_stack[-1][0]*1e3, self.plot_y_stack[-1][1]*1e3], [ymin_old*1e3, ymax_old*1e3])

        except IndexError:
            return True

        self.update_graph_alt_t(thisx, thisy, thist)

        # Append values to stack
        self.plot_x_stack.append([xmin_old, xmax_old])
        self.plot_y_stack.append([ymin_old, ymax_old])

        # Re-draw figure
        self.fig_alt_t.canvas.draw()

    def onselect_alt_t_v(self, ymin, ymax):
        if ymin == ymax:
            return True

        # Save the current graph's limits
        xmin_old = self.ax_alt_t.get_xlim()[0]
        xmax_old = self.ax_alt_t.get_xlim()[1]

        ymin_old = self.ax_alt_t.get_ylim()[0]
        ymax_old = self.ax_alt_t.get_ylim()[1]

        # Convert xmin_old to datetime
        a = dates.num2date(xmin_old)
        xmin_old = datetime.datetime(a.year, a.month, a.day, a.hour, a.minute,
            a.second, a.microsecond)

        # Convert xmax_old to datetime
        a = dates.num2date(xmax_old)
        xmax_old = datetime.datetime(a.year, a.month, a.day, a.hour, a.minute,
            a.second, a.microsecond)

        # if not self.plot_x_stack:
        #     xmin_old = self.plot_x_stack[-2][0]
        #     xmax_old = self.plot_x_stack[-2][1]
        #     indmin, indmax = np.searchsorted(self.plot_data['t'], (xmin_old, xmax_old))
        #     temp_x = self.plot_data['t'][indmin:indmax]
        #
        # else:
        #     temp_x = self.plot_data['t']
        #
        # if not self.plot_y_stack:
        #     indmin, indmax = np.searchsorted(self.plot_data['z'], (ymin_old, ymax_old))
        #     temp_y = self.plot_data['z'][indmin:indmax]*1e-3
        #
        # else:
        #     temp_y = self.plot_data['z']*1e-3
        #
        # # Find the indices for ymin, ymax
        # # temp_x = self.plot_data['t']
        # # temp_y = self.plot_data['z']*1e-3
        #
        # temp_x = temp_x[np.argsort(temp_y)]
        # temp_y = temp_y[np.argsort(temp_y)]
        #
        # indmin, indmax = np.searchsorted(temp_y, (ymin, ymax))
        # indmax = min(len(temp_y)-1, indmax)
        #
        # if (indmax - indmin) < 2:
        #     return True
        #
        # thisx = temp_x[indmin:indmax]
        # thisy = temp_y[indmin:indmax]

        try:
            if not self.plot_x_stack:
                thisx, thisy, thist = self.get_plot_data(self.plot_data['t'], self.plot_data['z'], None, [xmin_old, xmax_old], None, [ymin*1e3, ymax*1e3])
            else:
                thisx, thisy, thist = self.get_plot_data(self.plot_data['t'], self.plot_data['z'], self.plot_x_stack[-1], [xmin_old, xmax_old], [self.plot_y_stack[-1][0]*1e3, self.plot_y_stack[-1][1]*1e3], [ymin*1e3, ymax*1e3])

        except IndexError:
            return True

        self.update_graph_alt_t(thisx, thisy, thist)

        # Append values to stack
        self.plot_x_stack.append([xmin_old, xmax_old])
        self.plot_y_stack.append([ymin_old, ymax_old])

        # Re-draw figure
        self.fig_alt_t.canvas.draw()

    def onclick_alt_t(self, event):
        if event.button == 3 and (event.inaxes is self.ax_alt_t or self.synced):

            if self.plot_x_stack:
                # # Get old limits from stacks
                # xmin = self.plot_x_stack[-1][0]
                # xmax = self.plot_x_stack[-1][1]
                #
                # self.plot_x_stack = self.plot_x_stack[:-1]
                #
                # # Set new limits and redraw
                # indmin, indmax = np.searchsorted(self.plot_data['t'],
                #                                  (xmin, xmax))
                # indmax = min(len(self.plot_data['t'])-1, indmax)
                #
                # thisx = self.plot_data['t'][indmin:indmax]
                # self.ax_alt_t.set_xlim(thisx[0], thisx[-1])

                thisx, thisy, thist = self.get_plot_data(self.plot_data['t'], self.plot_data['z'], self.plot_x_stack[-1], self.plot_x_stack[-1], [self.plot_y_stack[-1][0]*1e3, self.plot_y_stack[-1][1]*1e3], [self.plot_y_stack[-1][0]*1e3, self.plot_y_stack[-1][1]*1e3])

                self.update_graph_alt_t(thisx, thisy, thist)

                self.plot_x_stack = self.plot_x_stack[:-1]

                self.fig_alt_t.canvas.draw()

    def onkeypress_alt_t(self, event):
        if event.key == 'r':
            if self.plot_x_stack:
                # # Get initial limits from stacks
                # xmin = self.plot_x_stack[0][0]
                # xmax = self.plot_x_stack[0][1]
                #
                # self.plot_x_stack = []
                #
                # # Set new limits and redraw
                # indmin, indmax = np.searchsorted(self.plot_data['t'],
                #                                  (xmin, xmax))
                # indmax = min(len(self.plot_data['t'])-1, indmax)
                #
                # thisx = self.plot_data['t'][indmin:indmax]
                # self.ax_alt_t.set_xlim(thisx[0], thisx[-1])
                #
                # max_y = -np.inf
                # min_y = np.inf
                #
                # mx_y = self.plot_data['z'][indmin:indmax].max()
                # mn_y = self.plot_data['z'][indmin:indmax].min()
                #
                # if mx_y > max_y:
                #     max_y = mx_y
                #
                # if mn_y < min_y:
                #     min_y = mn_y
                #
                # max_y = max_y + (max_y - min_y)*.1
                # min_y = min_y - (max_y - min_y)*.1
                #
                # self.ax_alt_t.set_ylim(min_y*1E-3, max_y*1E-3)
                #
                # self.fig_alt_t.canvas.draw()

                thisx, thisy, thist = self.get_plot_data(self.plot_data['t'], self.plot_data['z'], self.plot_x_stack[0], self.plot_x_stack[0], [self.plot_y_stack[0][0]*1e3, self.plot_y_stack[0][1]*1e3], [self.plot_y_stack[0][0]*1e3, self.plot_y_stack[0][1]*1e3])

                self.update_graph_alt_t(thisx, thisy, thist)

                self.plot_x_stack = []

                self.fig_alt_t.canvas.draw()

        elif event.key == 'y':
            self.span_alt_t.visible = False
            self.span_alt_t_v.visible = True

        elif event.key == ' ' or event.key == 'escape':
            plt.close(self.fig_alt_t)

    def onkeyrelease_alt_t(self, event):
        if event.key == 'y':
            self.span_alt_t.visible = True
            self.span_alt_t_v.visible = False

    def update_graph_alt_t(self, thisx, thisy, thist):
        thisy *= 1e-3

        data = np.hstack((thisx[:, np.newaxis], thisy[:, np.newaxis]))
        self.scat_alt_t.set_offsets(data)
        colors = self.cmap(np.linspace(0, 1, len(thist)))
        self.scat_alt_t.set_color(colors)

        max_y = -np.inf
        min_y = np.inf

        mx_y = np.max(thisy)
        mn_y = np.min(thisy)

        if mx_y > max_y:
            max_y = mx_y

        if mn_y < min_y:
            min_y = mn_y

        max_y = max_y + (max_y - min_y)*.1

        max_x = -np.inf
        min_x = np.inf

        mx_x = np.max(thisx)
        mn_x = np.min(thisx)

        if mx_x > max_x:
            max_x = mx_x

        if mn_x < min_x:
            min_x = mn_x

        max_x = max_x + (max_x - min_x)*.01
        min_x = min_x - (max_x - min_x)*.01

        # Set plot's limits
        self.ax_alt_t.set_ylim(min_y, max_y)
        self.ax_alt_t.set_xlim(min_x, max_x)

        self.ax_alt_t.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))
        self.ax_alt_t.xaxis.set_minor_formatter(mpl.ticker.FuncFormatter(self.date_format_minor))

        self.ax_alt_t.xaxis.set_major_locator(mpl.ticker.LinearLocator(5))
        self.ax_alt_t.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(self.date_format_major))

        # for label in self.ax_alt_t.xaxis.get_ticklabels(minor=True):
        #     label.set_rotation(30)
        #
        # for label in self.ax_alt_t.xaxis.get_ticklabels(minor=False):
        #     label.set_rotation(30)

    def plot_plan(self, fig=None, ax=None, xlims=[-20E3, 20E3],
                  ylims=[-20E3, 20E3]):
        self.plot_x_stack = []
        self.plot_y_stack = []

        if fig is None or ax is None:
            self.fig_plan = plt.figure()
            self.ax_plan = self.fig_plan.add_subplot(111)

        else:
            self.fig_plan = fig
            self.ax_plan = ax

        self.scat_plan = self.ax_plan.scatter(self.plot_data['x'],
                             self.plot_data['y'], marker='.',
                             c=self.plot_data['seconds_of_day'],
                             cmap=self.cmap, s=30, lw=0)

        self.ax_plan.set_xlim(xlims)
        self.ax_plan.set_ylim(ylims)

        self.ax_plan.set_ylabel('South - North')
        self.ax_plan.set_xlabel('West - East')

        self.rect_sel_plan = RectangleSelector(self.ax_plan,
                                               self.onselect_plan,
                                               button=[1],
                                               drawtype='box',
                                               rectprops=dict(alpha=0.2,
                                                              facecolor='red',
                                                              edgecolor='red',
                                                              linewidth=2))

        self.cid_plan = self.fig_plan.canvas.mpl_connect(
                                                        'button_release_event',
                                                        self.onclick_plan)

        self.kp_plan = self.fig_plan.canvas.mpl_connect('key_press_event',
                                                        self.onkeypress_plan)

    def onselect_plan(self, eclick, erelease):
        xmin_old = self.ax_plan.get_xlim()[0]
        xmax_old = self.ax_plan.get_xlim()[1]

        ymin_old = self.ax_plan.get_ylim()[0]
        ymax_old = self.ax_plan.get_ylim()[1]

        # print(self.plot_x_stack)
        # print(self.plot_y_stack)

        x_start = eclick.xdata
        y_start = eclick.ydata

        x_end = erelease.xdata
        y_end = erelease.ydata

        if x_start == x_end or y_start == y_end:
            return True

        xmin = np.min([x_start, x_end])
        xmax = np.max([x_start, x_end])

        ymin = np.min([y_start, y_end])
        ymax = np.max([y_start, y_end])

        # temp_x = self.plot_data['x']
        # temp_y = self.plot_data['y']
        #
        # # Sort both arrays wrt x
        # temp_y = temp_y[np.argsort(temp_x)]
        # temp_x = temp_x[np.argsort(temp_x)]
        #
        # # Find the indices for xmin, xmax
        # x_indmin, x_indmax = np.searchsorted(temp_x, (xmin, xmax))
        # x_indmax = min(len(temp_x)-1, x_indmax)
        #
        # temp_x = temp_x[x_indmin:x_indmax]
        # temp_y = temp_y[x_indmin:x_indmax]
        #
        # # Sort both arrays wrt y
        # temp_x = temp_x[np.argsort(temp_y)]
        # temp_y = temp_y[np.argsort(temp_y)]
        #
        # # Find the indices for ymin, ymax
        # y_indmin, y_indmax = np.searchsorted(temp_y, (ymin, ymax))
        # y_indmax = min(len(temp_y)-1, y_indmax)
        #
        # print(y_indmin, y_indmax)
        #
        # temp_x = temp_x[y_indmin:y_indmax]
        # temp_y = temp_y[y_indmin:y_indmax]
        #
        # thisx = temp_x
        # thisy = temp_y

        if not self.plot_x_stack:
            thisx, thisy, thist = self.get_plot_data(self.plot_data['x'], self.plot_data['y'], None, [xmin, xmax], None, [ymin, ymax])
        else:
            thisx, thisy, thist = self.get_plot_data(self.plot_data['x'], self.plot_data['y'], self.plot_x_stack[-1], [xmin, xmax], self.plot_y_stack[-1], [ymin, ymax])

        self.update_graph_plan(thisx, thisy, thist)
        # self.scat_plan.set_offsets([thisx, thisy])
        # Set plot's limits
        # try:
        #     self.ax_plan.set_xlim(np.min(thisx), np.max(thisx))
        #     self.ax_plan.set_ylim(np.min(thisy), np.max(thisy))
        # except ValueError:
        #     print("Error")
        #     return True

        self.plot_x_stack.append([xmin_old, xmax_old])
        self.plot_y_stack.append([ymin_old, ymax_old])

        # Re-draw figure
        self.fig_plan.canvas.draw()

    def onclick_plan(self, event):
        if event.button == 3 and (event.inaxes is self.ax_plan or self.synced):

            # print(self.plot_x_stack)
            # print(self.plot_y_stack)
            if self.plot_x_stack:
                # Get old limits from stacks
                xmin = self.plot_x_stack[-1][0]
                xmax = self.plot_x_stack[-1][1]

                ymin = self.plot_y_stack[-1][0]
                ymax = self.plot_y_stack[-1][1]

                # # Set new limits and redraw
                # temp_x = self.plot_data['x']
                # temp_y = self.plot_data['y']
                #
                # # Sort both arrays wrt x
                # temp_y = temp_y[np.argsort(temp_x)]
                # temp_x = temp_x[np.argsort(temp_x)]
                #
                # # Find the indices for xmin, xmax
                # x_indmin, x_indmax = np.searchsorted(temp_x, (xmin, xmax))
                # x_indmax = min(len(temp_x)-1, x_indmax)
                #
                # # if (x_indmax - x_indmin) < 2:
                # #     return True
                #
                # temp_x = temp_x[x_indmin:x_indmax]
                # temp_y = temp_y[x_indmin:x_indmax]
                #
                # # Sort both arrays wrt y
                # temp_x = temp_x[np.argsort(temp_y)]
                # temp_y = temp_y[np.argsort(temp_y)]
                #
                # # Find the indices for ymin, ymax
                # y_indmin, y_indmax = np.searchsorted(temp_y, (ymin, ymax))
                # y_indmax = min(len(temp_y)-1, y_indmax)
                #
                # # if (y_indmax - y_indmin) < 2:
                # #     return True
                #
                # temp_x = temp_x[y_indmin:y_indmax]
                # temp_y = temp_y[y_indmin:y_indmax]
                #
                # thisx = temp_x
                # thisy = temp_y

                if not self.plot_x_stack:
                    thisx, thisy, thist = self.get_plot_data(self.plot_data['x'], self.plot_data['y'], None, [xmin, xmax], None, [ymin, ymax])
                else:
                    thisx, thisy, thist = self.get_plot_data(self.plot_data['x'], self.plot_data['y'], self.plot_x_stack[-1], [xmin, xmax], self.plot_y_stack[-1], [ymin, ymax])

                self.update_graph_plan(thisx, thisy, thist)

                # # self.scat_plan.set_offsets([thisx, thisy])
                # # Set plot's limits
                # self.ax_plan.set_xlim(np.min(thisx), np.max(thisx))
                # self.ax_plan.set_ylim(np.min(thisy), np.max(thisy))

                self.plot_x_stack = self.plot_x_stack[:-1]
                self.plot_y_stack = self.plot_y_stack[:-1]

                self.fig_plan.canvas.draw()

    def onkeypress_plan(self, event):
        if event.key == 'r':
            if self.plot_x_stack:
                # Get initial limits from stacks
                xmin = self.plot_x_stack[0][0]
                xmax = self.plot_x_stack[0][1]

                ymin = self.plot_y_stack[0][0]
                ymax = self.plot_y_stack[0][1]

                # Set new limits and redraw
                # temp_x = self.plot_data['x']
                # temp_y = self.plot_data['y']
                #
                # # Sort both arrays wrt x
                # temp_y = temp_y[np.argsort(temp_x)]
                # temp_x = temp_x[np.argsort(temp_x)]
                #
                # # Find the indices for xmin, xmax
                # x_indmin, x_indmax = np.searchsorted(temp_x, (xmin, xmax))
                # x_indmax = min(len(temp_x)-1, x_indmax)
                #
                # # if (x_indmax - x_indmin) < 2:
                # #     return True
                #
                # temp_x = temp_x[x_indmin:x_indmax]
                # temp_y = temp_y[x_indmin:x_indmax]
                #
                # # Sort both arrays wrt y
                # temp_x = temp_x[np.argsort(temp_y)]
                # temp_y = temp_y[np.argsort(temp_y)]
                #
                # # Find the indices for ymin, ymax
                # y_indmin, y_indmax = np.searchsorted(temp_y, (ymin, ymax))
                # y_indmax = min(len(temp_y)-1, y_indmax)
                #
                # # if (y_indmax - y_indmin) < 2:
                # #     return True
                #
                # temp_x = temp_x[y_indmin:y_indmax]
                # temp_y = temp_y[y_indmin:y_indmax]
                #
                # thisx = temp_x
                # thisy = temp_y

                if not self.plot_x_stack:
                    thisx, thisy, thist = self.get_plot_data(self.plot_data['x'], self.plot_data['y'], None, [xmin, xmax], None, [ymin, ymax])
                else:
                    thisx, thisy, thist = self.get_plot_data(self.plot_data['x'], self.plot_data['y'], self.plot_x_stack[-1], [xmin, xmax], self.plot_y_stack[-1], [ymin, ymax])

                self.update_graph_plan(thisx, thisy, thist)

                # # self.scat_plan.set_offsets([thisx, thisy])
                # # Set plot's limits
                # self.ax_plan.set_xlim(np.min(thisx), np.max(thisx))
                # self.ax_plan.set_ylim(np.min(thisy), np.max(thisy))

                self.plot_x_stack = []
                self.plot_y_stack = []

                self.fig_plan.canvas.draw()

        elif event.key == ' ' or event.key == 'escape':
            plt.close(self.fig_plan)

    def update_graph_plan(self, thisx, thisy, thist):
        data = np.hstack((thisx[:, np.newaxis], thisy[:, np.newaxis]))
        self.scat_plan.set_offsets(data)
        colors = cm.rainbow(np.linspace(0, 1, len(thist)))
        self.scat_plan.set_color(colors)

        max_y = -np.inf
        min_y = np.inf

        mx_y = np.max(thisy)
        mn_y = np.min(thisy)

        if mx_y > max_y:
            max_y = mx_y

        if mn_y < min_y:
            min_y = mn_y

        max_y = max_y + (max_y - min_y)*.1

        max_x = -np.inf
        min_x = np.inf

        mx_x = np.max(thisx)
        mn_x = np.min(thisx)

        if mx_x > max_x:
            max_x = mx_x

        if mn_x < min_x:
            min_x = mn_x

        max_x = max_x + (max_x - min_x)*.1
        min_x = min_x - (max_x - min_x)*.1

        # Set plot's limits
        self.ax_plan.set_ylim(min_y, max_y)
        self.ax_plan.set_xlim(min_x, max_x)

    def plot_proj(self, projection='NS', lims=(-20E3, 20E3), zlims=(0, 20E3)):
        self.plot_x_stack = []
        self.plot_y_stack = []
        self.projection = projection

        self.fig_proj = plt.figure()
        self.ax_proj = self.fig_proj.add_subplot(111)

        if self.projection == 'NS':
            # This is the yz-plane
            self.scat_proj = self.ax_proj.scatter(self.plot_data['y'],
                                 self.plot_data['z'], marker='.',
                                 c=self.plot_data['seconds_of_day'],
                                 cmap=self.cmap, s=30, lw=0)
            self.ax_proj.set_xlim(lims)
            self.ax_proj.set_ylim(zlims)
            self.ax_proj.set_xlabel('South - North')
            self.ax_proj.set_ylabel('Altitude (m)')

        elif self.projection == 'EW':
            # This is the xz-plane
            self.scat_proj = self.ax_proj.scatter(self.plot_data['x'],
                                 self.plot_data['z'], marker='.',
                                 c=self.plot_data['seconds_of_day'],
                                 cmap=self.cmap, s=30, lw=0)
            self.ax_proj.set_xlim(lims)
            self.ax_proj.set_ylim(zlims)
            self.ax_proj.set_xlabel('West - East')
            self.ax_proj.set_ylabel('Altitude (m)')

        else:
            plt.close(self.fig_proj)
            return True

        self.rect_sel_proj = RectangleSelector(self.ax_proj,
                                               self.onselect_proj,
                                               button=[1],
                                               drawtype='box',
                                               rectprops=dict(alpha=0.2,
                                                              facecolor='red',
                                                              edgecolor='red',
                                                              linewidth=2))

        self.cid_proj = self.fig_proj.canvas.mpl_connect(
                                                        'button_release_event',
                                                        self.onclick_proj)

        self.kp_proj = self.fig_proj.canvas.mpl_connect('key_press_event',
                                                        self.onkeypress_proj)

    def onselect_proj(self, eclick, erelease):
        xmin_old = self.ax_proj.get_xlim()[0]
        xmax_old = self.ax_proj.get_xlim()[1]

        ymin_old = self.ax_proj.get_ylim()[0]
        ymax_old = self.ax_proj.get_ylim()[1]

        x_start = eclick.xdata
        y_start = eclick.ydata

        x_end = erelease.xdata
        y_end = erelease.ydata

        if x_start == x_end or y_start == y_end:
            return True

        xmin = np.min([x_start, x_end])
        xmax = np.max([x_start, x_end])

        ymin = np.min([y_start, y_end])
        ymax = np.max([y_start, y_end])

        temp_y = self.plot_data['z']

        if self.projection == 'NS':
            temp_x = self.plot_data['y']
        else:
            temp_x = self.plot_data['x']

        # # Sort both arrays wrt x
        # temp_y = temp_y[np.argsort(temp_x)]
        # temp_x = temp_x[np.argsort(temp_x)]
        #
        # # Find the indices for xmin, xmax
        # x_indmin, x_indmax = np.searchsorted(temp_x, (xmin, xmax))
        # x_indmax = min(len(temp_x)-1, x_indmax)
        #
        # # if (x_indmax - x_indmin) < 2:
        # #     return True
        #
        # temp_x = temp_x[x_indmin:x_indmax]
        # temp_y = temp_y[x_indmin:x_indmax]
        #
        # # Sort both arrays wrt y
        # temp_x = temp_x[np.argsort(temp_y)]
        # temp_y = temp_y[np.argsort(temp_y)]
        #
        # # Find the indices for ymin, ymax
        # y_indmin, y_indmax = np.searchsorted(temp_y, (ymin, ymax))
        # y_indmax = min(len(temp_y)-1, y_indmax)
        #
        # # if (y_indmax - y_indmin) < 2:
        # #     return True
        #
        # temp_x = temp_x[y_indmin:y_indmax]
        # temp_y = temp_y[y_indmin:y_indmax]
        #
        # thisx = temp_x
        # thisy = temp_y

        if not self.plot_x_stack:
            thisx, thisy, thist = self.get_plot_data(self.plot_data['x'], self.plot_data['y'], None, [xmin, xmax], None, [ymin, ymax])
        else:
            thisx, thisy, thist = self.get_plot_data(self.plot_data['x'], self.plot_data['y'], self.plot_x_stack[-1], [xmin, xmax], self.plot_y_stack[-1], [ymin, ymax])

        self.update_graph_proj(thisx, thisy, thist)

        # # self.scat_plan.set_offsets([thisx, thisy])
        # # Set plot's limits
        # self.ax_proj.set_xlim(np.min(thisx), np.max(thisx))
        # self.ax_proj.set_ylim(np.min(thisy), np.max(thisy))

        self.plot_x_stack.append([xmin_old, xmax_old])
        self.plot_y_stack.append([ymin_old, ymax_old])

        # Re-draw figure
        self.fig_proj.canvas.draw()

    def onclick_proj(self, event):
        if event.button == 3 and (event.inaxes is self.ax_proj or self.synced):

            # print(self.plot_x_stack)
            # print(self.plot_y_stack)
            if self.plot_x_stack:
                # Get old limits from stacks
                xmin = self.plot_x_stack[-1][0]
                xmax = self.plot_x_stack[-1][1]

                ymin = self.plot_y_stack[-1][0]
                ymax = self.plot_y_stack[-1][1]

                # Set new limits and redraw
                temp_y = self.plot_data['z']

                if self.projection == 'NS':
                    temp_x = self.plot_data['y']
                else:
                    temp_x = self.plot_data['x']

                # # Sort both arrays wrt x
                # temp_y = temp_y[np.argsort(temp_x)]
                # temp_x = temp_x[np.argsort(temp_x)]
                #
                # # Find the indices for xmin, xmax
                # x_indmin, x_indmax = np.searchsorted(temp_x, (xmin, xmax))
                # x_indmax = min(len(temp_x)-1, x_indmax)
                #
                # # if (x_indmax - x_indmin) < 2:
                # #     return True
                #
                # temp_x = temp_x[x_indmin:x_indmax]
                # temp_y = temp_y[x_indmin:x_indmax]
                #
                # # Sort both arrays wrt y
                # temp_x = temp_x[np.argsort(temp_y)]
                # temp_y = temp_y[np.argsort(temp_y)]
                #
                # # Find the indices for ymin, ymax
                # y_indmin, y_indmax = np.searchsorted(temp_y, (ymin, ymax))
                # y_indmax = min(len(temp_y)-1, y_indmax)
                #
                # # if (y_indmax - y_indmin) < 2:
                # #     return True
                #
                # temp_x = temp_x[y_indmin:y_indmax]
                # temp_y = temp_y[y_indmin:y_indmax]
                #
                # thisx = temp_x
                # thisy = temp_y

                if not self.plot_x_stack:
                    thisx, thisy, thist = self.get_plot_data(self.plot_data['x'], self.plot_data['y'], None, [xmin, xmax], None, [ymin, ymax])
                else:
                    thisx, thisy, thist = self.get_plot_data(self.plot_data['x'], self.plot_data['y'], self.plot_x_stack[-1], [xmin, xmax], self.plot_y_stack[-1], [ymin, ymax])

                self.update_graph_proj(thisx, thisy, thist)

                # # self.scat_plan.set_offsets([thisx, thisy])
                # # Set plot's limits
                # self.ax_proj.set_xlim(np.min(thisx), np.max(thisx))
                # self.ax_proj.set_ylim(np.min(thisy), np.max(thisy))

                self.plot_x_stack = self.plot_x_stack[:-1]
                self.plot_y_stack = self.plot_y_stack[:-1]

                self.fig_proj.canvas.draw()

    def onkeypress_proj(self, event):
        if event.key == 'r':
            if self.plot_x_stack:
                # Get initial limits from stacks
                xmin = self.plot_x_stack[0][0]
                xmax = self.plot_x_stack[0][1]

                ymin = self.plot_y_stack[0][0]
                ymax = self.plot_y_stack[0][1]

                # Set new limits and redraw
                temp_y = self.plot_data['z']

                if self.projection == 'NS':
                    temp_x = self.plot_data['y']
                else:
                    temp_x = self.plot_data['x']

                # # Sort both arrays wrt x
                # temp_y = temp_y[np.argsort(temp_x)]
                # temp_x = temp_x[np.argsort(temp_x)]
                #
                # # Find the indices for xmin, xmax
                # x_indmin, x_indmax = np.searchsorted(temp_x, (xmin, xmax))
                # x_indmax = min(len(temp_x)-1, x_indmax)
                #
                # # if (x_indmax - x_indmin) < 2:
                # #     return True
                #
                # temp_x = temp_x[x_indmin:x_indmax]
                # temp_y = temp_y[x_indmin:x_indmax]
                #
                # # Sort both arrays wrt y
                # temp_x = temp_x[np.argsort(temp_y)]
                # temp_y = temp_y[np.argsort(temp_y)]
                #
                # # Find the indices for ymin, ymax
                # y_indmin, y_indmax = np.searchsorted(temp_y, (ymin, ymax))
                # y_indmax = min(len(temp_y)-1, y_indmax)
                #
                # # if (y_indmax - y_indmin) < 2:
                # #     return True
                #
                # temp_x = temp_x[y_indmin:y_indmax]
                # temp_y = temp_y[y_indmin:y_indmax]
                #
                # thisx = temp_x
                # thisy = temp_y

                if not self.plot_x_stack:
                    thisx, thisy, thist = self.get_plot_data(self.plot_data['x'], self.plot_data['y'], None, [xmin, xmax], None, [ymin, ymax])
                else:
                    thisx, thisy, thist = self.get_plot_data(self.plot_data['x'], self.plot_data['y'], self.plot_x_stack[-1], [xmin, xmax], self.plot_y_stack[-1], [ymin, ymax])

                self.update_graph_proj(thisx, thisy, thist)

                # # self.scat_plan.set_offsets([thisx, thisy])
                # # Set plot's limits
                # self.ax_proj.set_xlim(np.min(thisx), np.max(thisx))
                # self.ax_proj.set_ylim(np.min(thisy), np.max(thisy))

                self.plot_x_stack = []
                self.plot_y_stack = []

                self.fig_proj.canvas.draw()

        elif event.key == ' ' or event.key == 'escape':
            plt.close(self.fig_proj)

    def update_graph_proj(self, thisx, thisy, thist):
        data = np.hstack((thisx[:, np.newaxis], thisy[:, np.newaxis]))
        self.scat_proj.set_offsets(data)
        colors = cm.rainbow(np.linspace(0, 1, len(thist)))
        self.scat_proj.set_color(colors)

        max_y = -np.inf
        min_y = np.inf

        mx_y = np.max(thisy)
        mn_y = np.min(thisy)

        if mx_y > max_y:
            max_y = mx_y

        if mn_y < min_y:
            min_y = mn_y

        max_y = max_y + (max_y - min_y)*.1

        max_x = -np.inf
        min_x = np.inf

        mx_x = np.max(thisx)
        mn_x = np.min(thisx)

        if mx_x > max_x:
            max_x = mx_x

        if mn_x < min_x:
            min_x = mn_x

        max_x = max_x + (max_x - min_x)*.1
        min_x = min_x - (max_x - min_x)*.1

        # Set plot's limits
        self.ax_proj.set_ylim(min_y, max_y)
        self.ax_proj.set_xlim(min_x, max_x)

    def plot_3D(self, xlims=[-20E3, 20E3], ylims=[-20E3, 20E3], zlims=[0, 20E3], projections=False, colorbar=False):
        self.fig_3d = plt.figure()
        self.ax_3d = self.fig_3d.add_subplot(111, projection='3d')

        xlims = np.array(xlims) * 1e-3
        ylims = np.array(ylims) * 1e-3
        zlims = np.array(zlims) * 1e-3

        if projections:
            self.ax_3d.plot(self.plot_data['x']*1e-3, self.plot_data['y']*1e-3, linestyle='None', color='grey', marker='.', markeredgewidth=0, alpha=0.1, zdir='z', zs=zlims[0])
            self.ax_3d.plot(self.plot_data['x']*1e-3, self.plot_data['z']*1e-3, linestyle='None', color='grey', marker='.', markeredgewidth=0, alpha=0.1, zdir='y', zs=ylims[-1])
            self.ax_3d.plot(self.plot_data['y']*1e-3, self.plot_data['z']*1e-3, linestyle='None', color='grey', marker='.', markeredgewidth=0, alpha=0.1, zdir='x', zs=xlims[0])


        self.scat_3d = self.ax_3d.scatter(self.plot_data['x']*1e-3,
                             self.plot_data['y']*1e-3, self.plot_data['z']*1e-3,
                             marker='.', c=self.plot_data['seconds_of_day'],
                             cmap=self.cmap, s=30, lw=0)



        self.ax_3d.set_xlim(xlims)
        self.ax_3d.set_ylim(ylims)
        self.ax_3d.set_zlim(zlims)

        self.ax_3d.set_xlabel('West - East (km)')
        self.ax_3d.set_ylabel('South - North (km)')
        self.ax_3d.set_zlabel('Altitude (km)')

        if colorbar:
            ticks_loc = [self.plot_data['seconds_of_day'][0], self.plot_data['seconds_of_day'][int(len(self.plot_data['seconds_of_day'])/2)], self.plot_data['seconds_of_day'][-1]]
            cb = self.fig_3d.colorbar(self.scat_3d, orientation='vertical', ticks=ticks_loc)
            times = [self.plot_data['t'][0].strftime('%H:%M:%S.%f'),
                     self.plot_data['t'][int(len(self.plot_data['t'])/2)].strftime('%H:%M:%S.%f'),
                     self.plot_data['t'][-1].strftime('%H:%M:%S.%f')]
            cb.ax.set_yticklabels(times)


    def plot_all(self):
        self.fig_all = plt.figure()
        self.gs = GridSpec(5, 4)
        self.gs.update(hspace=.5)

        self.ax_all_alt_t = plt.subplot(self.gs[0, :])
        self.ax_all_EW = plt.subplot(self.gs[1, :-1])
        self.ax_all_hist = plt.subplot(self.gs[1, -1])
        self.ax_all_plan = plt.subplot(self.gs[2:, :-1])
        self.ax_all_NS = plt.subplot(self.gs[2:, -1])

        alt_label = 'Altitude (km)'
        EW_label = 'West - East (km)'
        NS_label = 'South - North (km)'
        hist_label = '# Sources'
        time_label = 'Time after {0} (ms)'.format(datetime.datetime.strftime(self.plot_data['t'][0], "%H:%M:%S:%f"))

        self.ax_all_alt_t.set_ylabel(alt_label)
        self.ax_all_alt_t.set_xlabel(time_label)
        # self.ax_all_alt_t.set_title('LMA Sources')
        self.ax_all_EW.set_ylabel(alt_label)
        self.ax_all_hist.set_xlabel(hist_label)
        self.ax_all_plan.set_ylabel(NS_label)
        self.ax_all_plan.set_xlabel(EW_label)
        self.ax_all_NS.set_xlabel(alt_label)

        s = 30
        lw = 0
        c = cm.rainbow(np.linspace(0, 1, len(self.plot_data['t'])))  # Color by points
        # c = self.plot_data['seconds_of_day']  # Color by time
        marker = '.'

        # Altitude vs. time subplot
        time = self.plot_data['t'] - self.plot_data['t'][0]
        for i in range(len(time)):
            time[i] = float(time[i].total_seconds())*1e3

        self.scat_all_alt_t = self.ax_all_alt_t.scatter(
                                time,
                                self.plot_data['z']*1E-3,
                                marker=marker, c=c,
                                cmap=self.cmap, s=s, lw=lw)

        maj_t, min_t = self.get_date_format_major(self.plot_data['t'])

        max_maj = max(maj_t)
        max_min = max(min_t)

        xlims = [0, max(max_maj, max_min)]

        self.ax_all_alt_t.set_xticks(maj_t)
        self.ax_all_alt_t.set_xticks(min_t, minor=True)
        self.ax_all_alt_t.set_xlim(xlims)

        # self.ax_all_alt_t.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))
        # self.ax_all_alt_t.xaxis.set_minor_formatter(mpl.ticker.FuncFormatter(self.date_format_minor))
        #
        # self.ax_all_alt_t.xaxis.set_major_locator(mpl.ticker.LinearLocator(5))
        # self.ax_all_alt_t.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(self.date_format_major))
        #
        # self.ax_all_alt_t.set_xlim([self.plot_data['t'][0],
        #                             self.plot_data['t'][-1]])

        self.ax_all_alt_t.set_ylim([0, np.max(self.plot_data['z']*1e-3)])

        # Altitude vs. NS projection subplot
        self.scat_all_NS = self.ax_all_NS.scatter(self.plot_data['z']*1E-3,
                                 self.plot_data['y']*1E-3, marker=marker,
                                 c=c, cmap=self.cmap, s=s, lw=lw)
        self.ax_all_NS.set_xlim([0, np.max(self.plot_data['z']*1e-3)])
        self.ax_all_NS.set_ylim([np.min(self.plot_data['y'])*1e-3, np.max(self.plot_data['y']*1e-3)])

        # Altitude vs. EW projection subplot
        self.scat_all_EW = self.ax_all_EW.scatter(self.plot_data['x']*1E-3,
                                 self.plot_data['z']*1E-3, marker=marker,
                                 c=c, cmap=self.cmap, s=s, lw=lw)
        self.ax_all_EW.set_ylim([0, np.max(self.plot_data['z']*1e-3)])
        self.ax_all_EW.set_xlim([np.min(self.plot_data['x'])*1e-3, np.max(self.plot_data['x']*1e-3)])

        # Altitude vs. plan projection subplot
        self.scat_all_plan = self.ax_all_plan.scatter(self.plot_data['x']*1E-3,
                             self.plot_data['y']*1E-3, marker=marker,
                             c=c, cmap=self.cmap, s=s, lw=lw)

        self.ax_all_plan.set_xlim([np.min(self.plot_data['x'])*1e-3, np.max(self.plot_data['x']*1e-3)])
        self.ax_all_plan.set_ylim([np.min(self.plot_data['y'])*1e-3, np.max(self.plot_data['y']*1e-3)])

        # Altitude histogram subplot
        hist, bin_centers, num_pts = self.alt_histogram()
        self.ax_all_hist.plot(hist, bin_centers*1e-3)
        h = self.plot_data['z']*1e-3
        # self.ax_all_hist.text(0.95, 0.5, '{0} pts'.format(num_pts),
        #                       transform=self.ax_all_hist.transAxes,
        #                       rotation='vertical',
        #                       verticalalignment='center')

        self.ax_all_hist.xaxis.set_major_formatter(mpl.ticker.NullFormatter())
        self.ax_all_hist.set_ylim([0, np.max(self.plot_data['z']*1e-3)])


def main():
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111, axisbg='#FFFFCC')

    x = np.arange(0.0, 5.0, 0.01)
    y = np.sin(2*np.pi*x) + 0.5*np.random.randn(len(x))

    ax.plot(x, y, '-')
    ax.set_ylim(-2,2)
    ax.set_title('Press left mouse button and drag to test')
    
    p = Plot(fig, ax)
    p.plot()
    
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111, axisbg='#FFFFCC')

    x = np.arange(0.0, 5.0, 0.01)
    y = np.sin(2*np.pi*x) + 0.5*np.random.randn(len(x))

    ax.plot(x, y, '-')
    ax.set_ylim(-2,2)
    ax.set_title('Press left mouse button and drag to test')
    
    p1 = Plot(fig, ax)
    p1.plot()

    plt.show()
    

if __name__ == "__main__":
    main()

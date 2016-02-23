#!/usr/bin/env python

import sys
from PyQt4 import QtGui, QtCore
import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

import iclrt_tools.plotting.dfplots as df


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.init_ui()
        self.draw()

    def init_ui(self):
        self.main_frame = QtGui.QWidget()

        self.fig = Figure((5, 4), dpi=300)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.canvas.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.canvas.setFocus()

        self.canvas.mpl_connect('button_release_event',
                                self.onclick)
        self.canvas.mpl_connect('key_press_event', self.onkeypress)
        self.canvas.mpl_connect('key_release_event',
                                self.onkeyrelease)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def draw(self):
        t = np.arange(0, 2*np.pi, 0.001)
        x = np.sin(2*np.pi*t)

        self.fig.clear()
        self.ax = self.fig.add_subplot(111)

        self.ax.plot(t, x)
        self.p = df.Plot(self.fig, self.ax)

        self.canvas.draw()

    def onclick(self, event):
        self.p.onclick(event)
        self.canvas.draw()

    def onkeypress(self, event):
        self.p.onkeypress(event)
        self.canvas.draw()

    def onkeyrelease(self, event):
        self.p.onkeyrelease(event)
        self.canvas.draw()


def main():
    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

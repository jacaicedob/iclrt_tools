#!/usr/bin/env python

import sys
from PyQt4 import QtGui, QtCore
import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

import iclrt_tools.plotting.dfplots as df
import iclrt_tools.oscilloscopes.lecroy as lecroy
import iclrt_tools.oscilloscopes.yoko850 as yoko
import iclrt_tools.lma.lma as lma


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.init_ui()
        # self.draw()

    def init_ui(self):
        self.main_frame = QtGui.QWidget()

        self.init_vars()
        self.init_actions()
        self.init_bars()

        self.hbox = QtGui.QHBoxLayout()

        self.vbox = QtGui.QVBoxLayout()

        self.main_frame.setLayout(self.vbox)
        self.setCentralWidget(self.main_frame)

    def init_actions(self):
        self.exit_action = QtGui.QAction('&Exit', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.setStatusTip('Exit Application')
        self.exit_action.triggered.connect(self.close)

        self.open_scope = QtGui.QAction('&Scope File...', self)
        self.open_scope.setStatusTip('Open a scope file (LeCroy, Yokogawa)')
        self.open_scope.triggered.connect(self.scope_open_file_dialog)

        # self.open_lma = QtGui.QAction('&LMA File...', self)
        # self.open_lma.setStatusTip('Open an LMA file')
        # self.open_lma.triggered.connect(self.lma_open_file_dialog)
        #
        # self.open_radar = QtGui.QAction('&Radar File...', self)
        # self.open_radar.setStatusTip('Open a radar file (NEXRAD)')
        # self.open_radar.triggered.connect(self.radar_open_file_dialog)

    def init_bars(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        openMenu = fileMenu.addMenu('&Open')

        openMenu.addAction(self.open_scope)
        # openMenu.addAction(self.open_lma)
        # openMenu.addAction(self.open_radar)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exit_action)

        self.statusBar()

    def init_vars(self):
        self.plots = []

    def scope_open_file_dialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                            '/home/jaime/Documents/ResearchTopics/Publications/Current Reflections/Raw Data/')

        index = fname.find('.')
        extension = fname[index+1:]

        if extension.lower() == 'hdr' or extension.lower() == 'wvf':
            f = yoko.Yoko850File(fname[:index])
            header = f.get_header()
            traces = []

            for i in range(header.numTraces):
                traces.append(f.get_trace_data(header, i+1, 0, 2, wantOffset='y'))

            for trace in traces:
                fig = Figure(dpi=300)
                ax = fig.add_subplot(111)
                ax.plot(trace.dataTime, trace.data)

                self.plots.append((fig, ax))

            self.draw()

        else:
            f = lecroy.lecroy_data(fname)
            traces = []

            for i in range(f.subarray_count):
                traces.append(f.get_segment(i+1))

            for trace in traces:
                # fig = Figure(dpi=300)
                # ax = fig.add_subplot(111)
                # ax.plot(trace.dataTime, trace.data)
                fig, ax = trace.plot()

                self.plots.append((fig, ax))

            self.draw()

    def draw(self):
        fig = self.plots[0][0]
        ax = self.plots[0][1]

        self.canvas = FigureCanvas(fig)
        self.canvas.setParent(self.main_frame)
        self.canvas.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.canvas.setFocus()

        self.canvas.mpl_connect('button_release_event',
                                self.onclick)
        self.canvas.mpl_connect('key_press_event', self.onkeypress)
        self.canvas.mpl_connect('key_release_event',
                                self.onkeyrelease)

        self.canvas.draw()

        self.p = df.Plot(fig, ax)

        self.vbox.addWidget(self.canvas)

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

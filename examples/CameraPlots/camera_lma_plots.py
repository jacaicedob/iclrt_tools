#!/usr/bin/env python

import iclrt_tools.cameras.cameras as cams
import iclrt_tools.plotting.dfplots as df
import iclrt_tools.lma.lma as lma
import sys
import matplotlib.pyplot as plt
import datetime
import matplotlib as mpl

xml_file = '../../iclrt_tools/cameras/cameras.xml'
parser = cams.CameraParser(xml_file)
cam = parser.get_camera_info(year='2015', station='NEO')[0]

lma_files = ['/home/jaime/Documents/LMA/Data/Triggered/2015/150827/LYLOUT_150827_232422_0008_8stations.dat',
             '/home/jaime/Documents/LMA/Data/Triggered/2015/150827/LYLOUT_150827_233202_0008_8stations.dat',
             '/home/jaime/Documents/LMA/Data/Triggered/2015/150827/LYLOUT_150827_234116_0008_8stations.dat',
             '/home/jaime/Documents/LMA/Data/Triggered/2015/150827/LYLOUT_150827_234353_0008_8stations.dat',
             '/home/jaime/Documents/LMA/Data/Triggered/2015/150827/LYLOUT_150827_234736_0008_8stations.dat',
             '/home/jaime/Documents/LMA/Data/Triggered/2015/150827/LYLOUT_150827_235318_0008_8stations.dat']

pictures = ['/media/jaime/LarsenArray/2015Data/082715/Pictures and Videos/NEO/20150827_232423_0087.jpg',
            '/media/jaime/LarsenArray/2015Data/082715/Pictures and Videos/NEO/20150827_233203_0177.jpg',
            '/media/jaime/LarsenArray/2015Data/082715/Pictures and Videos/NEO/20150827_234115_0285.jpg',
            '/media/jaime/LarsenArray/2015Data/082715/Pictures and Videos/NEO/20150827_234353_0316.jpg',
            '/media/jaime/LarsenArray/2015Data/082715/Pictures and Videos/NEO/20150827_234738_0360.jpg',
            '/media/jaime/LarsenArray/2015Data/082715/Pictures and Videos/NEO/20150827_235320_0427.jpg']

for i, picture in enumerate(pictures):
    pic = cams.Picture(cam, picture)
    lma_file = lma.LMAFile(lma_files[i])

    pic.plot_picture()

    p = df.LMAPlotter(lma_file)
    p.plot_alt_t()
    plt.show()

    # Get time and altitude limits and filter by them
    t_lims = p.ax_alt_t.get_xlim()
    t_lims = [datetime.datetime.strftime(mpl.dates.num2date(t_lims[0]), '%H:%M:%S.%f'), datetime.datetime.strftime(mpl.dates.num2date(t_lims[-1]), '%H:%M:%S.%f')]
    z_lims = p.ax_alt_t.get_ylim()
    z_lims = [0, pic.fov[1] - pic.yoffset]  #z_lims[-1]*1E3]

    p.filter_time(t_lims)
    p.filter_alt(z_lims[-1])

    # Plot plan view
    p.plot_plan()
    plt.show()

    # Get x,y lims and filter by them
    x_lims = p.ax_plan.get_xlim()
    y_lims = p.ax_plan.get_ylim()

    # Plot 3D
    p.plot_3D(x_lims, y_lims, z_lims, projections=True)

    pic.plot_picture()



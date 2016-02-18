#!/usr/bin/env python

import numpy as np
import matplotlib as mpl
import matplotlib.image as mplimg
import matplotlib.pyplot as plt
import xml.etree.ElementTree as et
from PIL import Image


class Picture(object):
    def __init__(self, camera, filename):
        self.camera = camera
        self.image = Image.open(filename)
        self.image_size = self.image.size
        self.pixel_length = 0.0
        self.fov = (0.0, 0.0)
        self.xoffset = 0
        self.yoffset = 0
        self.get_fov()

    def __str__(self, camera_info=False):
        s = '-' * 50
        s += '\nPicture Info:\n'
        s += '-' * 50
        s += '\nFile: {}\n'.format(self.image.filename)
        self.get_fov()
        s += 'FOV (W x H): ({:0.3f} x {:0.3f}) m \n'.format(self.fov[0],
                                                          self.fov[1])
        s += 'm/px: {:0.3f}\n'.format(self.pixel_length)

        if camera_info:
            s += self.camera.__str__()

        return s

    def get_fov(self):
        """
        Get the Field of View (FOV) of the camera frame.
        :return: field of view (W x H)
        """
        if self.camera.pixel_size == 0:
            self.camera.pixel_size = self.camera.sensor_width / \
                                     float(self.image_size[0])

        self.pixel_length = self.camera.distance * self.camera.pixel_size / \
                            self.camera.focal_length

        self.fov = (self.image_size[0] * self.pixel_length,
                    self.image_size[1] * self.pixel_length)

    def set_offset(self, xoffset=None, yoffset=None):
        """
        Set the x and y offsets to graphically center the image to a certaint point
        """

        if xoffset is not None:
            self.xoffset = xoffset
        elif yoffset is not None:
            self.yoffset = yoffset

    def plot_picture(self, reference=5):
        self.set_reference = False
        self.reference = reference

        self.img = mplimg.imread(self.image.filename)

        # mpl.rc_file('../../Plotting/matplotlibrc')
        # mpl.rcParams['xtick.color'] = 'k'
        # mpl.rcParams['ytick.color'] = 'k'
        mpl.rcParams['ytick.direction'] = 'inout'
        mpl.rcParams['keymap.home'] = ''
        mpl.rcParams['axes.linewidth'] = 1.0

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.im = self.ax.imshow(self.img, extent=[-self.xoffset, self.fov[0] - self.xoffset,
                                                   -self.yoffset, self.fov[1] - self.yoffset])
        # self.im.axes.xaxis.set_major_locator(mpl.ticker.NullLocator())
        self.im.axes.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
        self.im.axes.yaxis.set_ticks_position('left')

        [t.set_color('white') for t in self.ax.yaxis.get_minorticklines()]
        [t.set_color('white') for t in self.ax.yaxis.get_majorticklines()]

        cid = self.fig.canvas.mpl_connect('button_release_event', self.onclick)
        kp = self.fig.canvas.mpl_connect('key_press_event', self.onkeypress)
        kr = self.fig.canvas.mpl_connect('key_release_event', self.onkeyrelease)

        plt.show()

    def onclick(self, event):
        if event.button == 1 and (event.inaxes is self.ax):
            if self.set_reference:
                self.yoffset = event.ydata - self.reference
                self.xoffset = event.xdata

                self.ax.clear()
                self.im = self.ax.imshow(self.img, extent=[-self.xoffset, self.fov[0] - self.xoffset,
                                                           -self.yoffset, self.fov[1] - self.yoffset])
                # self.im.axes.xaxis.set_major_locator(mpl.ticker.NullLocator())
                self.im.axes.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
                self.im.axes.yaxis.set_ticks_position('left')

                [t.set_color('white') for t in self.ax.yaxis.get_minorticklines()]
                [t.set_color('white') for t in self.ax.yaxis.get_majorticklines()]

                self.fig.canvas.draw()

    def onkeypress(self, event):
        if event.key == 'r':
            self.set_reference = True

    def onkeyrelease(self, event):
        if event.key == 'r':
            self.set_reference = False


class Camera(object):
    def __init__(self, brand, model, station, distance, focal_length,
                 sensor_width, sensor_height, pixel_size, frame_rate):
        self.brand = brand
        self.model = model
        self.station = station
        self.distance = float(distance)  # meters
        self.focal_length = float(focal_length) * 1E-3  # meters
        self.sensor_width = float(sensor_width) * 1E-3  # meters
        self.sensor_height = float(sensor_height) * 1E-3  # meters
        self.pixel_size = float(pixel_size) * 1E-6  # meters
        self.frame_rate = float(frame_rate)

    def __str__(self):
        s = '-' * 50
        s += '\nCamera Info:\n'
        s += '-' * 50
        s += '\nBrand: {}\n'.format(self.brand)
        s += 'Model: {}\n'.format(self.model)
        s += 'Station: {}\n'.format(self.station)
        s += 'Distance: {:0.1f} m\n'.format(self.distance)
        s += 'Focal Length: {:0.1f} mm\n'.format(self.focal_length * 1E3)
        s += 'Sensor Width: {:0.1f} mm\n'.format(self.sensor_width * 1E3)
        s += 'Sensor Height: {:0.1f} mm\n'.format(self.sensor_height * 1E3)
        s += 'Pixel Size: {:0.1f} um\n'.format(self.pixel_size * 1E6)

        if self.frame_rate != 0:
            s += 'Frame Rate: {:0.1f} fps\n'.format(self.frame_rate)

        return s


class CameraParser(object):
    def __init__(self, camera_xml_file):
        self.xml_file = camera_xml_file

    def get_camera_info(self, year='all', brand='all', model='all', station='all'):
        cameras = []
        root = et.parse(self.xml_file)

        for summer in root.findall('summer'):
            if year == 'all':
                pass
            elif summer.find('year').text != year:
                continue

            for camera in summer.findall('camera'):
                if brand == 'all':
                    pass
                elif camera.find('brand').text != brand:
                    continue

                if model == 'all':
                    pass
                elif camera.find('model').text != model:
                    continue

                if station == 'all':
                    pass
                elif camera.find('station').text != station:
                    continue

                brandd = camera.find('brand').text
                modell = camera.find('model').text
                station = camera.find('station').text
                distance = camera.find('distance').text
                focal_length = camera.find('focal_length').text
                sensor_width = camera.find('sensor_width').text
                sensor_height = camera.find('sensor_height').text
                pixel_size = camera.find('pixel_size').text
                frame_rate = camera.find('frame_rate').text

                cameras.append(Camera(brandd, modell, station, distance,
                                      focal_length, sensor_width,
                                      sensor_height, pixel_size, frame_rate))

        return cameras


if __name__ == "__main__":
    xml_file = './cameras.xml'
    parser = CameraParser(xml_file)
    cameras = parser.get_camera_info(year='2015', station='NEO')

    cam = cameras[0]
    picture = Picture(cam, '/media/jaime/LarsenArray/2015Data/082715/Pictures and Videos/NEO/20150827_232423_0087.jpg')

    print(picture)
    #
    picture.plot_picture()
    picture.plot_picture()

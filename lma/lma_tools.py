#!/usr/bin/env python
"""
Original code by Brian Hare (read_lma.py and plot_lma.py).
Adapted by Jaime Caicedo
"""

from datetime import datetime,timedelta
from math import sin,cos,atan2
import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import dates
import matplotlib as mpl
from matplotlib import cm

"""
A couple filters to filter out extraneous points. Takes a list of sources and
limit and returns an range object
"""

def chi_filter(sources, max_chi):
    return (s for s in sources if s.RC2<=max_chi)

def calc_stations(sources): ## for speed reasons, the LMA sources don't initiall caluclate number of stations. So this must be forced
    for s in sources:
        s.calc_numstations()
        yield s

def station_filter(sources, min_stations):
    return (s for s in sources if s.num_stations>=min_stations)

def alt_filter(sources, max_alt):
    return (s for s in sources if s.alt <= max_alt)

"""
Cartographic tools
"""
# Finds the distance between two latlon points
def distance_between_points(latlon1, latlon2):
    ##calculation of distance using haversine formula (in km)
    earth_radius = 6371 ##km

    latlon1=np.radians(latlon1)
    latlon2=np.radians(latlon2)

    dlat=latlon1[0]-latlon2[0]
    dlon=latlon1[1]-latlon2[1]

    a=np.sin(dlat/2) * np.sin(dlat/2) + np.sin(dlon/2) * np.sin(dlon/2) * np.cos(latlon1[0]) * np.cos(latlon2[0])
    b=2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return b*earth_radius

# Calculates the bearing between two latlon points.
def bearing(latlon1, latlon2):
        dLon=latlon1[1]-latlon2[1]
        y=sin(dLon)*cos(latlon2[0])
        x=cos(latlon1[0])*sin(latlon2[0]) - sin(latlon1[0])*cos(latlon2[0])*cos(dLon)
        return atan2(y,x)

"""
Struct to hold data for a single LMA point
"""

class LMA_source(object):
    def __init__(self, date, center, line):
        self.center=center
        words=line.split()
        self.seconds_from_date=float(words[0])
        self.lat=float(words[1])
        self.lon=float(words[2])
        self.alt=float(words[3])
        self.RC2=float(words[4])
        self.power=float(words[5])
        self.mask=str(bin(int(words[6],16)))

        TD=timedelta(seconds=self.seconds_from_date)
        self.timestamp=date+TD

        self.range=distance_between_points((self.lat, self.lon), self.center)

    def show(self):
        print("LMA source at:", self.timestamp)
        print("    lat:", self.lat, "lon:", self.lon, "alt:", self.alt)
        print("    RC2:", self.RC2, "power:", self.power)

    def calc_numstations(self):
        self.num_stations=0
        for s in self.mask[2:]:
            if s=='1':
                self.num_stations+=1

    def calc_bearingIncl(self):
        self.bearing=bearing( self.center, (self.lat,self.lon),)
        self.inclination=atan2((self.alt-self.center[2])/1000.0, self.range)


"""
LMA Files tools
"""

# Takes a file name and reads out date, center of site, and list of LMA points
def read_lma(f_name):
    sources=[]
    with open(f_name, 'r') as fin:
        found_data=False
        for line in fin:

            if found_data:
                new_source=LMA_source(date,center,line)
                sources.append(new_source)

            elif line[0:17]=="Data start time: ":
                info=line[17:]#.split()[0]
                date=datetime.strptime(info, '%m/%d/%y %H:%M:%S ')

            elif line[0:32]=="Coordinate center (lat,lon,alt):":
                info=line[32:].split()
                center=(float(info[0]), float(info[1]), float(info[2]))

            elif line[0:12]=='*** data ***':
                found_data=True

    return date, center, sources


# Holds info for a single file. Including name, start_timestamp and stop_timestamp. Can then open the file and read out a list of LMA points
class lma_file(object):
    def __init__(self, f_name):
        self.f_name=f_name

        with open(f_name, 'r') as fin:
            for line in fin:
                if line[0:17]=="Data start time: ":
                    info=line[17:]
                    self.start_timestamp=datetime.strptime(info, '%m/%d/%y %H:%M:%S ')

                elif line[0:27]=='Number of seconds analyzed:':
                    secs=int(line[27:])
                    self.end_timestamp=self.start_timestamp+timedelta(seconds=secs)

    def check_time(self, timestamp):
        if timestamp<self.end_timestamp and timestamp>self.start_timestamp:
            return 0
        elif timestamp<self.start_timestamp:
            return -1
        elif timestamp>self.end_timestamp:
            return 1

    def open(self):
        return read_lma(self.f_name)

# Takes a folder and reads out a list of LMA files
def file_list(folder):
    lma_files=glob.glob(folder+'*.dat')
    ret=[]
    for f_name in lma_files:
        f=lma_file(f_name)
        ret.append(f)
    return ret
    
    
"""
Plotting tools
"""

# Actually plots the data.
class lma_plotter(object):
    def __init__(self, date,center,lma_sources):

        self.date=date
        self.center=center
        self.color_keys=[]

        self.lats = []
        self.lons = []
        self.alts = []
        self.RC2S = []
        self.powers = []
        self.seconds = []
        self.num_stations = []

        self.N_data = 0
        self.add_data(lma_sources)     

    def add_data(self, lma_sources):
        """
        Allows the user to add data to the original data passed to the 
        constructor.
        """
        lats = np.array([s.lat for s in lma_sources])
        lons = np.array([s.lon for s in lma_sources])
        alts = np.array([s.alt for s in lma_sources])*1E-3
        RC2S = np.array([s.RC2 for s in lma_sources])
        powers = np.array([s.power for s in lma_sources])
                
        mn = datetime(year=self.date.year,month=self.date.month,day=self.date.day)
                
        seconds = np.array([(mn + timedelta(seconds=s.seconds_from_date)) for s in lma_sources])
        
        self.seconds1 = [s.seconds_from_date for s in lma_sources]

        num_stations = np.array([s.num_stations for s in lma_sources])
        
        self.lats.append(lats)
        self.lons.append(lons)
        self.alts.append(alts)
        self.RC2S.append(RC2S)
        self.powers.append(powers)
        self.seconds.append(seconds)
        self.num_stations.append(num_stations)

        self.N_data += 1
        
    def plot(self, hist_bins=100):
        
        #### make the figure
        self.fig = plt.figure()

        self.gs = mpl.gridspec.GridSpec(3,3) 
        self.ax = self.fig.add_subplot(self.gs[:,:-1])
        self.hist = self.fig.add_subplot(self.gs[:,-1])
                
        for i in range(self.N_data):     
            time = self.seconds[i]
            alts = self.alts[i]
            
            col = self.seconds1
            H,Hbins=np.histogram(alts, bins=hist_bins)

            self.ax.scatter(time,alts, marker='.', edgecolor='gray', c=col, cmap=cm.rainbow)
            self.ax.set_xlim([time[0], time[-1]])
            self.ax.xaxis.set_minor_locator(mpl.ticker.LinearLocator())
            self.ax.xaxis.set_minor_formatter(dates.DateFormatter('%H:%M:%S.%f'))
            self.ax.xaxis.set_major_formatter(mpl.ticker.NullFormatter())

            for label in self.ax.xaxis.get_ticklabels(minor=True):
                label.set_rotation(90)
                
            for label in self.ax.xaxis.get_ticklabels(minor=False):
                label.set_rotation(90)
                
#~             self.fig.autofmt_xdate()
            self.hist.plot(H,Hbins[:-1])
            plt.tight_layout()

        return self.fig, self.ax, self.hist
        


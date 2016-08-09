#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import other packages
import numpy as np
import matplotlib.pyplot as plt

import iclrt_tools.plotting.dfplots as df

### Regular dfplots
fig = plt.figure(figsize=(8,6))
ax = fig.add_subplot(111, axisbg='#FFFFCC')

x = np.arange(0.0, 5.0, 0.01)
y = np.sin(2*np.pi*x) + 0.5*np.random.randn(len(x))

ax.plot(x, y, '-')
ax.set_ylim(-2,2)
ax.set_title('Press left mouse button and drag to test')

p = df.plotdf(fig, ax)
p.plot()

fig = plt.figure(figsize=(8,6))
ax = fig.add_subplot(111, axisbg='#FFFFCC')

x = np.arange(0.0, 5.0, 0.01)
y = np.sin(2*np.pi*x) + 0.5*np.random.randn(len(x))

line = ax.plot(x, y, '-')
ax.set_ylim(-2,2)
ax.set_title('Press left mouse button and drag to test')

p1 = df.plotdf(fig, ax)
p1.plot()

### Synced plots
t = np.linspace(-np.pi,np.pi,1E3)
y1 = np.sin(2*np.pi*t)
y2 = 2*np.sin(2*np.pi*t+np.pi/2)
y3 = 10*np.sin(2*np.pi*t+np.pi/4)
y = [y1, y2, y3]

fig = plt.figure("Test Figure")
ax = plt.subplot(211)
line = ax.plot(t, y1,'-or', t, y2, 'g', t, y3, 'x')
ax.set_title("$sin(x)$")
ax.set_xlabel("Time ($\mu$sec)")
ax.set_ylabel("Ampltude (MV)")

ax2 = plt.subplot(212)
line2, = ax2.plot(t,y2)



p1 = df.plotdf(fig, ax, synced=True)
#~ p1.plot()
p2 = df.plotdf(fig, ax2,synced=True)
#~ p2.plot()

wrapper = df.syncdf([p1, p2])
wrapper.plot_all()

plt.show()

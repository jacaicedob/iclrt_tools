#!/usr/bin/env python

import sys
sys.path.append('/home/jaime/Documents/Python Code/Pyplot/')
sys.path.append('/home/jaime/Documents/Python Code/Pyplot/dfplots/')
sys.path.append('/home/jaime/Documents/Python Code/Models/CurrentWaves/')

import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool
from scipy import integrate  

import CurrentWaves as cw

"""
Function definitions
"""
def E_es_integrand(zp,tau):
    # Returns the integrand for the electrostatic component of E
    r = R(zp)

    #~ dt = np.diff(tau)[0]
    E_temp = np.sum(np.array([ (((2-3*(D/r)**2)*i_array[int(tt/delta_t),int((zp-Hb)/dz)]) / r**3) for tt in tau ]))*delta_t
    
    return E_temp

def E_ind_integrand(zp,tp):
    # Returns the integrand for the induction component of E
    r = R(zp)
    return ( (2-3*(D/r)**2)*i_array[int(tp/delta_t),int((zp-Hb)/dz)] ) / (c * r**2)

def E_rad_integrand(zp,tp):
    # Returns the integrand for the radiation component of E
    r = R(zp)
    return -( ((D**2) * di_array[int(tp/delta_t),int((zp-Hb)/dz)]) / ((c**2) * (r**3)) )

def di_r(zp,tp,r):
    # Returns the retarded time derivative of i
    fs_delay = tp - r/c     # Delay due to free space propagation to 
                            # observation pt.

    if fs_delay < 0:
        return 0

    else:
        z_delay = fs_delay - (zp-Hb)/v    # Delay due to velocity of wave

        if z_delay < 0:
            return 0
        else:
            j = int(round(z_delay/delta_t))
            if j >= di.shape[0]:
                return 0
            else:
                return di[j]

def I_r(zp,tp,r):
    # Returns retarted current of the initial current wave
    fs_delay = tp-r/c   # Delay due to free space propagation to observation pt.

    if fs_delay < 0:
        return 0
    else:
        z_delay = fs_delay - (zp-Hb)/v # Delay due to velocity of wave
        if z_delay < 0:
            return 0
        else:
            j = int(round(z_delay/delta_t))
            if j >= i.shape[0]:
                return 0
            else:
                return i[j]
        
def R(zp):
    # Returns the distance R from the source to the observation point
    return np.sqrt(D**2 + zp**2)    
    
def multi_E(t):
    
    tau = np.arange(0, t, delta_t)
    E_es_result = np.sum(np.array([E_es_integrand(z,tau) for z in z_array]))*dz
    
    E_ind_result = np.sum(np.array([E_ind_integrand(z,t) for z in z_array]))*dz
    E_rad_result = np.sum(np.array([E_rad_integrand(z,t) for z in z_array]))*dz

    #~ return (E_es_result, 0, 0)
    #~ return (0, E_ind_result, 0)
    #~ return (0, 0, E_rad_result)
    #~ return (0, E_ind_result, E_rad_result)

    return (E_es_result, E_ind_result, E_rad_result)
    
def init_data(z):
    i_result = np.array([ I_r(z,t,R(z))*np.exp(-(z-Hb)/decay) for t in t_array ])
    di_result = np.array([ di_r(z,t,R(z))*np.exp(-(z-Hb)/decay) for t in t_array ])
    
    return (i_result, di_result)

###################
###  Main Code  ###
###################

# Clear the terminal screen
os.system("clear")

print("-"*50)
print("Stepped-Leader Fields Simulation Using TL Model")
print("-"*50)

"""
Constants
"""

### Absolute constants

c = 3.0E8                   # Speed of light (m/s)
mu0 = 4.0*np.pi*1.0E-7          # Free-space permeability (H/m)
eps0 = 1.0 / (mu0 * c**2)     # Free-space permittivity (F/m)

#### Specific constants

# Geometric constants
RR = 300    # meters
theta = np.array([75]) * np.pi / 180    # See paper for geometry (radians)
Hb = float(RR / np.sqrt(1 + (np.tan(theta))**2))   # Bottom of channel (m)
Ht = Hb + 100           # Top of channel (m)
v = 1.5E8               # Return stroke speed (m/s)
D = float(Hb * np.tan(theta))  # Observation distance from bottom of channel (m)
decay = 25              # Current decay constant (m)

# Gridding constants
t_end_i = 2.5    # Maximum time for which the RS current is defined (us)
samples_i = 2.5E2  # Number of samples in RS current (unitless)

dz = 0.15                   # Distance per division (m)
samples_z = (Ht - Hb) / dz    # Number of samples in z array (unitless)


"""
Set up simulation variables
"""

# Get current time for script timing purposes
start = datetime.datetime.now()

### Generate desired return-stroke waveform.
                                  
# Current waveshape from Jerauld (2007)
alpha1 = 118 # kA/us
alpha2 = 10.5 # kA/us
alpha = [alpha1, alpha2]
beta = 1.85
Tpeak = 0.5  # us
gamma = 20E-3  # us

(t_array_i, di, err) = cw.jerauld_di_dt_2007(alpha, beta, Tpeak, gamma, \
                                     t_end_i, samples_i)
                                     
delta_t = np.diff(t_array_i)[0]
    
i = integrate.cumtrapz(y=di, dx=delta_t, initial=0) # kA

di *= 1E9           # A/s
i *= 1E3            # A
t_array_i *= 1E-6   # s
delta_t *= 1E-6     # s
t_end_i *= 1E-6     # s


### Generate time array for simulation

# Total simulation time = time for wave to get to top + time for radiation to 
# reach the observation point + length of waveform.
t_tot = (Ht-Hb)/v + np.sqrt(Ht**2 + D**2)/c + t_end_i

# Time array for computation
t_array = np.arange(0,t_tot,delta_t)

### Generate z array for simulation

z_array = np.arange(Hb,Ht,dz)

"""
Build data arrays for simulation:
  - These arrays (i, di) contain all the computed values for the current and 
    its derivative for all space and time required by the simulation.
"""

print("Building data arrays...")

i_array = np.empty( (t_array.shape[0], z_array.shape[0]) )
di_array = np.empty( (t_array.shape[0], z_array.shape[0]) )

### Without multi-core
#~ for t in t_array:
    #~ for z in z_array:
        #~ i_array[int(t/delta_t), int(z/dz)] = I_r(z,t,R(z))
        #~ di_array[int(t/delta_t), int(z/dz)] = di_r(z,t,R(z))
        
#### With multi-core

# Define the Queue for the multi-core pool
zz = [z_array[k] for k in range(z_array.shape[0]) if True]

# Instantiate the pool
p = Pool()

# Run the process
answers = p.map(init_data, zz)

# Wait for the pool to finish processing
p.close()
p.join()

# Parse the results
k = 0
for answer in answers:
    i_array[:,k] = answer[0]
    di_array[:,k] = answer[1]

    k += 1

#~ print("\n\nDone!")
    
#~ elapsed = time.time()-start
#~ print("Run time (minutes): ", elapsed/60.0)
#~ 
#~ plt.figure()
#~ plt.subplot(211)
#~ plt.plot(i_array[:,100])
#~ 
#~ plt.subplot(212)
#~ plt.plot(di_array[:,100])
#~ 
#~ plt.show()

#~ sys.exit(1)

print("  - Done.")

"""
Perform field calculations.
"""
E_es = np.empty(t_array.shape)
E_ind = np.empty(t_array.shape)
E_rad = np.empty(t_array.shape)


### Without multi-core

#~ for t in t_array:
    #~ # Auxiliary time array used in E_es calculation
    #~ tau = np.arange(0, t, delta_t)
    #~ E_es[int(t/delta_t)] = np.sum(np.array([E_es_integrand(z,t) for z in z_array]))*dz
    #~ 
    #~ E_ind[int(t/delta_t)] = np.sum(np.array([E_ind_integrand(z,t) for z in z_array]))*dz
    #~ E_rad[int(t/delta_t)] = np.sum(np.array([E_rad_integrand(z,t) for z in z_array]))*dz
    
### With multi-core

print("Starting field calculations...")

# Define the Queue for the multi-core pool
tt = [t_array[k] for k in range(t_array.shape[0]) if True]

# Instantiate the pool
p = Pool()

# Run the process
answers = p.map(multi_E, tt)

# Wait for the pool to finish processing
p.close()
p.join()

# Parse the results
k = 0
for answer in answers:
    E_es[k] = answer[0]
    E_ind[k] = answer[1]
    E_rad[k] = answer[2]

    k += 1
    
print("  - Done.") 
    
### Fix units
print("Fixing units...")

# Correct units for E-field
E_es /= ( 2.0*np.pi*eps0 )
E_ind /= ( 2.0*np.pi*eps0 )
E_rad /= ( 2.0*np.pi*eps0 )
E = (E_es + E_ind + E_rad)

# Change sign convention to AE and apply amplification factor
E_es *= -1
E_ind *= -1
E_rad *= -1
E *= -1

print("  - Done.")
 
"""
Plot results.
"""
print("Plotting results...")

### All fields in one figure

fig = plt.figure()
ax_es = fig.add_subplot(411)
ax_es.plot((t_array-D/c)*1E6, E_es)
ax_es.set_ylabel('E_es (V/m)')

ax_ind = fig.add_subplot(412)
ax_ind.plot((t_array-D/c)*1E6, E_ind)
ax_ind.set_ylabel('E_ind (V/m)')

ax_rad = fig.add_subplot(413)
ax_rad.plot((t_array-D/c)*1E6, E_rad)
ax_rad.set_ylabel('E_rad (V/m)')

ax = fig.add_subplot(414)
ax.plot((t_array-D/c)*1E6, E)
ax.set_ylabel('E (V/m)')
ax.set_xlabel('Time ($\mu$s)')

### Total E-field

#~ fig = plt.figure()
#~ ax = fig.add_subplot(111)
#~ ax.plot((t_array-D/c)*1E6, E)
#~ ax.set_title('$E_{total}$')
#~ ax.set_ylabel('E (V/m)')
#~ ax.set_xlabel('Time ($\mu$s)')

### E_es

#~ fig = plt.figure()
#~ ax = fig.add_subplot(111)
#~ ax.plot((t_array-D/c)*1E6, E_es)
#~ ax.set_title('$E_{es}$')
#~ ax.set_ylabel('E (V/m)')
#~ ax.set_xlabel('Time ($\mu$s)')

### E_ind

#~ fig = plt.figure()
#~ ax = fig.add_subplot(111)
#~ ax.plot((t_array-D/c)*1E6, E_ind)
#~ ax.set_title('$E_{ind}$')
#~ ax.set_ylabel('E (V/m)')
#~ ax.set_xlabel('Time ($\mu$s)')

### E_rad

#~ fig = plt.figure()
#~ ax = fig.add_subplot(111)
#~ ax.plot((t_array-D/c)*1E6, E_rad)
#~ ax.set_title('$E_{rad}$')
#~ ax.set_ylabel('E (V/m)')
#~ ax.set_xlabel('Time ($\mu$s)')

print("  - Done.")

"""
Get script timing.
"""

# Get the time difference between now and when the script started
elapsed = datetime.datetime.now() - start

# Calculate the number of minutes and seconds that corresponds to.
(elapsed_min, elapsed_sec) = divmod(elapsed.days * 86400 + elapsed.seconds,60)

print("\n\nRun time (min:sec): %02d:%02d " % (elapsed_min, elapsed_sec))

# Finish the program by displaying the graphs
plt.show()

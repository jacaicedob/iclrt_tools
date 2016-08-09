#!/usr/bin/env python
# Uses python3

"""
This program calculates the electric and magnetic fields of the lightning
return stroke (RS) using the Modified Transmission Line with Exponential
decay (MTLE) model from Nucci, 1988".

It does not account for any reflections of the RS wave either a height z 
above the ground or ground reflections.

This implementation uses the multiprocessing module.

execfile('/home/jaime/ICLRT/My Papers/Current Reflections/Models/MTL/No Reflections/mtl_model.py')

"""
import iclrt_tools.models.current_fit.current_fit as cf
import iclrt_tools.plotting.dfplots as df

import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool

import iclrt_tools.models.current_waves.current_waves as cw

"""
Function definitions
"""
def B_ind_integrand(zp,tp):
    # Returns the integrand for the induction component of B
    r = R(zp)
    return ( D * i_array[int(tp/delta_t),int(zp/dz)] ) / (r**3)

def B_rad_integrand(zp,tp):
    # Returns the integrand for the radiation component of B
    r = R(zp)
    return ( D * di_array[int(tp/delta_t),int(zp/dz)] ) / (c * r**2)

def E_es_integrand(zp,tau):
    # Returns the integrand for the electrostatic component of E
    r = R(zp)

    E_temp = np.sum(np.array([ (((2-3*(D/r)**2)*i_array[int(tt/delta_t),int(zp/dz)]) / r**3) for tt in tau ]))*delta_t
    
    return E_temp

def E_ind_integrand(zp,tp):
    # Returns the integrand for the induction component of E
    r = R(zp)
    return ( (2-3*(D/r)**2)*i_array[int(tp/delta_t),int(zp/dz)] ) / (c * r**2)

def E_rad_integrand(zp,tp):
    # Returns the integrand for the radiation component of E
    r = R(zp)
    return -1.0*( ((D**2) * di_array[int(tp/delta_t),int(zp/dz)]) / ((c**2) * (r**3)) )

def di_r(zp,tp,r):
    # Returns the retarded time derivative of i
    fs_delay = tp - r/c     # Delay due to free space propagation to 
                            # observation pt.

    if fs_delay < 0:
        return 0

    else:
        z_delay = fs_delay - zp/v    # Delay due to velocity of wave

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
    fs_delay = tp - r/c   # Delay due to free space propagation to 
                          # observation pt.

    if fs_delay < 0:
        return 0
    else:
        z_delay = fs_delay - zp/v # Delay due to velocity of wave
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
    
def P(zp):
    # Returns the height dependent current attenuation factor
    lmb = 2000.0  # Current decay constant from Nucci et al. (m)
    return np.exp(-zp/lmb)
    
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
    
def multi_B(t):
    B_ind_result = np.sum(np.array([B_ind_integrand(z,t) for z in z_array]))*dz
    B_rad_result = np.sum(np.array([B_rad_integrand(z,t) for z in z_array]))*dz

    #~ return (B_ind_result, 0)
    #~ return (0, B_rad_result)

    return (B_ind_result, B_rad_result)
    
def init_data(z):
    i_result = np.array([ I_r(z,t,R(z))*P(z) for t in t_array ])
    di_result = np.array([ di_r(z,t,R(z))*P(z) for t in t_array ])
    
    return (i_result, di_result)

###################
###  Main Code  ###
###################

# Clear the terminal screen
os.system("clear")

print("-"*50)
print("Return-Stroke Fields Simulation Using MTLE Model")
print("            With No Reflections                 ")
print("-"*50)

"""
Constants
"""

### Absolute constants

c = 3.0E8                     # Speed of light (m/s)
mu0 = 4.0*np.pi*1.0E-7        # Free-space permeability (H/m)
eps0 = 1.0 / (mu0 * c**2)     # Free-space permittivity (F/m)

#### Specific constants

# Geometric constants
Ht = 4.0E3          # Top of channel (m)
v = 1.3E8           # Return stroke speed (m/s)
D = 180          # Observation distance from bottom of channel (m)

# Gridding constants
t_end_i = 25.0E-6     # Maximum time for which the RS current is defined (s)
delta_t = 1.0E-6      # Time per division (s)
samples_i = t_end_i / delta_t  # Number of samples in RS current (unitless)

dz = 1.0            # Distance per division (m)
samples_z = Ht / dz   # Number of samples in z array (unitless)


"""
Set up simulation variables
"""

# Get current time for script timing purposes
start = datetime.datetime.now()

### Generate desired return-stroke waveform.

# Triangular wave used in Uman et al. (1975)
#~ (t_array_i, i) = cw.triangular(peak=1.0E4, peak_time=1.0E-6, t_end=t_end_i, \
                               #~ samples=samples_i)

# Current waveshape from Nucci et al. (1990)
#~ I01 = 9.9E3
#~ I02 = 7.5E3
#~ 
#~ tau_1 = 0.072E-6
#~ tau_2 = 5E-6
#~ tau_3 = 100E-6
#~ tau_4 = 6E-6
#~ 
#~ eta = 0.845
#~ 
#~ (t_array_i, i, err) = cw.nucci_1990(I=[I01, I02], tau = [tau_1, tau_2, \
                                    #~ tau_3, tau_4], eta=eta, t_end=t_end_i,\
                                    #~ samples=samples_i)
                                    
# Actual recorded waveform
import Yoko750 as yk
fileName = "/home/jaime/Documents/My Papers/Current Reflections/Raw Data/071414/Scope24/UF1427_IIHI"

f = yk.Yoko750File(fileName)
header = f.get_header()

wantOffset = 'y'

trace = 1 # Specifies which traces you want to look at

calFactor = 61945.76 # Specifies the calibration factor for each
								# trace
df32_tStart = 0 # Gives the starting time of interest for
                                    # each trace
df32_tStop = 2 # Gives the ending time of interest for
                                # each trace                                
result = f.get_trace_data(header, trace, df32_tStart, \
									df32_tStop, calFactor, \
									wantOffset)
                                    
i = result.data
t_array_i = result.dataTime - df32_tStart
t_end_i = t_array_i[-1]
delta_t = np.diff(t_array_i)[0]

dc = df.DCoffset_finder(t_array_i, i)
dc.plot()

plt.show()

i = i[int(dc.x_bounds[0]/delta_t):int(dc.x_bounds[-1]/delta_t)]
t_array_i = t_array_i[int(dc.x_bounds[0]/delta_t):int(dc.x_bounds[-1]/delta_t)]

ds_factor = 20

i = i[::ds_factor]
t_array_i = t_array_i[::ds_factor]
delta_t = np.diff(t_array_i)[0]
t_end_i = t_array_i[-1] - t_array_i[0]

#~ 
#~ cft = cf.CurrentFitTail(t_array_i, i, 20.0E-6)
#~ cft.fit()
#~ i = cft.i
#~ t_array_i = cft.t
#~ t_end_i = t_array_i[-1]
#~ delta_t = np.diff(t_array_i)[0]


### Generate the time derivative of the RS current waveform
di = np.gradient(i, delta_t)

### Generate time array for simulation

# Total simulation time = time for wave to get to top + time for radiation to 
# reach the observation point + length of waveform.
t_tot = Ht/v + np.sqrt(Ht**2 + D**2)/c + t_end_i

# Time array for computation
t_array = np.arange(0,t_tot,delta_t)

### Generate z array for simulation

z_array = np.arange(0,Ht,dz)


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
B_ind = np.empty(t_array.shape)
B_rad = np.empty(t_array.shape)

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

print("  Electric fields:")
# Instantiate the pool
p = Pool()

# Run the process
answers_E = p.map(multi_E, tt)

# Wait for the pool to finish processing
p.close()
p.join()

# Parse the results
k = 0
for answer in answers_E:
    E_es[k] = answer[0]
    E_ind[k] = answer[1]
    E_rad[k] = answer[2]

    k += 1
    
print("    - Done.") 

#~ print("  Magnetic fields:")
#~ # Instantiate the pool
#~ p = Pool()
#~ 
#~ # Run the process
#~ answers_B = p.map(multi_B, tt)
#~ 
#~ # Wait for the pool to finish processing
#~ p.close()
#~ p.join()
#~ 
#~ # Parse the results
#~ k = 0
#~ for answer in answers_B:
    #~ B_ind[k] = answer[0]
    #~ B_rad[k] = answer[1]
#~ 
    #~ k += 1
    #~ 
#~ print("    - Done.") 
    
### Fix units
print("Fixing units...")

#~ # Correct units for B-field
#~ B_ind *= mu0 / ( 2.0*np.pi )
#~ B_rad *= mu0 / ( 2.0*np.pi )
#~ B = (B_ind + B_rad)

# Correct units for E-field
E_es /= ( 2.0*np.pi*eps0 )
E_ind /= ( 2.0*np.pi*eps0 )
E_rad /= ( 2.0*np.pi*eps0 )
E = (E_es + E_ind + E_rad)

# Change sign convention to AE
E_es *= -1.0
E_ind *= -1.0
E_rad *= -1.0
E *= -1.0

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

### All B-fields in one figure

#~ fig = plt.figure()
#~ 
#~ ax_ind = fig.add_subplot(311)
#~ ax_ind.plot((t_array-D/c)*1E6, B_ind)
#~ ax_ind.set_ylabel('B_ind (Wb/$m^2$)')
#~ 
#~ ax_rad = fig.add_subplot(312)
#~ ax_rad.plot((t_array-D/c)*1E6, B_rad)
#~ ax_rad.set_ylabel('B_rad (Wb/$m^2$)')
#~ 
#~ ax = fig.add_subplot(313)
#~ ax.plot((t_array-D/c)*1E6, B)
#~ ax.set_ylabel('B (Wb/$m^2$)')
#~ ax.set_xlabel('Time ($\mu$s)')

print("  - Done.")

"""
Get script timing.
"""

# Get the time difference between now and when the script started
elapsed = datetime.datetime.now() - start

# Calculate the number of minutes and seconds that corresponds to.
(elapsed_min, elapsed_sec) = divmod(elapsed.days * 86400 + elapsed.seconds,60)

print("\n\nRun time (min:sec): %02d:%d " % (elapsed_min, elapsed_sec))

# Finish the program by displaying the graphs
plt.show()

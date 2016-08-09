#!/usr/bin/env python
# Uses python3

"""
This program calculates the electric and magnetic fields of an arbitrary
current source, located at an arbitrary height, and traveling either upward or
downward, using a Modified Transmission Line model, either the linear or the 
exponential decay. The only difference is the function applied to P(zp) method.

It does not account for any reflections of the RS wave either a height z 
above the ground or ground reflections.

This implementation uses the multiprocessing module.

execfile('/home/jaime/ICLRT/My Papers/Current Reflections/Models/MTL/No Reflections/mtl_model.py')

"""
import sys
sys.path.append('/home/jaime/Documents/Python Code/Pyplot/')
sys.path.append('/home/jaime/Documents/Python Code/Pyplot/dfplots/')

sys.path.append('/home/jaime/Documents/Python Code/Models/CurrentFit/')
sys.path.append('/home/jaime/Documents/Python Code/Models/CurrentWaves/')

sys.path.append('/home/jaime/Documents/Python Code/Scopes/Yokogawa/')
sys.path.append('/home/jaime/Documents/Python Code/Scopes/LeCroy/')


import iclrt_tools.models.current_fit.current_fit as cf
import iclrt_tools.plotting.dfplots as df

import os
import datetime
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from multiprocessing import Pool
import sys
import pickle

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

    if direction == 'up':
        E_temp = np.sum(np.array([ (((2-3*(D/r)**2)*i_array[int(tt/delta_t),int((zp-Hstart)/dz)]) / r**3) for tt in tau ]))*delta_t
    else:
        E_temp = np.sum(np.array([ (((2-3*(D/r)**2)*i_array[int(tt/delta_t),int(zp/dz)]) / r**3) for tt in tau ]))*delta_t
    #~ 
    #~ E_temp = np.sum(np.array([ (((2-3*(D/r)**2)*i_array[int(tt/delta_t),int(zp/dz)]) / r**3) for tt in tau ]))*delta_t
    
    return E_temp

def E_ind_integrand(zp,tp):
    # Returns the integrand for the induction component of E
    r = R(zp)
    if direction == 'up':
        return ( (2-3*(D/r)**2)*i_array[int(tp/delta_t),int((zp-Hstart)/dz)] ) / (c * r**2)
    else:
        return ( (2-3*(D/r)**2)*i_array[int(tp/delta_t),int(zp/dz)] ) / (c * r**2)
    #~ 
    #~ return ( (2-3*(D/r)**2)*i_array[int(tp/delta_t),int(zp/dz)] ) / (c * r**2)

def E_rad_integrand(zp,tp):
    # Returns the integrand for the radiation component of E
    r = R(zp)
    if direction == 'up':
        return -1.0*( ((D**2) * di_array[int(tp/delta_t),int((zp-Hstart)/dz)]) / ((c**2) * (r**3)) )
    else:
        return -1.0*( ((D**2) * di_array[int(tp/delta_t),int(zp/dz)]) / ((c**2) * (r**3)) )
    #~ 
    #~ return -1.0*( ((D**2) * di_array[int(tp/delta_t),int(zp/dz)]) / ((c**2) * (r**3)) )

def di_r(zp,tp,r):
    # Returns the retarded time derivative of i
    if direction == 'up':
        if zp < Hstart:
            return 0
    else:
        if zp > Hstart:
            return 0
    
    fs_delay = tp - r/c  # Delay due to free space propagation to 
                            # observation pt.
    
    ### ONLY FOR REF FROM GND is Hr != 0(don't comment out)
    # Speeds are assumed to be constant throughout the arrays (v, v_r)
    fs_delay -= Hr/v_rs + Hr/v_r[0] + Hstart/v_rs
    
    if not(name == 'rs'):
        fs_delay -= fileSaveCurrentsDelay
    ###    
    
    if fs_delay < 0:
        return 0

    else:
        if direction == 'up':
            z_delay = fs_delay - (zp-Hstart)/v[int(zp/dz)]#Vt(zp)    # Delay due to velocity of wave
        else:
            z_delay = fs_delay - (Hstart-zp)/v[int(zp/dz)]#Vt(zp)    # Delay due to velocity of wave

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
    if direction == 'up':
        if zp < Hstart:
            return 0
    else:
        if zp > Hstart:
            return 0
    
    fs_delay = tp - r/c # Delay due to free space propagation to 
                            # observation pt.
               
    ### ONLY FOR REF FROM GND is Hr != 0(don't comment out)
    # Speeds are assumed to be constant throughout the arrays (v, v_r)
    fs_delay -= Hr/v_rs + Hr/v_r[0] + Hstart/v_rs
    
    if name != 'rs':
        fs_delay -= fileSaveCurrentsDelay
    ###  

    if fs_delay < 0:
        return 0
    else:
        if direction == 'up':
            z_delay = fs_delay - (zp-Hstart)/v[int(zp/dz)]#Vt(zp)    # Delay due to velocity of wave
        else:
            z_delay = fs_delay - (Hstart-zp)/v[int(zp/dz)]#Vt(zp)    # Delay due to velocity of wave
            
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
    
def Vt(zp):
    # Returns the time for the RS wave to reach zp, given a velocity that
    # varies with height
    
    j = int(zp/dz)
    
    s = np.sum(v_inv[0:j])
    
    return dz*s
    
def P(zp):
    # Returns the height dependent current attenuation factor
    
    #### ONLY FOR REF GOING UP IS Hr not 0
    if Hr != 0:
        return 1
    ####
    
    if direction == 'up':
        j = int(zp/dz)
        m = int(Hstart/dz)
        
        # return 1   # TL Model
        return np.exp(-dz*np.sum(lmb_inv[m:j])) # MTLE Model
        
        # if name == 'rs':
        #     return (1.0 - float(zp/Ht)) # MTLL Model only for RS wave
        # else:
        #     return 1
            
    else:
        return 1
    
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
    
def get_currents(fileSave):
    ### Generate desired return-stroke waveform.

    # Triangular wave used in Uman et al. (1975)
    # (t_array_i, i) = cw.triangular(peak=1.0E4, peak_time=1.0E-6, t_end=25E-6, \
    #                                samples=500.0)
    #
    # t_end_i = t_array_i[-1]
    # delta_t = np.diff(t_array_i)[0]
    #
    # ### Generate the time derivative of the RS current waveform
    # di = np.gradient(i, delta_t)
    # i_r = i
    # ii_real = i
    #
    # return (t_array_i, delta_t, i, i_r, ii_real, di, t_end_i)

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
                
    #~ fileSave = './UF1333_I_RS1.p'
    try:
        fo = pickle.load(open(currents, "rb"))
        i = fo['i']
        t_array_i = fo['t_array_i']
        i_r = fo['i_r']
        ii_real = fo['ii_real']
        
        #~ p = df.RelativeTimePlot(t_array_i, i_r)
        #~ p.plot()
        #~ plt.show()
        
        delta_t = np.diff(t_array_i)[0]
        #~ print(delta_t)
        
        #~ from scipy.signal import savgol_filter
        #~ i_r = savgol_filter(i_r, 9, 5)
        #~ i_r = i_r[p.zero_ind:-1]
        
        #### FOR UP/DOWN and REF ONLY (i_r must already be negative)
        if name != 'rs':
            i = i_r
        
        #~ plt.plot(i)
        #~ plt.plot(ii_real)
        #~ plt.plot(i_r)
        #~ plt.show()
        #~ sys.exit(1)
            
    except FileNotFoundError: 
        print('File not found: \' %s \'' % currents)
        
        try:
            fo = pickle.load(open(fileSave, "rb"))
            i = fo['i_model']
            t_array_i = fo['time']
            i_r = -0.5*fo['i_r']
            ii_real = fo['ii_hi']
            ind = fo['ind']
            
            delta_t = np.diff(t_array_i)[0]
            #~ print(delta_t)
            
            #~ p = df.RelativeTimePlot(t_array_i, i)
            #~ p.plot()
            #~ plt.show()
            #~ i = i[p.zero_ind:-1]# - i[p.zero_ind]
            
            #~ i = i[ind-int(fileSaveCurrentsDelay/delta_t):-1]
            
            p = df.RelativeTimePlot(t_array_i, i_r)
            p.plot()
            plt.show()
                        
            
            from scipy.signal import savgol_filter
            i_r = savgol_filter(i_r, 9, 5)
            i_r = i_r[p.zero_ind:-1]# - i_r[p.zero_ind]
            
            plt.plot(i)
            plt.plot(ii_real)
            
            p = df.pickerPlot(plt.gcf(), plt.gca())
            p.plot()
            plt.show()
            
            data = {}
            data['i'] = i
            data['t_array_i'] = t_array_i
            data['i_r'] = i_r
            data['ii_real'] = ii_real        
            
            pickle.dump(data, open(currents, 'wb'))
            
            #~ plt.plot(i)
            #~ plt.plot(ii_real)
            #~ plt.plot(i_r)
            #~ plt.show()
            #~ sys.exit(1)
                
        except FileNotFoundError: 
            print('File not found: \' %s \'' % fileSave)
            raise
        
    t_end_i = t_array_i[-1]
    delta_t = np.diff(t_array_i)[0]

    ### Generate the time derivative of the RS current waveform
    di = np.gradient(i, delta_t)
    
    return (t_array_i, delta_t, i, i_r, ii_real, di, t_end_i)
    
def save_data(fileSave, data):

    pickle.dump(data, open('%s' % fileSave, "wb"))

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

## Geometric constants

Ht = 4.0E3      # Top of channel (m)
Hstart = 0.0    # Height at which desired wave starts
Hr = 280.0       # Height of discontinuity
D = 92.0       # Observation distance from bottom of channel (m)

## Speed and attenuation
v_rbounds = [1.4E8, 1.4E8] # Reflected wave speed (m/s)
v_bounds = [1.4E8, 1.4E8]   # Incident wave speed (m/s)
l_bounds = [3.0E3, 3.0E3]   # Lambda boundaries bottom to top
t_tot = 40.0E-6

## Gridding constants

#~ t_end_i = 25.0E-6     # Maximum time for which the RS current is defined (s)
#~ delta_t = 1.0E-6      # Time per division (s)
#~ samples_i = t_end_i / delta_t  # Number of samples in RS current (unitless)

dz = 1.0        # Distance per division (m)
samples_z = Ht / dz   # Number of samples in z array (unitless)

v = np.linspace(v_bounds[0], v_bounds[-1], samples_z)
v_inv = 1.0/v   # Array containing 1/v values used in Vt(zp) method

v_rs = v[0]

v_r = np.linspace(v_rbounds[0], v_rbounds[-1], samples_z)
v_rinv = 1.0/v_r   # Array containing 1/v values used in Vt(zp) method

lmb = np.linspace(l_bounds[0], l_bounds[-1], samples_z)
lmb_inv = 1.0/lmb
#~ lmb = 2000 * np.exp(0.00082*np.linspace(0,Ht,Ht))

#~ l1 = np.linspace(l_bounds[0], l_bounds[-1], int(1.0E3/dz))
#~ l2 = np.linspace(l_bounds[-1], l_bounds[-1], samples_z-int(1.0E3/dz))
#~ lmb = np.concatenate([l1, l2])

## Data Files

fileSaveCurrents = '/home/jaime/Documents/Python Code/Models/CurrentFit/DataFiles/UF0920_I_RS3.p'
fileSaveCurrentsDelay = 5.0E-6 # Delay from start of current to dip

currents = '/home/jaime/Documents/My Papers/Ongoing/Current Reflections/Models/MTLE/1 Reflection/ResultsGeneralTL/UF0920RS3/currents.p'

"""
variables = [name,direction, Hstart, Hr, fileSaveCurrents, v, v_inv]
"""
varss = []
name = ""
direction = ""
fileSaveData = ""

varss.append(['rs', 'up', 0.0, 0.0, './data_RS.p', v, v_inv])   # RS wave
varss.append(['up', 'up', Hr, 0.0, './data_up.p', v, v_inv]) # Up wave
varss.append(['ref', 'up', 0.0, Hr, './data_Ref.p', v_r, v_rinv])  # Reflected wave from gnd
varss.append(['down', 'down', Hr, 0.0, './data_down.p', v_r, v_rinv])  # Down wave

# Get current time for script timing purposes
start = datetime.datetime.now()

for variables in varss:

    name = variables[0]
    direction = variables[1]
    Hstart = variables[2]
    Hr = variables[3]
    fileSaveData = variables[4]
    v = variables[5]
    v_inv = variables[6]
    
    print(name.upper())

    """
    Set up simulation variables
    """

    ### Get the currents and derivatives
    (t_array_i, delta_t, i, i_r, ii_real, di, t_end_i) = get_currents(fileSaveCurrents)

    ### Generate time array for simulation

    # Total simulation time = time for wave to get to top + time for radiation to 
    # reach the observation point + length of waveform.
    #~ t_tot = Hstart/v[0] + R(Hstart)/c + t_end_i + Ht/v[0]#R(0)/c

    # Time array for computation
    t_array = np.arange(0,t_tot,delta_t)

    ### Generate z array for simulation

    if direction == 'up':
        z_array = np.arange(Hstart,Ht,dz)
    else:
        z_array = np.arange(0, Hstart,dz)
        
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

    print("Saving data...")
    data = {}

    data['time'] = t_array-D/c
    data['E_es'] = E_es
    data['E_ind'] = E_ind
    data['E_rad'] = E_rad
    data['E'] = E
    data['i_array'] = i_array
    data['di_array'] = di_array
    data['z_array'] = z_array
    data['i'] = i
    data['di'] = di
    data['D'] = D
    data['v'] = v
    data['lmb'] = lmb
    data['Hstart']  = Hstart

    save_data(fileSaveData, data)
    print("  - Done.")
    
"""
Plot results.
"""
print("Plotting results...")

### All fields in one figure

fig = plt.figure()
fig.suptitle('Distance from channel: %d m' % D)

ax_es = fig.add_subplot(411)
ax_es.plot((t_array-D/c)*1E6, E_es)
ax_es.set_ylabel('E_es (V/m)')
ax_es.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
ax_es.grid(True,which='both')
ax_es.autoscale(enable=True, axis='both', tight=True)

ax_ind = fig.add_subplot(412)
ax_ind.plot((t_array-D/c)*1E6, E_ind)
ax_ind.set_ylabel('E_ind (V/m)')
ax_ind.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
ax_ind.grid(True,which='both')
ax_ind.autoscale(enable=True, axis='both', tight=True)

ax_rad = fig.add_subplot(413)
ax_rad.plot((t_array-D/c)*1E6, E_rad)
ax_rad.set_ylabel('E_rad (V/m)')
ax_rad.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
ax_rad.grid(True,which='both')
ax_rad.autoscale(enable=True, axis='both', tight=True)

ax = fig.add_subplot(414)
ax.plot((t_array-D/c)*1E6, E)
ax.set_ylabel('E (V/m)')
ax.set_xlabel('Time ($\mu$s)')
ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
ax.grid(True,which='both')
ax.autoscale(enable=True, axis='both', tight=True)

### Total E-field

fig = plt.figure()
fig.suptitle('Distance from channel: %d m' % D)

ax = fig.add_subplot(111)
ax.plot((t_array-D/c)*1E6, E)
ax.set_title('$E_{total}$')
ax.set_ylabel('E (V/m)')
ax.set_xlabel('Time ($\mu$s)')
ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
ax.grid(True,which='both')
ax.autoscale(enable=True, axis='both', tight=True)

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

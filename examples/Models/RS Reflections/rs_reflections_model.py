#!/usr/bin/env python

# Add personal packages directory to path
import sys
# sys.path.append('/home/jaime/Documents/Python Code')

# Import other modules
import numpy as np
from matplotlib import pyplot as plt

import iclrt_tools.models.wave_model.wave_model as wavemodel

# Start main code

C = 3.0E8                     # Speed of light (m/s)
mu0 = 4.0*np.pi*1.0E-7        # Free-space permeability (H/m)
eps0 = 1.0 / (mu0 * C**2)     # Free-space permittivity (F/m)
two_pi_e0 = 2*np.pi*eps0


Ht = 2.0E3      # Top of channel (m)
Hr = 280.0       # Height of discontinuity
D = [92.0]       # Observation distance from bottom of channel (m)

# Speed and attenuation
v = 1.21E8  # Incident wave speed (m/s)
v_r = 1.67E8  # Reflected wave speed (m/s)
lmb = 3.0E3  # Lambda boundaries bottom to top

# Data Files

fileSaveCurrents = '/home/jaime/Documents/ResearchTopics/Publications/Current Reflections/CurrentFit/DataFiles/UF0920_I_RS3.p'
fileSaveCurrentsDelay = 5.0E-6  # Delay from start of current to dip

currents = '/home/jaime/Documents/ResearchTopics/Publications/Current Reflections/Models/WaveModel/UF0920RS3/currents.p'

(t_array_i, delta_t, i, i_r, ii_real, di, t_end_i) = \
    wavemodel.get_currents(currents, fileSaveCurrents)

rs_wave = wavemodel.RS(i, delta_t, v, 0, Ht, 0,
                       attenuation=lambda z: np.exp(-z/lmb))

up_wave = wavemodel.UP(i_r, delta_t, v, Hr, Ht,
                       Hr/v+fileSaveCurrentsDelay,
                       attenuation=lambda z: np.exp(-z/lmb))

down_wave = wavemodel.DOWN(i_r, delta_t, v_r, Hr, 0, Hr/v +
                           fileSaveCurrentsDelay)

ref_wave = wavemodel.REF(i_r, delta_t, v_r, 0, Ht, Hr/v + Hr/v_r +
                         fileSaveCurrentsDelay)

waves = [rs_wave, down_wave, up_wave, ref_wave]
file_names = ['./data_RS.p', './data_down.p', './data_up.p',
              './data_Ref.p']
data = {}

fm = wavemodel.field_model(waves, delta_t, Ht, fields='111')

for j, wave in enumerate(waves):

    t_array, E_es, __ = fm.calc_fields_individual(j, D, Ht, temp_field='001')
    t_array, E_ind, __ = fm.calc_fields_individual(j, D, Ht, temp_field='010')
    t_array, E_rad, __ = fm.calc_fields_individual(j, D, Ht, temp_field='100')
    t_array, E_tot, currents = fm.calc_fields_individual(j, D, Ht, temp_field='111')

    #~ data = {}

    data['time'] = t_array - D[0]/C
    data['E_es'] = E_es[0]
    data['E_ind'] = E_ind[0]
    data['E_rad'] = E_rad[0]
    data['E'] = E_tot[0]
    data['D'] = D[0]
    data['v'] = wave.velocity
    data['lmb'] = lmb
    data['Hstart'] = wave.Hstart
    data['i'] = wave.CBC
    data['di'] = wave.CBC_integral

    data['i_array'] = currents[0]
    data['di_array'] = 0  #di_array
    data['z_array'] = 0  #z_array

    wavemodel.save_data(file_names[j], data)


t_array, E_es, __ = fm.calc_fields(D, Ht, temp_field='001')
t_array, E_ind, __ = fm.calc_fields(D, Ht, temp_field='010')
t_array, E_rad, __ = fm.calc_fields(D, Ht, temp_field='100')
t_array, E_tot, currents = fm.calc_fields(D, Ht, temp_field='111')

data['time'] = t_array - D[0]/C
data['E_es'] = E_es[0]
data['E_ind'] = E_ind[0]
data['E_rad'] = E_rad[0]
data['E'] = E_tot[0]
data['D'] = D[0]
data['v'] = 0
data['lmb'] = lmb
data['Hstart'] = 0
data['i'] = currents[0]
data['di'] = np.gradient(currents[0], delta_t)

data['i_array'] = currents[0]
data['di_array'] = 0  #di_array
data['z_array'] = 0  #z_array

wavemodel.save_data('./data_sum.p', data)

print(data['time'].shape, data['E'].shape)

plt.figure()
plt.plot(data['time']*1E6, data['E'])

plt.figure()
plt.plot(data['i_array'][:, 0], label='MTLE')
plt.plot(ii_real, label='II_HI')
plt.legend()
plt.show()
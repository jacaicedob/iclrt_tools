#!/usr/bin/env python
# Uses python3

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
import scipy

import iclrt_tools.models.current_waves.current_waves as cw

### Absolute constants
c = 3.0E8                     # Speed of light (m/s)
mu0 = 4.0*np.pi*1.0E-7        # Free-space permeability (H/m)
eps0 = 1.0 / (mu0 * c**2)     # Free-space permittivity (F/m)

tl_factor = 1.0 / ( 2.0*np.pi*eps0 ) # Factor in front of integrals for TL model
ae_factor = -1.0                     # AE sign convention   
    
class Mtle_Current_Model(object):
    """
    This class implements the MTLE model
    """
    def __init__(self, i, i_r, time, v, lmb, Hb, Ht, z_r, D, z_samples=1.0E3):
        self.i = i
        self.data_points = len(self.i)
        
        self.i_r = i_r
        
        self.z_r = z_r
        
        self.time = time
        self.dt = np.diff(self.time)[0]
        
        self.v = v
        self.v_inv = 1.0/self.v
        
        self.lmb = lmb
        self.lmb_inv = 1.0/lmb
        
        self.Hb = Hb
        self.Ht = Ht
        self.D = D
        
        self.z_samples = z_samples
        self.z = np.linspace(self.Hb, self.Ht, self.z_samples)
        self.dz = np.diff(self.z)[0]
    
    def derivative(self, i, dt):
        return np.gradient(i, dt)
    
    def integral(self, i, dt):
        return scipy.integrate.cumtrapz(i, dx=dt, initial=0)
    
    def max_time_length(self):
        return int(self.T_v(self.Ht) / float(self.dt) + self.data_points)
        
    def P(self,z):
        # Returns the height dependent current attenuation factor
        j = int(z/self.dz)

        return np.exp(-self.dz*np.sum(self.lmb_inv[0:j])) # MTLE
        
    def T_v(self,z):
        # Returns the time for the RS wave to reach z, given a velocity that
        # varies with height
        
        j = int(z/self.dz)
        
        s = np.sum(self.v_inv[0:j])
        
        return self.dz*s
        
    def T_v_r(self,z):
        # Returns the time for the reflected wave to reach z, given a velocity that
        # varies with height
        
        if z < self.z_r:
            ind_s = int(z/self.dz)
            ind_e = int(self.z_r/self.dz)
            
            s = np.sum(self.v_inv[ind_s:ind_e])
            s += np.sum(self.v_r_inv[ind_s:ind_e])
            
            return self.dz*(self.z_r - z)*s
            
        else:
            return self.T_v(z)
            
    def T_v_gnd(self,z):
        # Returns the time for the reflected ground wave to reach z, given a 
        # velocity that varies with height
        
        j = int(self.z_r/self.dz)
        s = np.sum(self.v_inv[0:j])
        s += np.sum(self.v_r_inv[0:j])
        
        j = int(z/self.dz)
        s += np.sum(self.v_r_inv[0:j])
        
        return self.dz*s
    
    def get_I(self,z):
        I = np.zeros(self.max_time_length())
        dI = np.zeros(I.shape)
        intI = np.zeros(I.shape)
        
        delay = int(self.T_v(z)/self.dt)
        delay_r = int(self.T_v_r(z)/self.dt)
        delay_gnd = int(self.T_v_gnd(z)/self.dt)
        
        attenuation = self.P(z)
        
        I[delay:delay+self.data_points] = self.i*attenuation
        I[delay_r:delay_r+self.data_points] += self.i_r*attenuation
        I[delay_gnd:delay_gnd+self.data_points] += self.i_gnd*attenuation
        
        dI[delay:delay+self.data_points] = self.derivative(self.i, self.dt)*attenuation
        dI[delay_r:delay_r+self.data_points] += self.derivative(self.i_r, self.dt)*attenuation
        dI[delay_gnd:delay_gnd+self.data_points] += self.derivative(self.i_gnd, self.dt)*attenuation
        
        intI[delay:delay+self.data_points] = self.integral(self.i, self.dt)*attenuation
        intI[delay+self.data_points:] = intI[delay+self.data_points-1]
        
        intI[delay_r:delay_r+self.data_points] += self.integral(self.i_r, self.dt)*attenuation
        intI[delay_r+self.data_points:] = intI[delay_r+self.data_points-1]
        
        intI[delay_gnd:delay_gnd+self.data_points] += self.integral(self.i_gnd, self.dt)*attenuation
        intI[delay_gnd+self.data_points:] = intI[delay_gnd+self.data_points-1]
        
        return (I, dI, intI)
        
    def init_data(self, ind):
        z = self.z[ind]
                
        return self.get_I(z)

    def run(self):
        
        #### Fill out the current and current derivative arrays 
        #### with multi-core

        # Instantiate the pool
        p = Pool()
        # Define the Queue for the multi-core pool
        que = [k for k in range(int(self.z_samples))]

        # Run the process
        answers = p.map(self.init_data, que)

        # Wait for the pool to finish processing
        p.close()
        p.join()
        
        #~ plt.figure()
        #~ plt.plot(answers[0][0])
        #~ plt.plot(answers[int(len(answers)/2)][0])
        #~ plt.plot(answers[-1][0])
        #~ 
        #~ plt.figure()
        #~ plt.plot(answers[0][1])
        #~ plt.plot(answers[int(len(answers)/2)][1])
        #~ plt.plot(answers[-1][1])
        #~ 
        #~ plt.figure()
        #~ plt.plot(answers[0][2])
        #~ plt.plot(answers[int(len(answers)/2)][2])
        #~ plt.plot(answers[-1][2])
        #~ 
        plt.show()
        
        #~ sys.exit(1)
        
        return answers
    
class Mtlel_Current_Model(object):
    """
    This class implements the MTLE model from the ground to some height
    and then the MTLL model from there to the top of the channel
    """
    def __init__(self, i, time, v, lmb, Hb, Ht, Hl, D, z_samples=1.0E3):
        self.i = i
        self.data_points = len(self.i)
        
        self.time = time
        self.dt = np.diff(self.time)[0]
        
        self.v = v
        self.v_inv = 1.0/self.v
        
        self.lmb = lmb
        self.lmb_inv = 1.0/lmb
        
        self.Hb = Hb
        self.Ht = Ht
        self.Hl = Hl
        self.D = D
        
        self.z_samples = z_samples
        self.z = np.linspace(self.Hb, self.Ht, self.z_samples)
        self.dz = np.diff(self.z)[0]
    
    def derivative(self):
        return np.gradient(self.i, self.dt)
    
    def integral(self):
        return scipy.integrate.cumtrapz(self.i, dx=self.dt, initial=0)
    
    def max_time_length(self):
        return int(self.T_v(self.Ht) / float(self.dt) + self.data_points)
        
    def P(self,z):
        # Returns the height dependent current attenuation factor
        if z < self.Hl:
            j = int(z/self.dz)

            return np.exp(-self.dz*np.sum(self.lmb_inv[0:j])) # MTLE
        else:
            return (1 - 0.9*(z - self.Hl)/(self.Ht - self.Hl)) # MTLL
        
    def T_v(self,z):
        # Returns the time for the RS wave to reach z, given a velocity that
        # varies with height
        
        j = int(z/self.dz)
        
        s = np.sum(self.v_inv[0:j])
        
        return self.dz*s
    
    def get_I(self,z):
        I = np.zeros(self.max_time_length())
        dI = np.zeros(I.shape)
        intI = np.zeros(I.shape)
        
        delay = int(self.T_v(z)/self.dt)
        attenuation = self.P(z)
        
        I[delay:delay+self.data_points] = self.i*attenuation
        dI[delay:delay+self.data_points] = self.derivative()*attenuation
        intI[delay:delay+self.data_points] = self.integral()*attenuation
        intI[delay+self.data_points:] = intI[delay+self.data_points-1]
        
        return (I, dI, intI)
        
    def init_data(self, ind):
        z = self.z[ind]
                
        return self.get_I(z)

    def run(self):
        
        #### Fill out the current and current derivative arrays 
        #### with multi-core

        # Instantiate the pool
        p = Pool()
        # Define the Queue for the multi-core pool
        que = [k for k in range(int(self.z_samples))]

        # Run the process
        answers = p.map(self.init_data, que)

        # Wait for the pool to finish processing
        p.close()
        p.join()
        
        #~ plt.figure()
        #~ plt.plot(answers[0][0])
        #~ plt.plot(answers[int(len(answers)/2)][0])
        #~ plt.plot(answers[-1][0])
        #~ 
        #~ plt.figure()
        #~ plt.plot(answers[0][1])
        #~ plt.plot(answers[int(len(answers)/2)][1])
        #~ plt.plot(answers[-1][1])
        #~ 
        #~ plt.figure()
        #~ plt.plot(answers[0][2])
        #~ plt.plot(answers[int(len(answers)/2)][2])
        #~ plt.plot(answers[-1][2])
        #~ 
        plt.show()
        
        #~ sys.exit(1)
        
        return answers
########################################################################
class Simulation():
    def __init__(self):        
        self.Hb = 0.0
        self.Ht = 4.5E3
        self.dz = 1.0        
        self.z = np.arange(self.Hb, self.Ht)*self.dz
        self.z_samples = len(self.z)
        
        self.v_bounds = [1.6E8, 1.6E8]
        self.l_bounds = [2.0E8, 2.0E8]
        self.D = 180.0
        
        self.Hl = 300.0
        self.hh = 241.0
        
        self.fileSave = '/home/jaime/Documents/My Papers/RS Modeling/Data Sets/UF1333_data_081713_rs1.p'
        
        self.fileSaveI = '/home/jaime/Documents/My Papers/RS Modeling/MTL/MTLE/UF1333/RS1/UF1333_RS1_I.p'
        
        # Intialize arrays and current model
        self.init_arrays()
        
        self.model = Mtle_Current_Model(self.i, self.time, self.v, self.lmb, self.Hb, self.Ht, self.D, self.z_samples)
        
        #~ self.model = Mtlel_Current_Model(self.i, self.time, self.v, self.lmb, self.Hb, self.Ht, self.Hl, self.D, self.z_samples)
    
    def max_time_length(self):
        return self.model.max_time_length() + int(self.R(self.Ht)/c/self.model.dt)
    
    def modify_v(self, h, value):
        self.v = np.append(self.v[0:int(h/self.dz)], np.ones(self.z_samples-int(h/self.dz))*value)
        
    def modify_v_lin(self, h, value):
        length = self.z_samples-int(h/self.dz)
        v_i = self.v[int(h/self.dz)]
        v_f = value
        slope = v_f - v_i
        temp_v = np.ones(length)       
        
        for i in range(len(temp_v)):
            temp_v[i] = v_i + (v_f-v_i)/float(length) * i
        
        self.v = np.append(self.v[0:int(h/self.dz)], temp_v)
        
    def modify_lmb(self, h, value):
        self.lmb = np.append(self.lmb[0:int(h/self.dz)], np.ones(self.z_samples-int(h/self.dz))*value) 
        
    def init_arrays(self):
        self.v = np.linspace(self.v_bounds[0], self.v_bounds[-1], self.z_samples)
        self.lmb = np.linspace(self.l_bounds[0], self.l_bounds[-1], self.z_samples)
                
        #~ self.modify_v_lin(self.hh, 7.5E5)
        self.modify_v(self.hh, 1.15E8)
        self.modify_lmb(self.hh, 2.0E3)
        
        
        self.t_delay_from_dataset = 5.0E-6 # When getting the data using the
                                  # generateDataSet.py code, the time
                                  # array starts at -5 us, which messes
                                  # up the indexing after selecting the
                                  # time zero for the current waveform, so
                                  # it must be added to the t_array_i before
                                  # passing it to df.RelativeTimePlot()
        
        if os.path.isfile(self.fileSaveI):
            pass
        else:
            self.get_saved_current()
            
        (t_array_i, delta_t, i) = self.get_currents()
        
        self.i = i
        self.time = t_array_i
        
    def get_saved_current(self):
        try:
            fo = pickle.load(open(self.fileSave, "rb"))
            i = fo['II_HI']
            t_array_i = fo['time']*1E-6
            delta_t = np.diff(t_array_i)[0]
        except FileNotFoundError:
            raise
            
        rt_plot = df.RelativeTimePlot(t_array_i+self.t_delay_from_dataset, i, max_points=1E9)
        rt_plot.plot()

        plt.show()

        zero_time = rt_plot.zero_time

        i = i[int(zero_time/delta_t):int((zero_time + 110E-6)/delta_t)] - i[int(zero_time/delta_t)]

        t_array_i = t_array_i[int(zero_time/delta_t):int((zero_time + 110E-6)/delta_t)] - zero_time
        
        ### Smooth out the signal using a Savitzky-Golay filter
        from scipy.signal import savgol_filter
        ii_savgol = savgol_filter(i, 9, 5)
        i = ii_savgol

        data = {}
        data['I'] = i
        data['time'] = t_array_i
        
        pickle.dump(data, open(self.fileSaveI, 'wb'))
        
    def get_currents(self):
        try:
            #~ fo = pickle.load(open(self.fileSave, "rb"))
            fo = pickle.load(open(self.fileSaveI, "rb"))
            i = fo['I']
            t_array_i = fo['time']
                
        except FileNotFoundError: 
            raise
        
        ### Do a spline interpolation to make dt smaller
        #~ from scipy import interpolate
        #~ 
        #~ tck = interpolate.splrep(t_array_i, i, s=0)
        #~ tnew = np.arange(t_array_i[0],t_array_i[-1], 1.0E-9)
        #~ inew = interpolate.splev(tnew, tck, der=0)    
        #~ 
        #~ t_array_i = tnew
        #~ i = inew
        
        #~ (t_array_i, i) = cw.triangular(peak=1E4, peak_time=1E-6, t_end=25E-6, samples=1E3)
        #~ 
        #~ delta_t = np.diff(t_array_i)[0]
        
        delta_t = np.diff(t_array_i)[0]
        
        return (t_array_i, delta_t, i)      
    
    def R(self, z):
        # Returns the distance R from the source to the observation point
        return np.sqrt(self.D**2 + z**2)  
    
    def E_section(self, z_ind_range):
        ind_start = z_ind_range[0]
        ind_end = z_ind_range[1]
        
        result = []
        
        for ind in range(ind_end - ind_start + 1):
            result.append(self.E_z(ind + ind_start))
            
        return result
        
    def E_z(self, ind):
        r = self.R(self.z[ind])
        delay = int(r/(c*self.model.dt))
        
        i_delayed = np.zeros(self.max_time_length())
        di_delayed = np.zeros(self.max_time_length())
        intI_delayed = np.zeros(self.max_time_length())
        
        i_delayed[delay:delay+self.model_results[ind][0].shape[0]] = self.model_results[ind][0]
        
        di_delayed[delay:delay+self.model_results[ind][1].shape[0]] = self.model_results[ind][1]
        
        intI_delayed[delay:delay+self.model_results[ind][2].shape[0]] = self.model_results[ind][2]
        intI_delayed[delay+self.model_results[ind][2].shape[0]:] = intI_delayed[delay+self.model_results[ind][2].shape[0]-1]
        
        E_es_factor  = ((2.0-3.0*(self.D/r)**2)*intI_delayed)  / r**3
        E_ind_factor = ((2.0-3.0*(self.D/r)**2)*i_delayed) / (c * r**2)
        E_rad_factor = -1.0*(((self.D**2)*di_delayed)   / ((c**2) * (r**3)) )
        
        #~ print(E_es_factor.shape,E_ind_factor.shape,E_rad_factor.shape)
        
        return (E_es_factor, E_ind_factor, E_rad_factor)
    
    def save_data(self):
        print("Saving data...")
        
        data = {'time':self.time-self.D/c, 'E_es':self.E_es, 'E_ind':self.E_ind, \
        'E_rad':self.E_rad, 'E_tot':self.E_tot, 'z_array':self.z, 'i':self.model.i, \
        'di':self.model.derivative(), 'D':self.D, 'Ht':self.Ht, 'v':self.v, \
        'lmb':self.lmb}

        pickle.dump(data, open('./data.p', "wb"))
        
        print("  - Done")
        
    def plot_data(self):
        print("Plotting results...")
        mpl.rcdefaults()
        mpl.rcParams['keymap.back'] = 'b'
        mpl.rcParams['keymap.forward'] = 'b'
        
        time = self.time - self.D/c
        xlims = [-2, 80]

        ### All fields in one figure

        fig = plt.figure()
        fig.suptitle('Distance from channel: %d m' % self.D)

        ax_es = fig.add_subplot(411)
        ax_es.plot(time*1E6, self.E_es)
        ax_es.set_ylabel('E_es (V/m)')
        ax_es.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
        ax_es.grid(True,which='both')
        ax_es.set_xlim(xlims)
        ax_es.autoscale(enable=True, axis='y', tight=True)

        ax_ind = fig.add_subplot(412)
        ax_ind.plot(time*1E6, self.E_ind)
        ax_ind.set_ylabel('E_ind (V/m)')
        ax_ind.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
        ax_ind.grid(True,which='both')
        ax_ind.set_xlim(xlims)
        ax_ind.autoscale(enable=True, axis='y', tight=True)

        ax_rad = fig.add_subplot(413)
        ax_rad.plot(time*1E6, self.E_rad)
        ax_rad.set_ylabel('E_rad (V/m)')
        ax_rad.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
        ax_rad.grid(True,which='both')
        ax_rad.set_xlim(xlims)
        ax_rad.autoscale(enable=True, axis='y', tight=True)

        ax = fig.add_subplot(414)
        ax.plot(time*1E6, self.E_tot)
        ax.set_ylabel('E (V/m)')
        ax.set_xlabel('Time ($\mu$s)')
        ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
        ax.grid(True,which='both')
        ax.set_xlim(xlims)
        ax.autoscale(enable=True, axis='y', tight=True)

        ### Total E-field

        if self.D == 70.0:
            meas = 'E_NW60'
        elif self.D == 180.0:
            meas = 'E_12F'
        elif self.D == 315.0:
            meas = 'dE_8'
        elif self.D == 391.0:
            meas = 'dE_9'
        elif self.D == 3000.0:
            meas = 'E_GOLF'
        elif self.D == 42000.0:
            meas = 'E_LOG'
    
        fo = pickle.load(open(self.fileSave, "rb"))
        E_meas = fo[meas]
        t = fo['time']*1E-6
        E_meas = E_meas[::int(len(E_meas)/len(t))]

        fig = plt.figure()
        fig.suptitle('Distance from channel: %d m' % self.D)

        ax = fig.add_subplot(111)
        ax.plot(t[:int(len(self.E_tot))]*1E6, E_meas[:int(len(self.E_tot))], 'g', label=meas)
        ax.plot(time*1E6, self.E_tot, label='E-total')
        ax.set_title('$E_{total}$')
        ax.set_ylabel('E (V/m)')
        ax.set_xlabel('Time ($\mu$s)')
        ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
        ax.grid(True,which='both')
        ax.set_xlim(xlims)
        ax.autoscale(enable=True, axis='y', tight=True)
        plt.legend()

        picker = df.pickerPlot(fig,ax)
        picker.plot()

        #~ plt.figure()
        #~ plt.plot(z_array,result)
        plt.show()

        ### E_es

        #~ fig = plt.figure()
        #~ ax = fig.add_subplot(111)
        #~ ax.plot(time*1E6, self.E_es)
        #~ ax.set_title('$E_{es}$')
        #~ ax.set_ylabel('E (V/m)')
        #~ ax.set_xlabel('Time ($\mu$s)')

        ### E_ind

        #~ fig = plt.figure()
        #~ ax = fig.add_subplot(111)
        #~ ax.plot(time*1E6, self.E_ind)
        #~ ax.set_title('$E_{ind}$')
        #~ ax.set_ylabel('E (V/m)')
        #~ ax.set_xlabel('Time ($\mu$s)')

        ### E_rad

        #~ fig = plt.figure()
        #~ ax = fig.add_subplot(111)
        #~ ax.plot(time*1E6, self.E_rad)
        #~ ax.set_title('$E_{rad}$')
        #~ ax.set_ylabel('E (V/m)')
        #~ ax.set_xlabel('Time ($\mu$s)')

        print("  - Done.")
        plt.show()
    
    def run(self):
        # Get current time for script timing purposes
        start = datetime.datetime.now()
        
        # Clear the terminal screen
        os.system("clear")

        print("-"*50)
        print("Return-Stroke Fields Simulation Using MTLE Model")
        print("            With No Reflections                 ")
        print("-"*50)
        
        print("Building data arrays...")
        self.model_results = self.model.run()
        print("  - Done.")
        
        print("Starting field calculations...")
        mult = 1024.0
        n_z = self.z_samples/mult
        
        que = [(int(i*mult), int((i+1)*mult-1)) for i in range(int(n_z))]

        p = Pool()
        
        answers = p.map(self.E_section, que)
        
        p.close()
        p.join()
        
        self.E_es_p = np.zeros((self.max_time_length(), self.z_samples))
        self.E_ind_p = np.zeros(self.E_es_p.shape)
        self.E_rad_p = np.zeros(self.E_es_p.shape)
        
        for i in range(int(n_z)):
            (z_low, z_high) = que[i]
            
            for j in range(z_high - z_low + 1):
                self.E_es_p[:, z_low+j] = answers[i][j][0]
                self.E_ind_p[:, z_low+j] = answers[i][j][1]
                self.E_rad_p[:, z_low+j] = answers[i][j][2]
                
        self.E_es = tl_factor*ae_factor*scipy.integrate.simps(self.E_es_p, dx=self.dz)
        self.E_ind = tl_factor*ae_factor*scipy.integrate.simps(self.E_ind_p, dx=self.dz)
        self.E_rad = tl_factor*ae_factor*scipy.integrate.simps(self.E_rad_p, dx=self.dz)
        
        self.E_tot = self.E_es + self.E_ind + self.E_rad
        
        self.time = np.arange(0, self.E_tot.shape[0]) * self.model.dt
        
        print("  - Done.")
        
        # Get the time difference between now and when the script started
        elapsed = datetime.datetime.now() - start

        # Calculate the number of minutes and seconds that corresponds to.
        (elapsed_min, elapsed_sec) = divmod(elapsed.seconds, 60)

        print("\n\nRun time (min:sec): %02d:%d " % (elapsed_min, elapsed_sec))

    
if __name__ == "__main__":
    sim = Simulation()
    print(sim.model.T_v(2e3)*1E6)
    #~ sys.exit(1)
    
    sim.run()
    sim.save_data()
    sim.plot_data()

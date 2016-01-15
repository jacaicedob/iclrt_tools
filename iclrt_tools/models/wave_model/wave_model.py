#!/usr/bin/env python
# Uses python3

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import other packages
import numpy as np
from scipy.integrate import cumtrapz,simps
import matplotlib.pyplot as plt
import pickle
import sys

import iclrt_tools.models.current_waves.current_waves as cw

C = 3.0E8                     # Speed of light (m/s)
mu0 = 4.0*np.pi*1.0E-7        # Free-space permeability (H/m)
eps0 = 1.0 / (mu0 * C**2)     # Free-space permittivity (F/m)
two_pi_e0 = 2*np.pi*eps0

def get_currents(currents, fileSave):
    ### Generate desired return-stroke waveform.

    #~ # Triangular wave used in Uman et al. (1975)
    #~ (t_array_i, i) = cw.triangular(peak=1.0E4, peak_time=1.0E-6, t_end=25E-6, \
                                   #~ samples=500.0)
                                   #~ 
    #~ t_end_i = t_array_i[-1]
    #~ delta_t = np.diff(t_array_i)[0]
#~ 
    #~ ### Generate the time derivative of the RS current waveform
    #~ di = np.gradient(i, delta_t)
    #~ i_r = i
    #~ ii_real = i
    #~ 
    #~ return (t_array_i, delta_t, i, i_r, ii_real, di, t_end_i)

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
        #~ if name != 'rs':
            #~ i = i_r
        
        # plt.plot(i)
        # plt.plot(ii_real)
        # plt.plot(i_r)
        # plt.show()
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
            
            # p = df.RelativeTimePlot(t_array_i, i_r)
            # p.plot()
            # plt.show()
            #
            #
            # from scipy.signal import savgol_filter
            # i_r = savgol_filter(i_r, 9, 5)
            # i_r = i_r[p.zero_ind:-1]# - i_r[p.zero_ind]
            #
            # plt.plot(i)
            # plt.plot(ii_real)
            #
            # p = df.pickerPlot(plt.gcf(), plt.gca())
            # p.plot()
            # plt.show()
            
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

class Wave(object):
    """
    Wave object that models a wave to be used in TL models. It assumes
    that time zero is the time at which the current at ground is
    measured.
    
    This is important to keep in mind for processes like M-components
    where there is current in the channel, and therefore fields, before
    the current is 'seen' at ground.
    
    CBC = channel-base current
    """
    def __init__(self, CBC, dt):
        self.CBC = CBC
        self.dt = dt
        
        self.set_z(0)
        
        self.CBC_derivative = np.gradient(self.CBC, self.dt)
        self.CBC_integral = cumtrapz(self.CBC, dx=self.dt, initial=0)
        self.length = len(self.CBC)
        
    def set_z(self, z):
        """
        Sets the value of z. It could be used in the functions below
        whose value may depend on the height z. Returns true if the value
        of z is valid in the model. For example, this method returns false
        if the value of z is larger than the length of the channel.
        """
        self.z = z
        return True
    
    def get_min_starttime(self):
        """
        The minimum time at which we see the current at ANY height in
        the channel. This is the same as the start time of the current wave.
        For RS, it would be 0 since there is no current anywhere
        in the channel before then, but for M-components, it would be
        some negative number since there is current on the channel 
        before it is measured at ground (the downward going wave).
        """
        return 0
        
    def get_max_endtime(self):
        """
        The maximum time for which we see the current at ANY height in
        the channel. For RS, it would be:
                        0 + Ht/v + len(waveform),
        which is the time the entire wave has reached the channel height Ht.

        M-components:
        For the downward wave this would be:
                    min_starttime + Ht/v + len(waveform).

        And for the upward wave this would be the same as the return stroke,
        since time 0 is the time at which current is measured at ground.
        """
        return 0  #self.length*self.dt
        
    def get_starttime(self):
        """
        The minimum time at which we see the current at height z.
        """
        return 0
        
    def get_derivative(self):
        """
        Returns a tuple containing the length of the derivative array
        as well as the derivative itself.
        """
        return self.length, self.CBC_derivative
        
    def get_current(self):
        """
        Returns a tuple containing the length of the current array
        as well as the current itself.
        """
        return self.length, self.CBC
        
    def get_integral(self):
        """
        Returns a tuple containing the length of the integral array
        as well as the integral itself.
        """
        return self.length, self.CBC_integral


class RS(Wave):
    def __init__(self, CBC, dt, velocity, Hstart, Hend, t_start,
                 attenuation=lambda z: 1):
        self.velocity = float(velocity)
        self.Hend = float(Hend)
        self.Hstart = float(Hstart)
        self.t_start = t_start
        self.attenuation = attenuation

        super(RS, self).__init__(CBC, dt)
        
    def set_z(self, z):
        if z > self.Hend:
            return False
        else:
            self.z = z
            return True
        
    def get_min_starttime(self):
        return self.t_start
        
    def get_max_endtime(self):
        return self.t_start + self.Hend/self.velocity + \
               self.length*self.dt
        
    def get_starttime(self):
        return self.t_start + self.z/self.velocity
        
    def get_derivative(self):
        return self.length, self.CBC_derivative*self.attenuation(self.z)
        
    def get_current(self):
        return self.length, self.CBC*self.attenuation(self.z)
        
    def get_integral(self):
        return self.length, self.CBC_integral*self.attenuation(self.z)


class DOWN(Wave):
    def __init__(self, current, dt, velocity, Hstart, Hend, t_start,
                 attenuation=lambda z: 1):
        self.velocity = float(velocity)
        self.Hstart = float(Hstart)
        self.Hend = float(Hend)
        self.t_start = float(t_start)
        self.attenuation = attenuation
        
        super(DOWN, self).__init__(current, dt)
        
    def set_z(self, z):
        if z > self.Hstart or z < self.Hend:
            return False
        else:
            self.z = z
            return True
        
    def get_min_starttime(self):
        return self.t_start
        
    def get_max_endtime(self):
        return self.t_start + self.Hstart/self.velocity +\
               self.length*self.dt
        
    def get_starttime(self):
        return self.t_start + (self.Hstart - self.z)/self.velocity
        
    def get_derivative(self):
        return self.length, self.CBC_derivative*self.attenuation(self.z)
        
    def get_current(self):
        return self.length, self.CBC*self.attenuation(self.z)
        
    def get_integral(self):
        return self.length, self.CBC_integral*self.attenuation(self.z)


class UP(Wave):
    def __init__(self, current, dt, velocity, Hstart, Hend, t_start,
                 attenuation=lambda z: 1):
        self.velocity = float(velocity)
        self.Hstart = float(Hstart)
        self.Hend = float(Hend)
        self.t_start = float(t_start)
        self.attenuation = attenuation
        
        super(UP, self).__init__(current, dt)
        
    def set_z(self, z):
        if z < self.Hstart or z > self.Hend:
            return False
        else:
            self.z = z
            return True
        
    def get_min_starttime(self):
        return self.t_start
        
    def get_max_endtime(self):
        return self.t_start + (self.Hend - self.Hstart)/self.velocity + \
               self.length*self.dt
        
    def get_starttime(self):
        return self.t_start + (self.z - self.Hstart)/self.velocity
        
    def get_derivative(self):
        return self.length, self.CBC_derivative*self.attenuation(self.z-self.Hstart)
        
    def get_current(self):
        return self.length, self.CBC*self.attenuation(self.z-self.Hstart)
        
    def get_integral(self):
        return self.length, self.CBC_integral*self.attenuation(self.z-self.Hstart)


class REF(Wave):
    def __init__(self, current, dt, velocity, Hstart, Hend, t_start,
                 attenuation=lambda z: 1):
        self.velocity = float(velocity)
        self.Hend = float(Hend)
        self.Hstart = float(Hstart)
        self.t_start = float(t_start)
        self.attenuation = attenuation
        
        super(REF, self).__init__(current, dt)
        
    def set_z(self, z):
        if z > self.Hend:
            return False
        else:
            self.z = z
            return True
        
    def get_min_starttime(self):
        return self.t_start
        
    def get_max_endtime(self):
        return self.t_start + self.Hend/self.velocity + self.length*self.dt
        
    def get_starttime(self):
        return self.t_start + self.z/self.velocity
        
    def get_derivative(self):
        return self.length, self.CBC_derivative*self.attenuation(self.z)
        
    def get_current(self):
        return self.length, self.CBC*self.attenuation(self.z)
        
    def get_integral(self):
        return self.length, self.CBC_integral*self.attenuation(self.z)        


class field_model(object):
    """
    Calculates the E-fields due to several waves. The function
    calc_fields() allows to pass a list of distances and calculates the
    fields at each distance.
    """    
    
    def __init__(self, current_waves, dt, channel_height, fields='111'):
        """
        :param current_waves: a list of Wave objects to model
        :param dt: time step desired
        :param channel_height: the maximum height of the lightning channel
        :param fields: a mask to specify which fields are to be calculated. The
              MSB refers to the radiation (E_rad) component, the middle bit
              refers to the induction (E_ind) component, and the LSB refers to
              the electrostatic (E_es) component. A combination of bits allows
              the calculation of multiple fields at the same time.
                  '000' -> None
                  '001' -> E_es
                  '010' -> E_ind
                  '100' -> E_rad
                  '111' -> All
        :return:  nothing
        """
        self.current_waves = current_waves
        self.dt = dt
        self.channel_height = channel_height
        self.set_fields(fields)

        # Pick the earliest starttime and latest endtime of ALL waves.
        self.min_starttime = float('inf')
        self.max_endtime = -float('inf')
        
        for wave in self.current_waves:
            if wave.get_min_starttime() < self.min_starttime:
                self.min_starttime = wave.get_min_starttime()
                
            if wave.get_max_endtime() > self.max_endtime:
                self.max_endtime = wave.get_max_endtime()
                
    def set_fields(self, fields):
        """
        Reads the fields mask and assigns the value to a flag for each
        field component. These will be used in the integrand() function
        to decide which components to calculate.
        """
        self.do_static = bool(int(fields[2]))
        self.do_induction = bool(int(fields[1]))
        self.do_radiation = bool(int(fields[0]))
        
    def integrand(self, z, d, output_starttime, output, currents):
        """
        Calculates the value of the integrand of the height integral in
        the TL model equations and assigns it to the output array for
        each height z. It includes the free-space delay to the 
        measurement at distance d.
        
        It uses convolution to remove the stepping errors that occur
        when the time delay is not an integer multiple of dt and 
        therefore the indices of the output array will be staggered. 
        It assigns weights to each index based on an initial time
        displacement and convolves it with the current waveform to get
        a smooth integrand.
        
        output_starttime is the time at which the output starts.
        """
        z2 = z*z
        d2 = d*d
        R = np.sqrt(z2 + d2)
        retarded_time = R/C
        
        if self.do_static:
            electrostatic_factor = (2.0*z2 - d2)/(R**5.0)
        if self.do_induction:
            induction_factor = (2.0*z2 - d2)/(C*R**4.0)
        if self.do_radiation:
            radiation_factor = d2/(C*C*(R**3.0))
        
        for wave in self.current_waves:
            if not(wave.set_z(z)):
                continue
                
            start_time = wave.get_starttime()
            total_time = start_time + retarded_time
            
            if total_time < output_starttime:
                print('Timing error')
                exit(1)
                
            total_point_delay = (total_time - output_starttime)/self.dt
            n_point_delay = int(total_point_delay)
            remainder_delay = total_point_delay - n_point_delay
            weights = [1.0 - remainder_delay, remainder_delay]
            
            if self.do_static:
                num_current_points, integral_current = wave.get_integral()
                output[n_point_delay:n_point_delay+num_current_points+1] += \
                    np.convolve(integral_current, weights)*electrostatic_factor
                
            if self.do_induction:
                num_current_points, current = wave.get_current()
                output[n_point_delay:n_point_delay+num_current_points+1] += \
                    np.convolve(current, weights)*induction_factor
                
                currents[n_point_delay:n_point_delay+num_current_points+1] += \
                    np.convolve(current, weights)
                
            if self.do_radiation:
                num_current_points, derivative_current = wave.get_derivative()
                output[n_point_delay:n_point_delay+num_current_points+1] -= \
                    np.convolve(derivative_current, weights)*radiation_factor

    def integrand_individual(self, wave_index, z, d, output_starttime, output,
                             currents):
        """
        Calculates the value of the integrand of the height integral in
        the TL model equations and assigns it to the output array for
        each height z for a single wave. It includes the free-space delay to
        the measurement at distance d.

        It uses convolution to remove the stepping errors that occur
        when the time delay is not an integer multiple of dt and
        therefore the indices of the output array will be staggered.
        It assigns weights to each index based on an initial time
        displacement and convolves it with the current waveform to get
        a smooth integrand.

        output_starttime is the time at which the output starts.
        wave_index specifies which wave in self.waves to use
        """
        z2 = z*z
        d2 = d*d
        R = np.sqrt(z2 + d2)
        retarded_time = R/C

        if self.do_static:
            electrostatic_factor = (2.0*z2 - d2)/(R**5.0)
        if self.do_induction:
            induction_factor = (2.0*z2 - d2)/(C*R**4.0)
        if self.do_radiation:
            radiation_factor = d2/(C*C*(R**3.0))

        wave = self.current_waves[wave_index]

        if not(wave.set_z(z)):
            return 0

        start_time = wave.get_starttime()
        total_time = start_time + retarded_time

        if total_time < output_starttime:
            print('Timing error')
            exit(1)

        total_point_delay = (total_time - output_starttime)/self.dt
        n_point_delay = int(total_point_delay)
        remainder_delay = total_point_delay - n_point_delay
        weights = [1.0-remainder_delay, remainder_delay]

        if self.do_static:
            num_current_points, integral_current = wave.get_integral()
            output[n_point_delay:n_point_delay+num_current_points+1] += \
                np.convolve(integral_current, weights)*electrostatic_factor

        if self.do_induction:
            num_current_points, current = wave.get_current()
            output[n_point_delay:n_point_delay+num_current_points+1] += \
                np.convolve(current, weights)*induction_factor

            currents[n_point_delay:n_point_delay+num_current_points+1] += \
                np.convolve(current, weights)

        if self.do_radiation:
            num_current_points, derivative_current = wave.get_derivative()
            output[n_point_delay:n_point_delay+num_current_points+1] -= \
                np.convolve(derivative_current, weights)*radiation_factor

    def calc_fields(self, distances, n_z_points, temp_field=None):
        """
        Performs the field calculations.
        
        Parameters:
            - distances: an list containing all the desired distances
                         from the channel
            - n_z_points: the number of points to use for the height
                          array
            - temp_field: a mask to override the original field variable
                          and calculate another combination of fields
        """
        
        if temp_field is not None:
            old_field = [self.do_static, self.do_induction, self.do_radiation]
            self.set_fields(temp_field)
            
        Z_array, dz = np.linspace(0, self.channel_height, n_z_points,
                                  retstep=True)

        num_distances = len(distances)
        max_d2 = np.max(distances)**2
        min_d = np.min(distances)
        
        min_t = self.min_starttime + min_d/C
        max_t = self.max_endtime + np.sqrt(max_d2 +
                self.channel_height*self.channel_height)/C
        n_t_points = int((max_t - min_t)/self.dt) + 1
        
        T_array = np.arange(n_t_points)*self.dt + min_t
        
        field_matrices = [np.zeros((n_t_points, n_z_points))
                          for x in range(int(num_distances))]
        
        current_matrices = [np.zeros((n_t_points, n_z_points))
                            for x in range(int(num_distances))]
        
        for z_i in range(int(n_z_points)):
            for d_i in range(int(num_distances)):
                self.integrand(Z_array[z_i], distances[d_i], min_t,
                               field_matrices[d_i][:, z_i],
                               current_matrices[d_i][:, z_i])
            
        Es = [-simps(matrix, dx=dz)/two_pi_e0 for matrix in field_matrices]
        
        if temp_field is not None:
            self.do_static, self.do_induction, self.do_radiation = old_field
        
        return T_array, Es, current_matrices

    def calc_fields_individual(self, wave_index, distances, n_z_points,
                               temp_field=None):
        """
        Performs the field calculations.

        Parameters:
            - distances: an list containing all the desired distances
                         from the channel
            - n_z_points: the number of points to use for the height
                          array
            - temp_field: a mask to override the original field variable
                          and calculate another combination of fields
        """

        if temp_field is not None:
            old_field = [self.do_static, self.do_induction, self.do_radiation]
            self.set_fields(temp_field)

        Z_array, dz = np.linspace(0, self.channel_height, n_z_points,
                                 retstep=True)
        num_distances = len(distances)
        max_d2 = np.max(distances)**2
        min_d = np.min(distances)

        min_t = self.min_starttime + min_d/C
        max_t = self.max_endtime + np.sqrt(max_d2 +
                self.channel_height*self.channel_height)/C
        n_t_points = int((max_t-min_t)/self.dt)+1

        T_array = min_t + np.arange(n_t_points)*self.dt

        field_matrices = [np.zeros((n_t_points, n_z_points))
                          for x in range(int(num_distances))]

        current_matrices = [np.zeros((n_t_points,n_z_points))
                            for x in range(int(num_distances))]

        for z_i in range(int(n_z_points)):
            for d_i in range(int(num_distances)):
                self.integrand_individual(wave_index, Z_array[z_i],
                                          distances[d_i], min_t,
                                          field_matrices[d_i][:,z_i],
                                          current_matrices[d_i][:,z_i])

        Es = [-simps(matrix, dx=dz)/two_pi_e0 for matrix in field_matrices]

        if temp_field is not None:
            self.do_static, self.do_induction, self.do_radiation = old_field

        # plt.imshow(field_matrices[0][:,::8], interpolation='nearest')
        # plt.colorbar(orientation='vertical')
        # plt.show()

        return T_array, Es, current_matrices

    def calc_field_OneDistance(self, distance, n_z_points, temp_field=None,
                               plot_matrix=False):
        if temp_field is not None:
            old_field = [self.do_static, self.do_induction, self.do_radiation]
            self.set_fields(temp_field)
            
        Z_array, dz = np.linspace(0, self.channel_height, n_z_points,
                                  retstep=True)
        
        min_t = self.min_starttime + distance/C
        max_t = self.max_endtime + np.sqrt(distance*distance +
                                 self.channel_height*self.channel_height)/C
        n_t_points = int((max_t-min_t)/self.dt)+1
        
        T_array = min_t + np.arange(n_t_points)*self.dt
        
        field_matrix=np.zeros((n_t_points,n_z_points))
        
        for z_i in range(n_z_points):
            self.integrand(Z_array[z_i], distance, min_t, field_matrix[:,z_i])
            
        Es=-simps(field_matrix, dx=dz)/two_pi_e0
        
        if temp_field!=None:
            self.do_static, self.do_induction, self.do_radiation=old_field
            
        if plot_matrix:
            plt.matshow(-field_matrix/two_pi_e0)
            plt.colorbar()
            plt.show()
        
        return T_array, Es
        
    
# if __name__=='__main__':
    # Ht = 2.0E3      # Top of channel (m)
    # Hr = 280.0       # Height of discontinuity
    # D = [92.0]       # Observation distance from bottom of channel (m)
    #
    # ## Speed and attenuation
    # v_r = 1.4E8 # Reflected wave speed (m/s)
    # v = 1.4E8   # Incident wave speed (m/s)
    # lmb = 3.0E3   # Lambda boundaries bottom to top
    # t_tot = 40E-6
    #
    # ## Data Files
    #
    # fileSaveCurrents = '/home/jaime/Documents/Python Code/Models/CurrentFit/DataFiles/UF0920_I_RS3.p'
    # fileSaveCurrentsDelay = 5.0E-6 # Delay from start of current to dip
    #
    # currents = '/home/jaime/Documents/My Papers/Ongoing/Current Reflections/Models/MTLE/1 Reflection/ResultsGeneralTL/UF0920RS3/currents.p'
    #
    # (t_array_i, delta_t, i, i_r, ii_real, di, t_end_i) = \
    #     get_currents(fileSaveCurrents)
    #
    # rs_wave = RS(i, delta_t, v, 0, Ht, 0, attenuation=lambda z: np.exp(-z/lmb))
    #
    # down_wave = DOWN(i_r, delta_t, v_r, Hr, Ht, Hr/v+fileSaveCurrentsDelay)
    #
    # up_wave = UP(i_r, delta_t, v, Hr, Ht, Hr/v+fileSaveCurrentsDelay,
    #              attenuation=lambda z: np.exp(-z/lmb))
    #
    # ref_wave = REF(i_r, delta_t, v_r, 0, Ht, Hr/v + Hr/v_r +
    #                fileSaveCurrentsDelay)
    #
    # waves = [rs_wave, down_wave, up_wave, ref_wave]
    # file_names = ['./data_RS.p', './data_down.p', './data_up.p',
    #               './data_Ref.p']
    # data = {}
    #
    # fm = field_model(waves, delta_t, Ht, fields='111')
    #
    # t_array, E_es, __ = fm.calc_fields(D, Ht, temp_field='001')
    # t_array, E_ind, __ = fm.calc_fields(D, Ht, temp_field='010')
    # t_array, E_rad, __ = fm.calc_fields(D, Ht, temp_field='100')
    # t_array, E_tot, currents = fm.calc_fields(D, Ht, temp_field='111')
    #
    # data['time'] = t_array - D[0]/C
    # data['E_es'] = E_es[0]
    # data['E_ind'] = E_ind[0]
    # data['E_rad'] = E_rad[0]
    # data['E'] = E_tot[0]
    # data['D'] = D[0]
    # data['v'] = wave.velocity
    # data['lmb'] = lmb
    # data['Hstart'] = wave.Hstart
    # data['i'] = wave.CBC
    # data['di'] = wave.CBC_integral
    #
    # data['i_array'] = currents[0]
    # data['di_array'] = 0  #di_array
    # data['z_array'] = 0  #z_array
    #
    # save_data('./data_sum.p', data)
    #
    # for j, wave in enumerate(waves):
    #
    #     t_array, E_es, __ = fm.calc_fields_individual(j, D, Ht, temp_field='001')
    #     t_array, E_ind, __ = fm.calc_fields_individual(j, D, Ht, temp_field='010')
    #     t_array, E_rad, __ = fm.calc_fields_individual(j, D, Ht, temp_field='100')
    #     t_array, E_tot, currents = fm.calc_fields_individual(j, D, Ht, temp_field='111')
    #
    #     #~ data = {}
    #
    #     data['time'] = t_array - D[0]/C
    #     data['E_es'] = E_es[0]
    #     data['E_ind'] = E_ind[0]
    #     data['E_rad'] = E_rad[0]
    #     data['E'] = E_tot[0]
    #     data['D'] = D[0]
    #     data['v'] = wave.velocity
    #     data['lmb'] = lmb
    #     data['Hstart'] = wave.Hstart
    #     data['i'] = wave.CBC
    #     data['di'] = wave.CBC_integral
    #
    #     data['i_array'] = currents[0]
    #     data['di_array'] = 0  #di_array
    #     data['z_array'] = 0  #z_array
    #
    #     save_data(file_names[j], data)
    #
    #
    #
    # print(data['time'].shape, data['E'].shape)
    #
    # plt.figure()
    # plt.plot(data['time']*1E6, data['E'])
    #
    # plt.figure()
    # plt.plot(data['i_array'][:,0])
    # plt.show()

#!/usr/bin/env python

"""
This program calculates the electric and magnetic fields of the lightning
return stroke (RS) using the Transmission Line (TL) model from Uman 1975.

It does not account for any reflections of the RS wave either a height z 
above the ground or ground reflections.

This implementation uses the multiprocessing module

execfile('/Volumes/OSX2/Users/jaime/My Papers/Current Reflections/Models/TL/No Reflections/tl_mp.py')

execfile('/home/jaime/UF/Graduate School/ICLRT/My Papers/Current Reflections/Models/TL/No Reflections/tl_mp.py')

"""

#############################################################################
### Package imports
import numpy as np
import dfplots as df
import matplotlib.pyplot as plt 

import time
from scipy import integrate   
#~ np.set_printoptions(threshold=np.nan)

from multiprocessing import Pool
import CurrentWaves as cw
import sys

##############################################################################
### Function Definitions
    
def E_es_integrand(z,tp):
    # Returns the integrand for the electrostatic component of E
    r = R(z)
    return ((2-3.0*(D/r)**2)/r**3)*I_r(z,tp,r)*np.exp(-(z-Hb)/decay)
    #~ return I_r(z,tp,r)

def E_ind_integrand(z,tp):
    #~ print "E_ind at z'=%0.2f m and t'=%0.2f us" % (z, tp*1E6)
    # Returns the integrand for the induction component of E
    r = R(z)
#~     return ((2.0-3.0*(D/r)**2)/(c * r**2))*I_r(z,tp,r)*np.exp(-(z-Hb)/decay)
    return ((2.0*z**2 - D**2) / (c * r**4))*I_r(z,tp,r)*np.exp(-(z-Hb)/decay)
    
def E_rad_integrand(z,tp):
    # Returns the integrand for the radiation component of E
    #~ print "E_rad at z'=%0.2f m and t'=%0.2f us" % (z, tp*1E6)
    r = R(z)
    return (D**2 / (c**2 * r**3))*di_r(z,tp,r)*np.exp(-(z-Hb)/decay)

def di_r(z,tp,r):
    # Returns the retarded time derivative of i
    fs_delay = tp-r/c   # Delay due to free space propagation to 
                        # observation pt.

    if fs_delay < 0:
        return 0

    else:
        z_delay = fs_delay - (z-Hb)/v   # Delay due to velocity of wave. The
                                        # term Hb is added to make the wave
                                        # start at z=Hb and not z=0

        if z_delay < 0:
            return 0
        else:
            j = int(round(z_delay/delta_t))
            if j >= di.shape[0]:
                return 0
            else:
                return di[j]

def I_r(z,tp,r):
    # Returns retarted current of the initial current wave
    fs_delay = tp-r/c   # Delay due to free space propagation to 
                        # observation pt.

    if fs_delay < 0:
        return 0
    else:
        z_delay = fs_delay - (z-Hb)/v   # Delay due to velocity of wave. The
                                        # term Hb is added to make the wave
                                        # start at z=Hb and not z=0
        if z_delay < 0:
            return 0
        else:
            j = int(round(z_delay/delta_t))
            if j >= i.shape[0]:
                return 0
            else:
                #~ print "a"
                return i[j]
        
def R(z):
    # Returns the distance R from the source to the observation point
    return np.sqrt(D**2 + z**2)    
    
def multi_E(t):
#~  print "E_es"   
#~     result_E_es = custom_dblquad(E_es_integrand,
#~                                  RR/c,t, # tp (tprime) limits
#~                                  lambda zp:Hb, #z limits
#~                                  lambda zp:Ht,
#~                                  epsabs=1.49E-15,
#~                                  epsrel=1.49E-15, 
#~                                  limit=1000, full_output=1)
#~ 
#~     error_E_es = result_E_es[1]
#~     result_E_es = result_E_es[0]

    result_E_es = integrate.dblquad(E_es_integrand, \
                                    RR/c,t, # tp (tprime) limits
                                    lambda zp:Hb, #z limits
                                    lambda zp:Ht, \
                                    epsabs=1.49E-15, \
                                    epsrel=1.49E-15)
    
    error_E_es = result_E_es[0]
    result_E_es = result_E_es[1]

#~  print "E_ind"
#~     result_E_ind = integrate.quad(E_ind_integrand,Hb,Ht,t, 
#~                                   limit=1000,epsabs=1.49E-15,
#~                                   epsrel=1.49E-15, limlst=1000,
#~                                   full_output=1)
#~                                                
#~     error_E_ind = result_E_ind[1]
#~     result_E_ind = result_E_ind[0]

#~ print "E_rad"
#~     result_E_rad = integrate.quad(E_rad_integrand,Hb,Ht,t,
#~                                   limit=1000,epsabs=1.49E-15,
#~                                   epsrel=1.49E-15, limlst=1000,
#~                                   full_output=1)
#~ 
#~     error_E_rad = result_E_rad[1]
#~     result_E_rad = result_E_rad[0]
    
    return (result_E_es, 0, 0)
    #~ return (result_E_es, result_E_ind, result_E_rad)



if __name__ == "__main__":
    
    ###########################################################################
    ### Constants

    c = 3.0E8             # Speed of light (m/s)
    mu0 = 4*np.pi*1E-7    # Free-space permeability (H/m)
    eps0 = 1/mu0/(c**2)     # Free-spae permittivity (F/m)
    
    RR = 300    # meters
    theta = np.array([75]) * np.pi / 180 #np.array([90]) * np.pi / 180 # radians
    
    Hbb = RR / np.sqrt(1 + (np.tan(theta))**2) #np.zeros(theta.shape[0])
    
    DD = Hbb * np.tan(theta) #np.ones(1)*RR
    
    Htt = Hbb + 100      # meterss
    v = 1.5E8           # m/s
    
    M = 1     # Amplitude multiplier
    
    decay = 25 # np.inf          # meters

    ###########################################################################
    ### Main Code    
    start = time.time()
    samples = 2.5E3     # Number of samples of the current waveform
    
    t_end_i = 2.5    # Length of incident current waveform in useconds                  
    
    ##### Current waveshape from Jerauld (2007)
    alpha1 = 118 # kA/us
    alpha2 = 10.5 # kA/us
    alpha = [alpha1, alpha2]
    beta = 1.85
    Tpeak = 0.5  # us
    gamma = 20E-3  # us
    
    (t_array_i, di, err) = cw.jerauld_di_dt_2007(alpha, beta, Tpeak, gamma, \
                                         t_end_i, samples)
    if err:
        print err
        sys.exit(1)
    
    delta_t = np.diff(t_array_i)[0]
    
    i = integrate.cumtrapz(y=di, dx=delta_t, initial=0) # kA
    
    di *= 1E9      # A/s
    i *= 1E3       # A
    t_array_i *= 1E-6   # s
    delta_t *= 1E-6 # s
    
#~     fig = plt.figure()
#~     ax = fig.add_subplot(211)
#~     ax.plot(t_array_i*1E6, di)
#~     #~ 
#~     ax2 = fig.add_subplot(212)
#~     ax2.plot(t_array_i*1E6,i)
#~     #~ 
#~     p1 = df.plotdf(fig,ax)
#~     p2 = df.plotdf(fig, ax2)
#~     #~ 
#~     wrapper = df.syncdf([p1, p2])
#~     wrapper.plot_all()
#~          
#~     plt.show()
#~          
#~     sys.exit(1)
    p5 = []
    
    for xx in xrange(DD.shape[0]):
    
        Ht = Htt[xx]
        Hb = Hbb[xx]
        D = DD[xx]
    
        t_max = ((Ht-Hb)/v + np.sqrt(Ht**2+D**2)/c + t_end_i*1E-6) # Largest time to 
                                                              #compute fields
                                                              # in seconds
        t_array = np.arange(RR/c,t_max,delta_t)    # Time array for loop iteration
    
        print "Simulation start time: %s" % time.strftime("%H:%M:%S", time.localtime())
        print ""
        print "D = %0.2f meters" % (D)
        print "%0.2f < z' < %0.2f meters" % (Hb, Ht)
        print "%0.2f < t < %0.2f us" % (t_array[0]*1E6, t_array[-1]*1E6)
        print "%0.2f < r < %0.2f meters" % (R(Hb), R(Ht))
        print "delta_t = %0.2f ns" % (delta_t*1E9)
        #~ sys.exit(1)

        E_es = np.zeros(t_array.shape)
        E_ind = np.zeros(t_array.shape)
        E_rad = np.zeros(t_array.shape)

        print "Observation distance: %0.2f meters" % D
        print "Total iterations: %d" % t_array.shape[0]

        print "\n"
        print "-" * 50
        print "Performing Iterations"
        print "-" * 50

        tt = [t_array[k] for k in xrange(t_array.shape[0]) if True]
        
        p = Pool()
        answers = p.map(multi_E, tt)
    
        p.close()
        p.join()
        
        print "Done!"
        print "\n"
        print "-" * 50
        print "Parsing Results"
        print "-" * 50

        k = 0
        for answer in answers:
            E_es[k] = answer[0]
            E_ind[k] = answer[1]
            E_rad[k] = answer[2]

            k += 1
            
##### Calculate E_es a different way
        #~ delta_z = 0.1
        #~ z_array = np.arange(Hb, Ht, delta_z)
        #~ integrand = np.zeros(t_array.shape)
    #~ 
        #~ result_A  = integrate.quad(A_integrand, Hb, Ht, limit=1000, \
                                          #~ epsabs=1.49E-15, epsrel=1.49E-15, \
                                          #~ limlst=1000, full_output=1)
        #~ A = result_A[0]
                                  
        #~ print ""
        #~ print result_A[0]

        #~ for j in xrange(t_array.shape[0]):
            #~ t = t_array[j]
        #~ 
            #~ sum = 0
        #~ 
            #~ for zp in z_array:
                #~ r = R(zp)
            #~ 
            #~ 
                #~ sum += A*I_r(zp,t,r)*np.exp(-(zp-Hb)/decay)                                    
                #~ 
            #~ integrand[j] = sum
    #~ 
    #~ 
        #~ for k in xrange(integrand.shape[0]-1):
            #~ k += 1
            #~ E_es[k] = integrate.simps(integrand[:k])
#####            


        print "Done!"
        print "\n"
        print "-" * 50
        print "Summing up the individual components of B and E..."
        print "-" * 50

        E_es =  (1.0/2.0/np.pi/eps0) * M * E_es
        E_ind =  (1.0/2.0/np.pi/eps0) * M * E_ind
        E_rad =  -(1.0/2.0/np.pi/eps0) * M * E_rad
        E_tot = E_es + E_ind + E_rad
        
        E_es *= -1
        E_ind *= -1
        E_rad *= -1
        E_tot *= -1
        
        dE_tot = np.gradient(E_tot, delta_t)
        
#~         I_tl = 2.0*np.pi*(c**2)*D*eps0*np.abs(E_tot)/v
    
        #~ E_es = -1 * E_es
        #~ E_ind = -1 * E_ind
        #~ E_rad = -1 * E_rad
        #~ E_tot = -1 * E_tot  # AE sign convention

        ### Save data
        #print "\n"
        #print "-" * 50
        #print "Saving the data to a file..."
        #print "-" * 50
        #
        #tfile = './%04dSamples/t' % samples
        #np.save(tfile,t_array)
        #
        #E_es_file = './%04dSamples/E_es_%dkm' % (samples,D*1E-3)
        #E_ind_file = './%04dSamples/E_ind_%dkm' % (samples,D*1E-3)
        #E_rad_file = './%04dSamples/E_rad_%dkm' % (samples,D*1E-3)
        #E_tot_file = './%04dSamples/E_tot_%dkm' % (samples,D*1E-3)
        #np.save(E_es_file,E_es)
        #np.save(E_ind_file,E_ind)
        #np.save(E_rad_file,E_rad)
        #np.save(E_tot_file,E_tot)

        ### Plots
        print "Done!"
        print "\n"
        print "-" * 50
        print "Plotting the results..."
        print "-" * 50

        #~ fig = plt.figure('Input Current Waveform')
        #~ ax = fig.add_subplot(111)
        #~ lines  = ax.plot(t_array_i*1E6, i*1E-3)
        #~ ax.set_xlabel('Time ($\mu$sec)')
        #~ ax.set_ylabel('I $\\times 10^{-3}$(A)')
        #~ ax.set_title('Input current waveform i(z,t)')
    #~  #s = './%04dSamples/Figures/I.jpg' % (samples)
    #~  #plt.savefig(s, format='jpg')
    #~  
    #~  fig = plt.figure('Input Current Waveform Derivative')
    #~  ax = fig.add_subplot(111)
    #~  lines = ax.plot(t_array_i*1E6, di*1E-3)
    #~  ax.set_xlabel('Time ($\mu$sec)')
    #~  ax.set_ylabel('dI/dt $\\times 10^{-3}$(A)')
    #~  ax.set_title('Input current di(z,t)')

        fig = plt.figure('Currents')
        ax1 = fig.add_subplot(2,1,1)
        ax1.plot(t_array_i*1E6, i)
        ax1.set_ylabel('I (kA)')
        ax1.set_title('Original Input Current')
        ax2 = fig.add_subplot(2,1,2)
        ax2.plot((t_array-D/c)*1E6, I_tl)
        ax2.set_xlabel('Time ($\mu$sec)')
        ax2.set_ylabel('$I_{TL}$ (kA)')
        ax2.set_title('Calculated RS Current')
        
        p5 = df.plotdf(fig, ax1)
        p6 = df.plotdf(fig, ax2)

        fig = plt.figure('Electric Fields')
        ax1 = fig.add_subplot(4,1,1)
        ax1.plot((t_array-D/c)*1E6,E_es*1E-3)
        s = 'Electric fields ($kV/m$) at D = %0.3f km' % (D*1.0E-3)
        ax1.set_title(s)
        ax1.set_ylabel('E_es ($kV/m$)')
        ax2 = fig.add_subplot(4,1,2)
        ax2.plot((t_array-D/c)*1E6,E_ind*1E-3)
        ax2.set_ylabel('E_ind ($kV/m$)')
        ax3 = fig.add_subplot(4,1,3)
        ax3.plot((t_array-D/c)*1E6,E_rad*1E-3)
        ax3.set_ylabel('E_rad ($kV/m$)')
        ax4 = fig.add_subplot(4,1,4)
        ax4.plot((t_array-D/c)*1E6,E_tot*1E-3)
        ax4.set_ylabel('E_tot ($kV/m$)')
        ax4.set_xlabel('Time ($\mu$sec)')
        #s = './%04dSamples/Figures/E_%fkm.jpg' % (samples,D*1E-3)
        #plt.savefig(s, format='jpg')
        
        p1 = df.plotdf(fig, ax1)
        p2 = df.plotdf(fig, ax2)
        p3 = df.plotdf(fig, ax3)
        p4 = df.plotdf(fig, ax4)

        #~ fig = plt.figure()
        #~ ax = fig.add_subplot(111)
        #~ ax.plot((t_array-D/c)*1E6,E_tot*1E-3)
        #~ s = 'Total Electric field at R = %f m, $\\theta$ = %f' % (RR, theta[xx]*180/np.pi)
        #~ ax.set_title(s)
        #~ ax.set_xlabel('Time ($\mu$sec)')
        #~ ax.set_ylabel('E ($kV/m$)')
    #~ 
        #~ p5.append(df.plotdf(fig, ax))
        #~ 
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot((t_array-D/c)*1E6,dE_tot*1E-9)
        s = 'Total dE/dt at R = %f m, $\\theta$ = %f' % (RR, theta[xx]*180/np.pi)
        ax.set_title(s)
        ax.set_xlabel('Time ($\mu$sec)')
        ax.set_ylabel('dE/dt ($kV/m/\mu sec$)')
        #~ p5.append(df.plotdf(fig, ax))
    #~ 
        #s = './%04dSamples/Figures/E_tot_%dkm.jpg' % (samples,D*1E-3)
        #plt.savefig(s, format='jpg')

    
    synced = df.syncdf([p1, p2, p3, p4])
    synced.plot_all()
    
#~     synced2 = df.syncdf([p5, p6])
#~     synced2.plot_all()
    
    print "Done!\n\n"
    
    elapsed = time.time()-start
    print "Run time (minutes): ", elapsed/60
    
    #~ for pp in p5:
        #~ pp.plot()
    
    plt.show()
    #    plt.close('all')

    

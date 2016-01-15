#!/usr/bin/env python

import numpy as np
import dfplots as df
import matplotlib.pyplot as plt 

import time
from scipy import integrate	  

from multiprocessing import Pool
import CurrentWaves as cw
import sys


def I_r(z,tp,r):
	# Returns retarted current of the initial current wave
	fs_delay = tp-r/c	# Delay due to free space propagation to 
						# observation pt.

	if fs_delay < 0:
		return 0
	else:
		z_delay = fs_delay - (z-Hb)/v	# Delay due to velocity of wave. The
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

def A_integrand(z):
	r = R(z)
	return (2*(z**2)- D**2)/(r**5)
	
def E_es_integrand(tp, z, r, A):
#~	   print tp,z, r
	return A*I_r(z,tp,r)*np.exp(-(z-Hb)/decay)
	
def E_es_integrand1(z,tp):
	# Returns the integrand for the electrostatic component of E
	r = R(z)
	return ((2-3.0*(D/r)**2)/r**3)*I_r(z,tp,r)*np.exp(-(z-Hb)/decay)
#~	   return I_r(z,tp,r)


if __name__ == "__main__":

	###########################################################################
	### Constants

	c = 3.0E8			  # Speed of light (m/s)
	mu0 = 4*np.pi*1E-7	  # Free-space permeability (H/m)
	eps0 = 1/mu0/c**2	  # Free-spae permittivity (F/m)
	
	RR = 300	# meters
	theta = 0 * np.pi / 180 # radians
	
	Hbb = 300#RR / np.sqrt(1 + (np.tan(theta))**2)
	
	DD = Hbb * np.tan(theta)
	
	Htt = Hbb + 100		  # meterss
	v = 1.5E8			# m/s
	
	M = 1	  # Amplitude multiplier
	
	decay = 25			# meters

	###########################################################################
	### Main Code	 
	
	start = time.time()
	
	samples = 25
	t_end_i = 2.5E-6 # s
	
	##### Current waveshape from Jerauld (2007)
	alpha1 = 118 # kA
	alpha2 = 10.5 # kA
	alpha = [alpha1, alpha2]
	beta = 1.85
	Tpeak = 0.5 # us
	gamma = 20E-3 # us
	
	(t_array_i, di, err) = cw.jerauld_di_dt_2007(alpha, beta, Tpeak, gamma, \
										 t_end_i, samples)

#~	(t_array_i, i) = cw.triangular(peak=1E4, peak_time=1E-6, t_end=25E-6, \
#~					 samples=samples)
	if err:
		print err
		sys.exit(1)
	
	delta_t = np.diff(t_array_i)[0] # s
	delta_z = 1 # m
	
	i = integrate.cumtrapz(y=di, dx=delta_t, initial=0)	   # kA

#~	di = np.gradient(i,delta_t)
	
	
	di *= 1E9	# A/s
	i *= 1E3   # A
	
	D = DD
	Hb = Hbb
	Ht = Htt
		 
	t_max = ((Ht-Hb)/v + np.sqrt(Ht**2+D**2)/c + t_end_i)	# Largest time to 
															  #compute fields 
															  # in s
#~	   t_array = np.arange(RR/c,t_max,delta_t)	  # Time array for loop iteration
	t_array = np.arange(0,t_max,delta_t) # s
	z_array = np.arange(Hb, Ht, delta_z)	# m
	
#~	   print z_array
	r_array = np.zeros(z_array.shape[0])	   
	
	print "Calculating r_array"
	for j in xrange(r_array.shape[0]):
		r_array[j] = R(z_array[j])
	
	
	##### Iterations
	
	print "-" * 50
	print "D = %0.2f meters" % (D)
	print "%0.2f < z' < %0.2f meters" % (Hb, Ht)
	print "%0.2f < t < %0.2f us" % (t_array[0]*1E6, t_array[-1]*1E6)
	print "%0.2f < r < %0.2f meters" % (R(Hb), R(Ht))
	print "delta_t = %0.2f ns" % (delta_t*1E9)
	
	print "-" * 50
	print "Start time: %s" % time.strftime("%H:%M:%S", time.localtime())
	print "Iterations: %d" % t_array.shape[0]
	print "-" * 50
	
	E_es = np.zeros(t_array.shape[0])
	
	for m in xrange(t_array.shape[0]-1):
		m += 1
				
		t_int = np.arange(0, t_array[m], delta_t)
		
		integrand_t = np.zeros(t_int.shape[0])
		integrand_z = np.zeros(z_array.shape[0])
		
		for j in  xrange(z_array.shape[0]):
			A = ( 2.0*(z_array[j])**2 - D**2 ) / ( r_array[j] )**5
		
			for k in xrange(t_int.shape[0]):
				tp = t_array[k]
			
				integrand_t[k] = \
						A * I_r(z_array[j],tp,r_array[j]) * \
						np.exp(-(z_array[j]-Hb)/decay)
			
			integrand_z[j] = integrate.simps(integrand_t, t_int)
			
		E_es[m] = integrate.simps(integrand_z, z_array)
	
#~	   E_es = np.zeros(t_array.shape)
#~	   integrand = np.zeros(t_array.shape)
	
#~	   result_A	 = integrate.quad(A_integrand, Hb, Ht, limit=1000, \
#~								  epsabs=1.49E-15, epsrel=1.49E-15, \
#~								  limlst=1000, full_output=1)
#~ A = result_A[0]
								  
#~	   print ""
#~ #~	  print result_A[0]
#~ 
#~	   for j in xrange(t_array.shape[0]):
#~		   t = t_array[j]
#~		   
#~		   sum = 0
#~		   
#~		   for zp in z_array:
#~			   r = R(zp)
#~			   
#~			   
#~			   sum += (2*(zp**2)- D**2)/(r**5)*I_r(zp,t,r)*np.exp(-(zp-Hb)/decay)
#~			   
#~			   #~ result = integrate.quad(E_es_integrand, RR/c, t, \
#~ #~									  args=(zp, r, A))#, #limit=1000, \
#~ #~ #~									 epsabs=1.49E-15, epsrel=1.49E-15, \
#~ #~									  #limlst=1000, full_output=1)
#~ #~			  
#~ #~			  sum += result[0]
#~ #~			  print result[0], result[1] 
#~ 
#~									   
#~				   
#~		   integrand[j] = sum
#~	   
#~	   
#~		   for k in xrange(integrand.shape[0]-1):
#~			   k += 1
#~			   E_es[k] = integrate.simps(integrand[:k])



#~	   for j in xrange(t_array.shape[0]):
#~		   t = t_array[j]
#~ 
#~		   result_E_es = integrate.dblquad(E_es_integrand1, \
#~										   RR/c,t, # tp (tprime) limits
#~										   lambda zp:Hb, #z limits
#~										   lambda zp:Ht, \
#~										   epsabs=1.49E-15, \
#~										   epsrel=1.49E-15)
#~									
#~		   error_E_es = result_E_es[1]
#~		   E_es[j] = result_E_es[0]
		
	E_es =	(1.0/2.0/np.pi/eps0) * M * E_es
	
#~ 	E_es *= -1
	
	dE = np.gradient(E_es, delta_t)
	
	
	elapsed = time.time()-start
	print "Run time (minutes): ", elapsed/60
	
	plt.subplot(211)
	plt.plot((t_array-D/c)*1E6, E_es)
	plt.subplot(212)
	plt.plot((t_array-D/c)*1E6, dE)
	plt.show()



	
		
		
		
		
		
		
		

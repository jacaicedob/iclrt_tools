#!/usr/bin/python

"""
This program calculates and returns current waveforms to be used in any 
lightning model.

The waveforms that can be implemented are:
    1) nucci_1990:
        This waveform is described in the paper titled "Lightning Return Stroke
        Current Models With Specified Channel-Base Current: A Review
        and Comparison" by Nucci et. al. (1990)
    
    2) triangular:
        A common triangular wave.
        
All functions return a tuple containing two numpy arrays: one for the time axis, and one for the data axis.

For more information on the parameters required for each waveform, take a look
at the documentation in each function definition.
 
Sample Code is provided at the end of the source code in the __main__ method.

"""

import numpy as np
import matplotlib.pyplot as plt
import sys

def gamerota_2012_median_first(t_end, samples, type="neg"):
    """
    Returns the waveform described by Gamerota et. al. (2012) for the median
    first stroke (negative or positive).
    
    Params:
        type (string): "Negative" or "positive". Defines the type of flash.
        t_end (float): Specified the end of the interval for the waveform.
                       The waveform is specified in the interval [0, t_end]
        samples (int): Number of samples between [0, t_end]
    
    Output:
        (t_array_i, i): Tuple containing the current waveform array, i,
                        with its appropriate time array, t_array_i.
    """
    if not(isinstance(type, str)):
        err = "Error: the type parameter must be a string."
        
        return (None, None, err)
        
    type = type.lower()
    
    if "neg" in type:
    
        I0 = np.array( [3, 3, 3, 3, 20 , 15] ) * 1E3 # Amps
        n = np.array( [2, 3, 9, 11, 85, 2] )            # Unitless
        tau_1 = np.array( [4, 4, 4, 4, 4.5, 20]) * 1E-6 # Seconds
        tau_2 = np.array( [20, 20, 20, 20, 23, 240] ) * 1E-6    #Seconds
        
    elif "pos" in type:
    
        I0 = np.array( [20, 5, 6, 7] ) * 1E3 # Amps
        n = np.array( [116, 3, 2.5, 4] )            # Unitless
        tau_1 = np.array( [6, 9, 8, 6]) * 1E-6  # Seconds
        tau_2 = np.array( [50, 30, 30, 30] ) * 1E-6 #Seconds
    
    else:
        err = "Error: Unkown type. Use \"positive\" or \"negative\"."
        
        return (None, None, err)
        
     
    delta_t = float(t_end) / samples
    t_array_i = np.arange(0,t_end,delta_t)

    i = np.zeros(t_array_i.shape[0])

    for tt in xrange(i.shape[0]):
        for k in xrange(I0.shape[0]):
            eta_k = np.exp(-tau_1[k]*(n[k]*(tau_2[k]/tau_1[k]))**(1/n[k]) \
                           / tau_2[k])
                       
            i[tt] += (I0[k] * np.exp(-t_array_i[tt]/tau_2[k]) * \
                     (t_array_i[tt]/tau_1[k])**n[k]) / (eta_k * (1 + \
                     (t_array_i[tt]/tau_1[k])**n[k]))
    
    return (t_array_i, i, None)

def gamerota_2012_median_cc(t_end, samples, type="neg"):
    """
    Returns the waveform described by Gamerota et. al. (2012) for the median
    continuing current (negative or positive).
    
    Params:
        type (string): "Negative" or "positive". Defines the type of flash.
        t_end (float): Specified the end of the interval for the waveform.
                       The waveform is specified in the interval [0, t_end]
        samples (int): Number of samples between [0, t_end]
    
    Output:
        (t_array_i, i): Tuple containing the current waveform array, i,
                        with its appropriate time array, t_array_i.   
    """
    
    if not(isinstance(type, str)):
        err = "Error: the type parameter must be a string."
        
        return (None, None, err)
        
    type = type.lower()
    
    if "neg" in type:
    
        I0 = np.array( [200] ) # Amps
        n = np.array( [9] )         # Unitless
        tau_1 = np.array( [4]) * 1E-6   # Seconds
        tau_2 = np.array( [70] ) * 1E-6 #Seconds
        
    elif "pos" in type:
        I0 = np.array( [4] ) * 1E3 # Amps
        n = np.array( [9] )         # Unitless
        tau_1 = np.array( [3]) * 1E-6   # Seconds
        tau_2 = np.array( [30] ) * 1E-6 #Seconds
        
    else:
        err = "Error: Unkown type. Use \"positive\" or \"negative\"."
        
        return (None, None, err)
    
    delta_t = float(t_end) / samples
    t_array_i = np.arange(0,t_end,delta_t)
    
    i = np.zeros(t_array_i.shape[0])
    
    for tt in xrange(i.shape[0]):
        for k in xrange(I0.shape[0]):
            eta_k = np.exp(-tau_1[k]*(n[k]*(tau_2[k]/tau_1[k]))**(1/n[k]) \
                           / tau_2[k])
                           
            i[tt] += (I0[k] * np.exp(-t_array_i[tt]/tau_2[k]) * \
                     (t_array_i[tt]/tau_1[k])**n[k]) / (eta_k * (1 + \
                     (t_array_i[tt]/tau_1[k])**n[k]))
         
    return (t_array_i, i, None)

def gamerota_2012_median_subsequent(t_end, samples, type="neg"):
    """
    Returns the waveform described by Gamerota et. al. (2012) for the median
    subsequent stroke (negative or positive).
    
    Params:
        type (string): "Negative" or "positive". Defines the type of flash.
        t_end (float): Specified the end of the interval for the waveform.
                       The waveform is specified in the interval [0, t_end]
        samples (int): Number of samples between [0, t_end]
    
    Output:
        (t_array_i, i): Tuple containing the current waveform array, i,
                        with its appropriate time array, t_array_i.    
    """
    
    if not(isinstance(type, str)):
        err = "Error: the type parameter must be a string."
        
        return (None, None, err)
        
    type = type.lower()
    
    if "neg" in type:
    
        I0 = np.array( [7.5, 5] ) * 1E3 # Amps
        n = np.array( [55, 2] )         # Unitless
        tau_1 = np.array( [1.1, 1.2]) * 1E-6    # Seconds
        tau_2 = np.array( [15, 500] ) * 1E-6    #Seconds
        
    elif "pos" in type:
        err = "Error: Waveform not defined for positive subsequent strokes."

        return (None, None, err)
        
    else:
        err = "Error: Unkown type. Use \"positive\" or \"negative\"."
        
        return (None, None, err)
    
    delta_t = float(t_end) / samples
    t_array_i = np.arange(0,t_end,delta_t)
    
    i = np.zeros(t_array_i.shape[0])
    
    for tt in xrange(i.shape[0]):
        for k in xrange(I0.shape[0]):
            eta_k = np.exp(-tau_1[k]*(n[k]*(tau_2[k]/tau_1[k]))**(1/n[k]) \
                           / tau_2[k])
                           
            i[tt] += (I0[k] * np.exp(-t_array_i[tt]/tau_2[k]) * \
                     (t_array_i[tt]/tau_1[k])**n[k]) / (eta_k * (1 + \
                     (t_array_i[tt]/tau_1[k])**n[k]))
    
    return (t_array_i, i, None)
    
def jerauld_di_dt_2007(alpha, beta, Tpeak, gamma, t_end, samples):
    """
    Returns the di/dt waveform described by Jerauld (2007).
    
    Params:
        alpha (list of floats): [alpha1, alpha2] as specified in the paper
        beta (float): as described in the paper
        Tpeak (float): as described in the paper
        gamma (float): as described in the paper
        t_end (float): Specified the end of the interval for the waveform.
                       The waveform is specified in the interval [0, t_end]
        samples (int): Number of samples between [0, t_end]
    
    Output:
        (t_array_i, di): Tuple containing the current derivative waveform 
                         array, di, with its appropriate time array, t_array_i.
    """
    
    try:
        alpha1 = alpha[0]
        alpha2 = alpha[1]
        
    except TypeError as e:
        err = "Error: Input I must be a list of the form [I01, I02]"
        
        return (None, None, err)
        
    except IndexError as e:
        err = "Error: Not enough items in the list. Input alpha must be a \
               list of the form [alpha1, alpha2]"

        return (None, None, err)
        
    delta_t = float(t_end) / samples
    t_array_i = np.arange(0,t_end,delta_t)
    
    di = ( alpha1 / ( 1 + ( (t_array_i - Tpeak) / gamma )**2 ) +\
           alpha2 / ( 1 + ( (t_array_i - Tpeak) / (0.5*Tpeak) )**2 )) *\
         ( (1 + beta) / ( 1 + np.exp( (t_array_i - Tpeak - 3*gamma)/gamma) ) -\
           beta )*\
         ( 1 - 1 / ( 1 + np.exp( 4 * (t_array_i - 0.5 * Tpeak) / Tpeak ) ) )
    
    return (t_array_i, di, None)

def nucci_1990(I, tau, eta, t_end, samples):
    """
    Returns the waveform described by Nucci et. al. (1990).
    
    Params:
        I (list of floats): [I01, I02] as specified in the paper
        tau (list of floats): [tau_1, tau_2, tau_3, tau_4] as specified in 
                              the paper
        eta (float): as described in the paper
        t_end (float): Specified the end of the interval for the waveform.
                       The waveform is specified in the interval [0, t_end]
        samples (int): Number of samples between [0, t_end]
    
    Output:
        (t_array_i, i): Tuple containing the current waveform array, i,
                        with its appropriate time array, t_array_i.
    """
            
    try:
        I01 = I[0]
        I02 = I[1]
        
    except TypeError:
        err = "Error: Input I must be a list of the form [I01, I02]"
        
        return (None, None, err)
    
    except IndexError:
        err = "Error: Not enough items in the list. Input I must be a \
               list of the form [I01, I02]"

        return (None, None, err)
    
    try:
        tau_1 = tau[0]
        tau_2 = tau[1]
        tau_3 = tau[2]
        tau_4 = tau[3]
        
    except TypeError:
        err = "Error: Input tau must be a list of the form [tau_1, tau_2 \
               tau_3, tau_4]"
   
        return (None, None, err)
    
    except IndexError:
        err = "Error: Not enough items in the list. Input tau must be \
               a  list of the form [tau_1, tau_2, tau_3, tau_4]"

        return (None, None, err)
    
    delta_t = float(t_end) / samples
    t_array_i = np.arange(0,t_end,delta_t)
    
    i = (I01 * (t_array_i/tau_1)**2)/(eta * ((t_array_i/tau_1)**2 + 1)) * \
         np.exp(-t_array_i/tau_2) + I02 * (np.exp(-t_array_i/tau_3) - \
         np.exp(-t_array_i/tau_4))
    
    return (t_array_i, i, None)

def triangular(peak, peak_time, t_end, samples):
    """
    Returns a triangular wake that peaks to value "peak" at time
    "peak_time".
    
    Params:
        peak (float): The peak value of the wave
        peak_time (float) : The time at which peak occurs
        t_end (float): Specified the end of the interval for the waveform.
                       The waveform is specified in the interval [0, t_end]
        samples (int): Number of samples between [0, t_end]
                              
    Output:
        (t_array_i, i): Tuple containing the current waveform array, i,
                        with its appropriate time array, t_array_i.
    """
            
    delta_t = float(t_end) / samples
    t_array_i = np.arange(0, t_end, delta_t)
    
    peak_index = int(peak_time/delta_t)
    t_max_i = t_array_i[-1]
    
    i = np.zeros(t_array_i.shape[0])
    i[0:(peak_index+1)] = (peak/peak_time)*t_array_i[0:(peak_index+1)]
    i[(peak_index+1):] = -(peak/(t_max_i-peak_time))* \
    (t_array_i[(peak_index+1):]-t_max_i)
        
    return (t_array_i, i)        
    
def heidler(I0, tau1, tau2, n, t_end, samples):
    """
    Returns a Heidler function as defined in Heidler et al (1999).
    
    Params:
        I0 (float): The peak value of the wave
        tau1 (float): The time constant of the wave-rise-time
        tau2 (float): The time constant of the wave-decay-time
        n (integer): The wave steepness factor
        t_end (float): Specified the end of the interval for the waveform.
                       The waveform is specified in the interval [0, t_end]
        samples (int): Number of samples between [0, t_end]
                              
    Output:
        (t_array_i, i): Tuple containing the current waveform array, i,
                        with its appropriate time array, t_array_i.
        
    """
    
    delta_t = float(t_end) / samples
    t_array_i = np.arange(0, t_end, delta_t)
    
    eta = np.exp(-tau1/tau2 * (n*tau2/tau1)**(1.0/(n+1)))   
    
    i = ( I0 * (t_array_i/tau1)**n * np.exp(-t_array_i/tau2) ) / \
        ( eta * (1 + (t_array_i/tau1)**n) )
        
    return (t_array_i, i)
    
        
if __name__ == "__main__":
    # Note: The functions return None if there is an error so always test for
    # errors before using their output
    
    ### Nucci 1990
    (t_array_i, i, err) = nucci_1990(I=[9.9E3,7.5E3], tau=[0.072E-6, 5E-6, 100E-6, 6E-6], eta=0.845, t_end=100E-6, samples=100)
    
    if err:
        print(err)
        
    else:
        plt.figure("Nucci")
        plt.plot(t_array_i, i)
        plt.title("Nucci")
        plt.show()
    
    
    ### Triangular
    (t_array_i, i) = triangular(peak=1E4, peak_time=1E-6, t_end=25E-6, samples=100)
    
    plt.figure("Triangular")
    plt.plot(t_array_i, i)
    plt.title("Triangular")
    plt.show()
    
    ### Gamerota 2012
    
    # First Strokes
    (t_array_i, i, err) = gamerota_2012_median_first(type="neg", t_end=60E-6, \
                                                samples=180)
    if err:
        print(err)
        
    else:
        plt.figure("Gamerota Median First Negative")
        plt.plot(t_array_i, i)
        plt.title("Gamerota Median First Negative")
        plt.show()
    
      
    (t_array_i, i, err) = gamerota_2012_median_first(type="pos", t_end=60E-6, \
                                                samples=180)
    if err:
        print(err)
        
    else:
        plt.figure("Gamerota Median First Positive")
        plt.plot(t_array_i, i)
        plt.title("Gamerota Median First Positive")
        plt.show()
    
    
    # Subsequent Strokes
    (t_array_i, i, err) = gamerota_2012_median_subsequent(type="neg", t_end=60E-6, \
                                                     samples=180)
    
    if err:
        print(err)
        
    else:
        plt.figure("Gamerota Median Subsequent Negative")
        plt.plot(t_array_i, i)
        plt.title("Gamerota Median Subsequent Negative")
        plt.show()  
      
      
    (t_array_i, i, err) = gamerota_2012_median_subsequent(type="pos", t_end=60E-6, \
                                                     samples=180)
    
    if err:
        print(err)
        
    else:
        plt.figure("Gamerota Median Subsequent Positive")
        plt.plot(t_array_i, i)
        plt.title("Gamerota Median Subsequent Positive")
        plt.show()  

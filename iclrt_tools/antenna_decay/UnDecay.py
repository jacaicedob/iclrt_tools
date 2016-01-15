from scipy.signal import lfilter

##Written by Brian Hare in 2-06-2015
## orignal code by Terry Ngin in matlab.  His original comments:

#%UnDecay
#%
#%Written by Terry Ngin 02/10/12
#%
#%UnDecay takes E field data with a known decay constant as an input
#%and outputs the 'corrected' waveform with the decay effects removed.  
#%
#%From Jason Jerauld's PhD Thesis, (Equation 3-32) the output of a flat
#%plate antenna measuring electric field can be decomposed in the frequency
#%domain into two parts:  the real signal and the circuit response.
#%
#%This code reverses the circuit response by passing the data through a
#%filter with zeros and poles of the circuit response reversed, cancelling 
#%their IDEAL effect.  The main source of error will be in the estimation of 
#%the flat plate antenna capacitance (two plates: measurement flat plate 
#%and cloud charge sources). This capacitance may vary with weather and 
#%measurement site. The 2011 design used an estimation of 80 pF.
#%
#%
#%INPUTS
#%
#% data - E field data from any source
#%
#% decay - the expected decay constant for the antenna, in seconds
#%
#% sampleRate - the sample rate of the digitizer saving the data
#%
#%
#% WARNING: Be wary using the data for times longer than about a time constant.
#% The circuit decay being removed here is what keeps the electric field 
#% integrator stable. Without this decay, the integrator is essentially integrating 
#% everything from the beginning of time, which will eventually cause the output 
#% to saturate or do other strange things. 
#
#
#%From the Fourier domain equation in Jason Jerauld's thesis, flip the
#%numerator and denominator (flipping poles and zeros).
#%Then, use the first order approximation of the bilinear transform 
#%to go from the continuous Laplace domain (s-plane) to the sampled 
#%discrete domain (z-plane)

def UnDecay(data, decay_time, sampleRate):
    """
    For data that has decay, with a decay_time and sampleRate, remove the decay. decay_time sould be in seconds. sampleRate should be samples per second
    """
    num = [((1.0/sampleRate)/(2.0*decay_time)) + 1.0, ((1.0/sampleRate)/(2.0*decay_time)) - 1.0]
    den = [1.0, -1.0]
    return lfilter(num, den, data)

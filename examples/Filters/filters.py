import numpy as np
from scipy.signal import butter, lfilter
from matplotlib import pyplot as plt
from numpy.fft import rfft, rfftfreq

def averaging_filter(x,t,n):
    """low-pass filter by averaging over n points"""
    x= np.convolve(x, np.ones((n,))/n, mode='valid')[:-1]
    t=t[int(n/2):-int(n/2)]
    return x,t
    
def butter_lowpass(cutoff, sampling_rate, order=5):
    nyq = 0.5 * sampling_rate
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, sampling_rate, order=5):
    """ low-pass filter using a Butterworth filter """
    b, a = butter_lowpass(cutoff, sampling_rate, order=order)
    y = lfilter(b, a, data)
    return y
    
def freq_analyze(data, noise, dt):
    plt.figure()
    plt.plot(data)
    plt.title('data to analyze')
    
    plt.figure()
    plt.title('noise to analyze')
    plt.plot(noise)
    
    data_FFT=rfft(data)
    data_freqs=rfftfreq(len(data), dt)
    noise_FFT=rfft(noise)
    noise_freqs=rfftfreq(len(noise), dt)
    
    plt.figure()
    plt.plot(data_freqs, data_FFT, label='data FFT')
    plt.plot(noise_freqs, noise_FFT, label='noise FFT')
    plt.title('FFT of noise and data')
    plt.yscale('log')
    plt.show()
    

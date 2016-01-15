#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/PythonCode/')

# Import all other modules
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.fftpack import fft, ifft
import pickle

import iclrt_tools.plotting.dfplots as df


class FFT(object):
    
    def __init__(self, signal, dt, noise=None, name='Signal'):
        self.name = name
        self.signal = signal    # Signal of interest
        self.noise = noise      # Signal to extract noise
        
        self.L_sig = len(signal)  # Length of signal
        self.L_fft = self.find_fft_length(self.L_sig, 2.0)  # Length of FFT        
        
        self.dt = dt  # Time resolution
        # Signal time array
        self.time = np.arange(0, self.L_sig*self.dt, self.dt)
        
        self.fs = 1.0 / self.dt  # Signal sampling rate

        # Acquisition time in sec. The FFT length is used in this case
        # because it is greater than the signal length and the signal gets
        # zero padded in time domain, which increases the acquisition time.
        self.acq_time = self.L_fft*self.dt
        
        self.fmax = self.fs/2.0  # Maximum resolvable frequency (Nyquist freq)
        self.df = 1.0/self.acq_time  # Frequency resolution
        
        self.transform = fft(self.signal, self.L_fft)/float(self.L_fft)  # FFT

        # FFT Frequencies,not shiftable
        self.freqs = np.arange(0.0, 2.0*self.fmax, self.df)

    def find_fft_length(self, ll, offset=0.0):
        """
        Find the next power of two given a length L and returns it
        """        
        return int(2**(np.ceil(np.log2(ll)) + offset))
        
    def print_details(self):
        print('*'*50)
        print("Samples Acquired: {0:d}".format(self.L_sig))
        print("Acquisition Time: {0:0.2e} (s)".format(self.acq_time))
        print("Sampling Frequency: {0:0.2e} (Hz)".format(self.fs))
        print("Sampling Interval: {0:0.2e} (s)".format(self.dt))
        print("FFT Length: {0:d}".format(self.L_fft))
        print("Frequency Resolution: {0:0.2e} (Hz)".format(self.df))
        print("Maximum Resolvable Frequency: {0:0.2e} "
              "(Hz)".format(self.fs/2.0))
        print('*'*50)
        
    def get_noise(self, signal):
        """
        Allows the user to select the noise portion of signal and 
        returns it for further analysis
        """
        # Get the noise portion
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(signal, '.')
        ax.set_title('Select noise range and close window')
        
        p = df.plotdf(fig, ax, max_points=1E6)
        p.plot()
        plt.show()
        
        xlims = p.x_bounds
        temp_noise = signal[xlims[0]:xlims[-1]]
        l = len(temp_noise)
        
        if l < self.L_sig:
            # Make the length of the noise equal to the length of the
            # data by making copies of the noise section
            ratio = int(float(self.L_sig) / l) + 1
            
            noise = np.zeros(ratio*l)        
            
            for i in range(ratio):
                noise[i*l:(i+1)*l] = temp_noise
                
        else:
            noise = temp_noise            
            
        return noise[0:self.L_sig]

    def noise_analysis(self, bode=True, plot=True):
        """
        Finds the FFT of the noise signal and displays it together with
        the signal of interest to compare the frequency contents.
        
        Because it is noise analysis, it is more appropriate to find the
        power spectral density (PSD). PSD = abs(Xfft)**2.
        
        This is not the one sided PSD. The one-sided PSD is 2*PSD. The
        plots here show the dual-sided PSD up to the maximum resolvable
        frequency (L_fft/2)
        """
        
        if not(isinstance(self.noise, np.ndarray)):
            self.noise = self.get_noise(self.signal)
        else:
            self.noise = self.get_noise(self.noise)
        
        # Get FFT of noise
        hann = np.hanning(len(self.noise))
        X_s = fft(self.noise*hann, self.L_fft)/float(self.L_fft)
        freqs = self.freqs
        
        self.noise_fft = X_s
        self.noise_freqs = freqs
        
        if plot:
            # Plot
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(self.time*1E3,self.noise, label='Noise')
            ax.plot(self.time*1E3, self.signal, label='{}'.format(self.name))
            ax.set_ylabel('(A)')
            ax.set_xlabel('Time (ms)')
            ax.legend()
            
            p = df.plotdf(fig,ax)
            p.plot()
            
            if bode:
                psd_noise = 10*np.log10(abs(X_s)**2)
                psd_signal = 10*np.log10(abs(self.transform)**2)
                
            else:
                psd_noise = abs(X_s)**2
                psd_signal = abs(self.transform)**2
            
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(freqs[0:self.L_fft/2+1]*1E-3, psd_noise[0:self.L_fft/2+1],
                    '.', label='Noise PSD')
            ax.plot(freqs[0:self.L_fft/2+1]*1E-3, psd_signal[0:self.L_fft/2+1],
                    label='{} PSD'.format(self.name))
            ax.set_ylabel('PSD')
            ax.set_xlabel('Frequency (kHz)')
            # ax.set_yscale('log')
            ax.legend()
            
            p = df.plotdf(fig,ax)
            p.plot()
            
            plt.show()
        
    def plot_fft(self, bode=True, show=True):
        
        freqs = self.freqs
        X = self.transform
        
        if bode:
            X_mag = 20*np.log10(abs(X))
        else:
            X_mag = abs(X)
    
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(freqs, X_mag, label='{} FFT'.format(self.name))
        ax.set_ylabel('|FFT|')
        ax.set_xlabel('Frequency (Hz)')
        ax.legend()
        
        p = df.plotdf(fig,ax)
        p.plot()
        
        fig = plt.figure()
        ax = fig.add_subplot(211)
        ax.plot(self.time, self.signal, label='{}'.format(self.name))
        ax.set_ylabel('(A)')
        ax.set_xlabel('Time (s)')
        ax.legend()
        p = df.plotdf(fig,ax)
        p.plot()
        
        ax = fig.add_subplot(212)
        ax.plot(freqs, X_mag, label='{} FFT'.format(self.name))
        ax.set_ylabel('|FFT|')
        ax.set_xlabel('Frequency (Hz)')
        ax.legend()
        
        p = df.plotdf(fig,ax)
        p.plot()
        
        if show:        
            plt.show()
            
    def frequency_window(self, length=1.0):
        """
        Returns the FFT windowed by a square window of length (Hz) and
        its corresponding frequency array
        """

        # Number of indices of the window based on the frequency resolution
        n = length / self.df
        
        self.windowed_transform = self.transform[0:n+1]
        self.windowed_freqs = self.freqs[0:n+1]
        
class FFT_TransferFunction(object):
    """
    This class is used to analyze two FFT objects.
    """
    def __init__(self, fft_input, fft_output):
       self.Fi = fft_input  # FFT object for the input
       self.Fo = fft_output # FFT object for the output
       
       self.freqs = self.Fi.freqs
       self.L_fft = self.Fi.L_fft
       self.df = self.Fi.df
       
       self.tf = self.get_trasfer_function()
       
    def get_trasfer_function(self):
        return abs(self.Fo.transform)/abs(self.Fi.transform)
        
    def get_ifft(self):
        return ifft(self.tf, self.L_fft)
        
    def frequency_window(self, length=1.0):
        """
        Returns the FFT windowed by a square window of length (Hz) and
        its corresponding frequency array
        """

        # Number of indices of the window based on the frequency resolution
        n = length / self.df
        
        self.windowed_tf = self.tf[0:n+1]
        self.windowed_freqs = self.freqs[0:n+1]
        
    def plot_tf(self, windowed=False, bode=True):
        if bode:
            X_mag = 20*np.log10(abs(self.tf))
        else:
            X_mag = abs(self.tf)
                    
        fig = plt.figure()
        
        if windowed:
            if bode:
                W_mag = 20*np.log10(abs(self.windowed_tf))
            else:
                W_mag = abs(self.windowed_tf)
            
            ax1 = fig.add_subplot(211)
            ax2 = fig.add_subplot(212)
            ax2.plot(self.windowed_freqs, W_mag, label='Windowed FFT')
            ax2.legend()
            
            p = df.plotdf(fig, ax2)
            p.plot()
        else:
            ax1 = fig.add_subplot(111)
            
        ax1.plot(self.freqs, X_mag, '.', label='FFT')
        ax1.legend()
        
        p = df.plotdf(fig, ax1)
        p.plot()
        
        plt.show()


class FFT_RS_TransferFunction(object):
    """
    This class is used to analyze the transfer function of the RS Reflection
    """
    def __init__(self, fft_original, fft_reflected):
        # FFT object for the original wave (including reflection)
        self.Forig = fft_original
        # FFT object for the reflected wave (the reflection)
        self.Fref = fft_reflected
       
        self.freqs = self.Forig.freqs
        self.L_fft = self.Forig.L_fft
        self.df = self.Forig.df
       
        self.tf = self.get_trasfer_function()
       
    def get_trasfer_function(self):
        return 1.0 / (abs(self.Forig.transform)/abs(self.Fref.transform) - 1)
        
    def get_ifft(self):
        return ifft(self.tf, self.L_fft)
        
    def frequency_window(self, length=1.0):
        """
        Returns the FFT windowed by a square window of length (Hz) and
        its corresponding frequency array
        """

        # Number of indices of the window based on the frequency resolution
        n = length / self.df
        
        self.windowed_tf = self.tf[0:n+1]
        self.windowed_freqs = self.freqs[0:n+1]
        
    def plot_tf(self, windowed=False, bode=True):
        if bode:
            X_mag = 20*np.log10(abs(self.tf))
        else:
            X_mag = abs(self.tf)
                    
        fig = plt.figure()
        
        if windowed:
            if bode:
                W_mag = 20*np.log10(abs(self.windowed_tf))
            else:
                W_mag = abs(self.windowed_tf)
            
            ax1 = fig.add_subplot(211)
            ax2 = fig.add_subplot(212)
            ax2.plot(self.windowed_freqs, W_mag, label='Windowed FFT')
            ax2.legend()
            
            p = df.plotdf(fig, ax2)
            p.plot()
        else:
            ax1 = fig.add_subplot(111)
            
        ax1.plot(self.freqs, X_mag, label='FFT')
        ax1.legend()
        
        p = df.plotdf(fig, ax1)
        p.plot()
        
        plt.show()
        
if __name__ == '__main__':
    """
    Get waveform
    """
    fileName = '/home/jaime/Documents/Python Code/Models/CurrentFit/' \
               'DataFiles/UF0920_I_RS3_FFT.p'

    data = pickle.load(open(fileName, 'rb'))

    i = data['i_model']
    i_r = -0.5*data['i_r']
    ii_hi = data['ii_hi'][0:len(i)]
    t = data['time']
    dt = np.diff(t)[0]
    
    noiseFileName = '/home/jaime/Documents/Python Code/Data Sets/' \
                    'DataFiles/UF0920_data_061809_rs3.p'
    
    data = pickle.load(open(noiseFileName, 'rb'))
    noise = data['Noise']['data']
    
    I_fft = FFT(ii_hi, dt, noise=noise, name='I')
    Ir_fft = FFT(i_r, dt, name='Reflection')
    
    I_fft.noise_analysis(plot=False)
    
    L = I_fft.L_fft/2.0 + 1
    
    plt.figure()
    plt.title('PSD in dB')
    plt.plot(I_fft.freqs[0:L], 10*np.log10(abs(I_fft.transform[0:L])**2),
             label='Input')
    plt.plot(Ir_fft.freqs[0:L], 10*np.log10(abs(Ir_fft.transform[0:L])**2),
             label='Output')
    plt.plot(I_fft.noise_freqs[0:L], 10*np.log10(abs(I_fft.noise_fft[0:L])**2),
             '.', label='Noise')
    # plt.plot(I_fft.freqs, 10*np.log10(abs(I_fft.transform)**2) -
    #          10*np.log10(abs(I_fft.noise_fft)**2), '.',
    #          label='Input - Noise')
    # plt.plot([I_fft.freqs[0], I_fft.freqs[-1]], [-3,-3], 'r')
    plt.legend()

    p = df.plotdf(plt.gcf(), plt.gca(), max_points=1E5)
    p.plot()
    plt.show()
    
    sys.exit(1)
    
    # I_fft.print_details()
    # Ir_fft.print_details()
    # 
    # I_fft.plot_fft(show=False)
    # Ir_fft.plot_fft(show=False)

    tf = FFT_RS_TransferFunction(I_fft, Ir_fft)
    
    # tf.frequency_window(5.0E3)
    tf.plot_tf(bode=False)
    #
    # tx_ifft = tf.get_ifft()
    #
    # plt.figure()
    # plt.subplot(311)
    # plt.plot(tf.freqs, abs(tf.tf), label='Transfer Function FFT')
    # plt.legend()
    #
    # plt.subplot(312)
    # plt.plot(tf.windowed_freqs, abs(tf.windowed_tf),
    #          label='Transfer Function FFT (5kHz)')
    # plt.legend()
    #
    # plt.subplot(313)
    # plt.plot(tx_ifft, label='IFFT')
    #
    # p = df.plotdf(plt.gcf(), plt.gca())
    # p.plot()
    #
    # plt.legend()
    
    
    plt.show()
    
    


    #~ """
    #~ Perform FFT
    #~ """
    #~ print('delta_t: %0.1e s\nfs:      %0.1e Hz' % (delta_t, fs))
    #~ 
    #~ L = i_diff.shape[0]              # Length of signal
    #~ 
    #~ NFFT = int(2**(nextpow2(L)+2))  # Lenght of FFT
    #~ 
    #~ Y = fft(i_diff,NFFT)/L           # Normalized FFT
    #~ F = fftfreq(NFFT, delta_t)  # FFT Frequencies (array)
    #~ 
    #~ Y1 = fft(i_model[:i.shape[0]], NFFT)/L
    #~ Y2 = Y/Y1#fft(i, NFFT)/L
    #~ 
    #~ Y = fftshift(Y)
    #~ Y1 = fftshift(Y1)
    #~ Y2 = fftshift(Y2)
    #~ 
    #~ F = fftshift(F)
    #~ 
    #~ fig, ax = plt.subplots(1)
    #~ ax.plot(F,2*abs(Y2),'b', label='FFT II_HI')
    #~ # ax.plot(F,2*abs(Y1),'g', label='FFT I_model')
    #~ # ax.plot(F,2*abs(Y), 'r', label='FFT I_diff')
    #~ 
    #~ 
    #~ 
    #~ ax.set_title('Amplitude Spectrum')
    #~ ax.set_ylabel('|Y(f)|')
    #~ ax.set_xlabel('Frequency (Hz)')
    #~ plt.legend()
    #~ plt.show()
    #~ 
    #~ y = ifft(fftshift(Y)*L, NFFT) 
    #~ y1 = ifft(fftshift(Y1)*L, NFFT) 
    #~ y2 = ifft(fftshift(Y2)*L, NFFT) 
    #~ 
    #~ # plt.plot(t,abs(y[0:L]))
    #~ # plt.plot(t*1E6,i)
    #~ plt.figure()
    #~ plt.plot(t*1E6,i_diff, 'g', label='-(Original I_diff)')
    #~ plt.plot(t*1E6,y[0:L], 'r', label='IFFT I_diff')
    #~ plt.xlabel('Time ($\mu$s)')
    #~ plt.ylabel('Current (A)')
    #~ plt.title('IFFT vs Original Difference')
    #~ 
    #~ plt.legend()
    #~ 
    #~ plt.figure()
    #~ plt.plot(t*1E6,i_model[:i.shape[0]], 'g', label='Original I_model')
    #~ plt.plot(t*1E6,abs(y1[0:L]), 'r', label='IFFT I_model')
    #~ plt.xlabel('Time ($\mu$s)')
    #~ plt.ylabel('Current (A)')
    #~ plt.title('IFFT vs Original I_model')
    #~ 
    #~ plt.legend()
    #~ 
    #~ plt.figure()
    #~ plt.plot(t*1E6,i, 'g', label='Original II_HI')
    #~ plt.plot(t*1E6,abs(y2[0:L]), 'r', label='IFFT II_HI')
    #~ plt.xlabel('Time ($\mu$s)')
    #~ plt.ylabel('Current (A)')
    #~ plt.title('IFFT vs Original II_HI')
    #~ 
    #~ plt.legend()
    #~ plt.show()

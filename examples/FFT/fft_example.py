#!/usr/bin/env python

import sys
sys.path.append('/home/jaime/Documents/Python Code')

import numpy as np
import matplotlib.pyplot as plt
import pickle

import JaimePackages.plotting.dfplots as df
import JaimePackages.fourier_analysis.fourier_analysis as fourier

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

I_fft = fourier.FFT(ii_hi, dt, noise=noise, name='I')
Ir_fft = fourier.FFT(i_r, dt, name='Reflection')

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

tf = fourier.FFT_RS_TransferFunction(I_fft, Ir_fft)

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

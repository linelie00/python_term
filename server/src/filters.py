from scipy.signal import butter, filtfilt
import math

def highpass_filter(data, cutoff_frequency, sampling_frequency):
    nyquist_frequency = 0.5 * sampling_frequency
    normal_cutoff = cutoff_frequency / nyquist_frequency
    b, a = butter(1, normal_cutoff, btype='high', analog=False)
    return filtfilt(b, a, data)

def bandpass_filter(signal, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)

def calculate_rms(data):
    square_sum = sum(i**2 for i in data)
    mean = square_sum / len(data)
    return math.sqrt(mean)

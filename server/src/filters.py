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
    square_sum = sum([i**2 for i in data])
    mean = square_sum / len(data)
    return math.sqrt(mean)

def calculate_spo2(ir_data, red_data):
    ac_ir = highpass_filter(ir_data, 0.5, 50)
    dc_ir = ir_data - ac_ir
    ac_red = highpass_filter(red_data, 0.5, 50)
    dc_red = red_data - ac_red

    ir_rms = calculate_rms(bandpass_filter(ac_ir, 0.5, 5, 50))
    red_rms = calculate_rms(bandpass_filter(ac_red, 0.5, 5, 50))
    ratio = (red_rms / dc_red.mean()) / (ir_rms / dc_ir.mean())

    return max(0, min(100, 110 - 15 * ratio))

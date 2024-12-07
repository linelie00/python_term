import numpy as np
import biosppy.signals.ppg as ppg
from .filters import highpass_filter, bandpass_filter, calculate_rms

def process_ppg_data(ir_data_list, red_data_list, additional_data_list, socketio):
    try:
        print(f"Processing {len(ir_data_list)} IR data points")
        signal = np.array(ir_data_list, dtype=np.float64)
        out = ppg.ppg(signal=signal, sampling_rate=50., show=False)

        if len(out['peaks']) >= 2:
            diff = (out['peaks'][1] - out['peaks'][0]) / 50.0
            heart_rate = int(60.0 / diff)
        else:
            heart_rate = None

        spo2 = calculate_spo2(ir_data_list, red_data_list)
        response = {
            'ts': out['ts'].tolist(),
            'filtered': out['filtered'].tolist(),
            'peaks': out['peaks'].tolist(),
            'heart_rate': heart_rate,
            'spo2': spo2
        }
        socketio.emit('ppg_data', response)
        print(f"Emitted PPG data")

        for i, (ir_value, red_value) in enumerate(zip(ir_data_list, red_data_list)):
            if i == len(ir_data_list) - 1:
                additional_data_list.append((ir_value, red_value, heart_rate, spo2))
            else:
                additional_data_list.append((ir_value, red_value, None, None))

        ir_data_list.clear()
        red_data_list.clear()
    except Exception as e:
        ir_data_list.clear()
        red_data_list.clear()
        print(f"Error processing PPG data: {e}")

def calculate_spo2(ir_data, red_data):
    # SpO2 계산 로직 (filters.py 활용)
    pass

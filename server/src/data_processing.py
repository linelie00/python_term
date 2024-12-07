import numpy as np
from biosppy.signals import ppg
from src.filters import calculate_spo2

def process_ppg_data(ir_data_list, red_data_list, additional_data_list, socketio):
    try:
        signal = np.array(ir_data_list, dtype=np.float64)
        out = ppg.ppg(signal=signal, sampling_rate=50., show=False)

        heart_rate = None
        if len(out['peaks']) >= 2:
            diff = (out['peaks'][1] - out['peaks'][0]) / 50.0
            heart_rate = int(60.0 / diff)

        spo2 = int(calculate_spo2(np.array(ir_data_list), np.array(red_data_list)))

        response = {
            'ts': out['ts'].tolist(),
            'filtered': out['filtered'].tolist(),
            'peaks': out['peaks'].tolist(),
            'heart_rate': heart_rate,
            'spo2': spo2
        }
        socketio.emit('ppg_data', response)

        for ir, red in zip(ir_data_list, red_data_list):
            additional_data_list.append((ir, red, heart_rate, spo2))

        ir_data_list.clear()
        red_data_list.clear()
    except Exception as e:
        ir_data_list.clear()
        red_data_list.clear()
        print(f"Error processing PPG data: {e}")

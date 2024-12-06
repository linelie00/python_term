from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins='*')

# 서버 상태 데이터
heart_rate_data = {
    "timestamps": [],
    "filteredPPG": [],
    "ppgPeaks": [],
    "heartRate": None,
    "spo2": None
}

label_data = {
    "age": "",
    "species": "",
    "weight": "",
    "disease": ""
}

@app.route('/')
def index():
    return render_template('index.html', heart_rate_data=heart_rate_data, label_data=label_data)

@socketio.on('reset_data')
def handle_reset_data(data):
    global label_data
    label_data = data
    emit('reset_server', label_data, broadcast=True)

@socketio.on('save_data')
def handle_save_data(data):
    global heart_rate_data, label_data
    # 저장 요청 시 서버 상태 초기화
    heart_rate_data = {
        "timestamps": [],
        "filteredPPG": [],
        "ppgPeaks": [],
        "heartRate": None,
        "spo2": None
    }
    label_data = {
        "age": "",
        "species": "",
        "weight": "",
        "disease": ""
    }
    emit('save_server', {}, broadcast=True)

@socketio.on('ppg_data_request')
def send_ppg_data():
    global heart_rate_data
    # 가상의 데이터를 생성해 클라이언트로 전송 (여기서 실제 데이터로 교체 가능)
    new_timestamps = [i for i in range(len(heart_rate_data["timestamps"]), len(heart_rate_data["timestamps"]) + 10)]
    new_filtered_ppg = [random.uniform(0.5, 1.5) for _ in range(10)]
    new_peaks = [random.choice(new_timestamps) for _ in range(2)]

    heart_rate_data["timestamps"].extend(new_timestamps)
    heart_rate_data["filteredPPG"].extend(new_filtered_ppg)
    heart_rate_data["ppgPeaks"].extend(new_peaks)
    heart_rate_data["heartRate"] = random.randint(60, 100)
    heart_rate_data["spo2"] = random.randint(90, 100)

    emit('ppg_data', heart_rate_data)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000)

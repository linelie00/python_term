from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from datetime import datetime
import os

# 모듈 불러오기
from src.csv_manager import open_csv_file, close_csv_file
from src.data_processing import process_ppg_data
from src.socket_events import register_socketio_events

# Flask 및 Socket.IO 초기화
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins='*')
CORS(app)

# 데이터 저장 리스트
ir_data_list = []
red_data_list = []
additional_data_list = []

# Socket.IO 이벤트 등록
register_socketio_events(socketio, ir_data_list, red_data_list, additional_data_list)

@app.route('/ppgdata', methods=['POST'])
def receive_data():
    try:
        data = request.get_json(silent=True)
        if data and 'ir' in data and 'red' in data:
            ir_values = data['ir']
            print(ir_values)
            red_values = data['red']

            for ir_value, red_value in zip(ir_values, red_values):
                ir_data_list.append(int(ir_value))
                red_data_list.append(int(red_value))

            if len(ir_data_list) > 80:
                process_ppg_data(ir_data_list, red_data_list, additional_data_list, socketio)

        return jsonify({'message': 'Data received successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)

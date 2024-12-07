import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import threading
import socketio

# Socket.IO 클라이언트 초기화
sio = socketio.Client()

# 데이터 저장 변수
heart_rate_data = {
    'timestamps': [],
    'filteredPPG': [],
    'ppgPeaks': [],
    'heartRate': None,
    'spo2': None
}
label_data = {'name': '', 'age': ''}
error_message = ''

# Socket.IO 이벤트 처리
@sio.on('ppg_data')
def handle_ppg_data(data):
    global heart_rate_data, error_message
    # 데이터 이어서 저장
    start_time = heart_rate_data['timestamps'][-1] if heart_rate_data['timestamps'] else 0
    new_timestamps = [start_time + t for t in data['ts']]  # 이어지는 시간 계산
    heart_rate_data['timestamps'].extend(new_timestamps)
    heart_rate_data['filteredPPG'].extend(data['filtered'])
    heart_rate_data['ppgPeaks'].extend([len(heart_rate_data['timestamps']) - len(data['ts']) + p for p in data['peaks']])
    heart_rate_data['heartRate'] = data.get('heart_rate', None)
    heart_rate_data['spo2'] = data.get('spo2', None)
    error_message = ''  # 에러 메시지 초기화

# Socket.IO 연결
def start_socket():
    sio.connect('http://127.0.0.1:5000')
    print('Connected to server')

# Socket.IO 연결을 별도 스레드에서 실행
thread = threading.Thread(target=start_socket)
thread.start()

# Dash 애플리케이션 초기화
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Real-time Heart Rate Graph"),
    html.H2(id='label-display'),
    html.H2(id='heart-rate-display'),
    html.H2(id='spo2-display'),
    html.Div(id='error-message', style={'color': 'red', 'fontSize': '24px', 'fontWeight': '700'}),
    dcc.Graph(id='heart-rate-graph'),
    html.Div([
        dcc.Input(id='name', type='text', placeholder='Name', style={'margin-right': '10px'}),
        dcc.Input(id='age', type='text', placeholder='Age', style={'margin-right': '10px'}),
        html.Button('Submit', id='submit-button', n_clicks=0, style={'margin-right': '10px'})
    ], style={'margin-top': '20px'}),
    dcc.Interval(
        id='interval-component',
        interval=1000,  # 1초마다 업데이트
        n_intervals=0
    )
])

# 그래프 및 텍스트 업데이트 콜백
@app.callback(
    [Output('heart-rate-graph', 'figure'),
     Output('label-display', 'children'),
     Output('heart-rate-display', 'children'),
     Output('spo2-display', 'children'),
     Output('error-message', 'children'),
     Output('name', 'value'),
     Output('age', 'value')],
    [Input('interval-component', 'n_intervals'),
     Input('submit-button', 'n_clicks'),
     Input('name', 'value'),
     Input('age', 'value')],
    prevent_initial_call=True
)
def update_graph(n_intervals, submit_clicks, name, age):
    global label_data, heart_rate_data, error_message

    # Submit 버튼 클릭 처리
    if submit_clicks > 0:
        if name and age:
            label_data = {'name': name, 'age': age}
            sio.emit('save_data', label_data)
            error_message = ''

        # Submit 이후 입력 필드 초기화
        return (go.Figure(),
                f"Name: {label_data['name']} / Age: {label_data['age']}",
                f"Heart Rate: {heart_rate_data['heartRate'] or 'N/A'} bpm",
                f"SpO2: {heart_rate_data['spo2'] or 'N/A'}%",
                error_message,
                '',  # Name 필드 초기화
                '')  # Age 필드 초기화

    # 그래프 생성
    figure = go.Figure()

    # 이어지는 데이터를 사용하여 그래프 생성
    figure.add_trace(go.Scatter(
        x=heart_rate_data['timestamps'],
        y=heart_rate_data['filteredPPG'],
        mode='lines',
        name='Filtered PPG'
    ))

    # 피크 데이터를 점으로 추가
    scatter_data = [
        {'x': heart_rate_data['timestamps'][i], 'y': heart_rate_data['filteredPPG'][i]}
        for i in heart_rate_data['ppgPeaks']
    ]
    figure.add_trace(go.Scatter(
        x=[point['x'] for point in scatter_data],
        y=[point['y'] for point in scatter_data],
        mode='markers',
        name='PPG Peaks'
    ))

    # 실시간 상태 표시
    heart_rate_text = f"Heart Rate: {heart_rate_data['heartRate'] or 'N/A'} bpm"
    spo2_text = f"SpO2: {heart_rate_data['spo2'] or 'N/A'}%"
    label_text = f"Name: {label_data['name']} / Age: {label_data['age']}"

    return figure, label_text, heart_rate_text, spo2_text, error_message, name, age


if __name__ == '__main__':
    app.run_server(port=3000, debug=True)

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
    start_time = heart_rate_data['timestamps'][-1] + 1 if heart_rate_data['timestamps'] else 0
    new_timestamps = [start_time + t for t in range(len(data['ts']))]
    heart_rate_data['timestamps'].extend(new_timestamps)
    heart_rate_data['filteredPPG'].extend(data['filtered'])
    heart_rate_data['ppgPeaks'].extend([new_timestamps[p] for p in data['peaks']])
    heart_rate_data['heartRate'] = data.get('heart_rate', None)
    heart_rate_data['spo2'] = data.get('spo2', None)
    error_message = ''

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
    html.H1("Real-time Heart Rate Monitor", style={'textAlign': 'center'}),
    html.Div([
        html.Label("Name:", style={'margin-right': '10px', 'fontWeight': 'bold', 'fontSize': '18px'}),
        dcc.Input(id='name', type='text', placeholder='Enter Name', style={
            'border': 'none',
            'borderBottom': '1px solid black',
            'width': '150px',
            'margin-right': '20px',
            'fontSize': '18px'
        }),
        html.Label("Age:", style={'margin-right': '10px', 'fontWeight': 'bold', 'fontSize': '18px'}),
        dcc.Input(id='age', type='text', placeholder='Enter Age', style={
            'border': 'none',
            'borderBottom': '1px solid black',
            'width': '100px',
            'fontSize': '18px'
        })
    ], style={'textAlign': 'center', 'margin-bottom': '20px'}),
    html.H2(id='heart-rate-display', style={'textAlign': 'center', 'fontSize': '18px'}),
    html.H2(id='spo2-display', style={'textAlign': 'center', 'fontSize': '18px'}),
    html.Div(id='error-message', style={'color': 'red', 'fontSize': '24px', 'fontWeight': '700', 'textAlign': 'center'}),
    dcc.Graph(
        id='heart-rate-graph',
        config={'scrollZoom': True},  # 스크롤 줌 활성화
        style={'margin': '0 auto', 'width': '80%'}
    ),
    html.Div([
        html.Button('Submit', id='submit-button', n_clicks=0, style={
            'fontSize': '20px',
            'padding': '10px 20px',
            'textAlign': 'center',
            'display': 'block',
            'margin': '20px auto'
        })
    ]),
    dcc.Interval(
        id='interval-component',
        interval=1000,  # 1초마다 업데이트
        n_intervals=0
    )
])

# 그래프 및 텍스트 업데이트 콜백
@app.callback(
    [Output('heart-rate-graph', 'figure'),
     Output('heart-rate-display', 'children'),
     Output('spo2-display', 'children'),
     Output('error-message', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('submit-button', 'n_clicks')],
    [State('name', 'value'),
     State('age', 'value')]
)
def update_graph(n_intervals, submit_clicks, name, age):
    global label_data, heart_rate_data, error_message

    # Submit 버튼 클릭 처리
    if submit_clicks > 0 and name and age:
        label_data = {'name': name, 'age': age}
        sio.emit('save_data', label_data)
        error_message = ''

    # 최근 200개의 데이터만 그래프에 표시
    num_recent_points = 200
    x_data = heart_rate_data['timestamps'][-num_recent_points:]
    y_data = heart_rate_data['filteredPPG'][-num_recent_points:]
    peaks = [
        {'x': heart_rate_data['timestamps'][i], 'y': heart_rate_data['filteredPPG'][i]}
        for i in range(len(heart_rate_data['timestamps']) - num_recent_points, len(heart_rate_data['timestamps']))
        if i in heart_rate_data['ppgPeaks']
    ]

    # 그래프 생성
    figure = go.Figure()
    figure.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        mode='lines',
        name='Filtered PPG'
    ))

    if peaks:
        figure.add_trace(go.Scatter(
            x=[point['x'] for point in peaks],
            y=[point['y'] for point in peaks],
            mode='markers',
            name='PPG Peaks'
        ))

    # x축 범위를 최근 데이터로 업데이트
    figure.update_layout(
        xaxis=dict(
            range=[x_data[0], x_data[-1]] if x_data else [0, 1]
        )
    )

    # 상태 텍스트
    heart_rate_text = f"Heart Rate: {heart_rate_data['heartRate'] or 'N/A'} bpm"
    spo2_text = f"SpO2: {heart_rate_data['spo2'] or 'N/A'}%"

    return figure, heart_rate_text, spo2_text, error_message

if __name__ == '__main__':
    app.run_server(port=3000, debug=True)

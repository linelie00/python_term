from flask_socketio import emit

def register_socket_events(socketio, ir_data_list, red_data_list, additional_data_list):
    @socketio.on('reset_data')
    def handle_reset_data(data):
        socketio.emit('reset_server', data)

    @socketio.on('save_data')
    def handle_save_data(data):
        socketio.emit('save_server', data)
        # Reset data or save logic
        ir_data_list.clear()
        red_data_list.clear()
        additional_data_list.clear()

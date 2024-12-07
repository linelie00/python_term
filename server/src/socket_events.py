from src.csv_manager import open_csv_file, close_csv_file

def register_socketio_events(socketio, ir_data_list, red_data_list, additional_data_list):
    @socketio.on('reset_data')
    def handle_reset_data(data):
        socketio.emit('reset_server', data)

    @socketio.on('save_data')
    def handle_save_data(data):
        name = data.get('name', 'unknown')
        age = data.get('age', 'unknown')
        label = f"{name}_{age}"
        close_csv_file()
        if additional_data_list:
            open_csv_file(label)
            csv_writer.writerows(additional_data_list)
            close_csv_file()
        additional_data_list.clear()

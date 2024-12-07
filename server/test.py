import pandas as pd
import requests
import time

# CSV 파일 경로
CSV_FILE_PATH = './csv/data/12_12112_12_12_240717-16-58.csv'

# 서버 URL
SERVER_URL = 'http://127.0.0.1:5000/ppgdata'

# 데이터를 읽고 200개씩 나누는 함수
def read_and_send_data(csv_file_path, server_url):
    try:
        # CSV 파일 읽기
        data = pd.read_csv(csv_file_path)

        # 'IR Value'와 'Red Value' 열 확인
        if 'IR Value' not in data.columns or 'Red Value' not in data.columns:
            raise ValueError("CSV 파일에 'IR Value' 또는 'Red Value' 열이 없습니다.")

        # 데이터를 200개씩 나누기
        ir_values = data['IR Value'].tolist()
        red_values = data['Red Value'].tolist()

        for i in range(0, len(ir_values), 200):
            ir_chunk = ir_values[i:i + 200]
            red_chunk = red_values[i:i + 200]

            # JSON 데이터 생성
            json_data = {
                "ir": ir_chunk,
                "red": red_chunk
            }

            # HTTP POST 요청 보내기
            response = requests.post(server_url, json=json_data)

            # 응답 처리
            if response.status_code == 200:
                print(f"Successfully sent chunk {i // 200 + 1}: {response.json()}")
            else:
                print(f"Failed to send chunk {i // 200 + 1}: {response.status_code}, {response.text}")

            # 2초 대기
            time.sleep(2)

    except Exception as e:
        print(f"Error occurred: {e}")

# 실행
if __name__ == '__main__':
    read_and_send_data(CSV_FILE_PATH, SERVER_URL)

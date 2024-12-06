import csv
import os
from datetime import datetime

csv_file = None
csv_writer = None

def open_csv_file(label):
    global csv_file, csv_writer
    timestamp = datetime.now().strftime('%y%m%d-%H-%M')
    filename = f'csv/{label}_{timestamp}.csv'

    if not os.path.exists('csv'):
        os.makedirs('csv')

    csv_file = open(filename, mode='a', newline='')
    csv_writer = csv.writer(csv_file)

    if os.path.getsize(filename) == 0:
        csv_writer.writerow(['IR Value', 'Red Value', 'Heart Rate', 'SpO2'])

    print(f"Opened CSV file: {filename}")

def close_csv_file():
    global csv_file
    if csv_file:
        csv_file.close()
        csv_file = None
        print("Closed CSV file")

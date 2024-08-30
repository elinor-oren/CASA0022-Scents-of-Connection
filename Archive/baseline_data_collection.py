import serial
import os
import pandas as pd
from datetime import datetime
import time

# Configuration for each headset
headsets = {
    'headset1': {'name': 'headset1', 'port': '/dev/cu.usbserial-110', 'baudrate': 9600, 'participant': 6, 'headset': 1},
    'headset2': {'name': 'headset2', 'port': '/dev/cu.usbserial-10', 'baudrate': 9600, 'participant': 6, 'headset': 2}
}

# Column names based on the data order
columns = ['timestamp','signal_strength', 'attention', 'meditation', 'delta', 'theta', 'low_alpha',
           'high_alpha', 'low_beta', 'high_beta', 'low_gamma', 'high_gamma']

# Initialize serial connection
def setup_serial_connection(name, port, baudrate):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        return ser, name
    except Exception as e:
        print(f"Failed to connect on {port}: {str(e)}")
        return None, name
    
# Save data to CSV file
def save_data_to_csv(data, participant, headset):
    directory = '/Users/elinor/Documents/GitHub/CASA0022-dissertation/data' # Specify the directory where files should be saved
    if not os.path.exists(directory):
        os.makedirs(directory)  # Create the directory if it does not exist
    
    df = pd.DataFrame([data], columns=columns)
    # Define the filename with participant, headset, and date
    filename = f'data_participant_{participant}_headset_{headset}_{datetime.now().strftime("%Y%m%d")}.csv'
    full_path = os.path.join(directory, filename)  # Construct the full file path
    df.to_csv(full_path, mode='a', header=not os.path.exists(full_path), index=False)

def read_and_process_data(ser, participant, headset):
    """ Read data from serial and save to CSV """
    if ser:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line:
                data = list(map(int, line.split(',')))
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Timestamp to millisecond precision
                data.insert(0, timestamp)
                save_data_to_csv(data, participant, headset)
        except Exception as e:
            print(f"Error reading data: {str(e)}")

def collect_baseline_data(duration_minutes=7):
    # Setup connections
    connections = {key: setup_serial_connection(config['name'], config['port'], config['baudrate'])
                   for key, config in headsets.items()}
    
    start_time = time.time()
    end_time = start_time + duration_minutes * 60
    
    try:
        while time.time() < end_time:
            for key, (ser, name) in connections.items():
                if ser:
                    config = headsets[name]
                    read_and_process_data(ser, config['participant'], config['headset'])
    except KeyboardInterrupt:
        print("Stopping data collection.")
    finally:
        for ser, _ in connections.values():
            if ser:
                ser.close()

if __name__ == '__main__':
    collect_baseline_data(duration_minutes=7)  # Set the desired duration here

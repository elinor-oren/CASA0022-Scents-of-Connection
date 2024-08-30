import serial
import os 
import pandas as pd
from datetime import datetime

# Configuration for each headset
headsets = {
    'headset1': {'port': '/dev/cu.usbserial-10', 'baudrate': 9600, 'participant': 1, 'headset': 1},
    'headset2': {'port': '/dev/cu.usbserial-110', 'baudrate': 9600, 'participant': 2, 'headset': 2}
}

# Column names based on the data order
columns = ['signal_strength', 'attention', 'meditation', 'delta', 'theta', 'low_alpha',
           'high_alpha', 'low_beta', 'high_beta', 'low_gamma', 'high_gamma']

# Initialize serial connection
def setup_serial_connection(port, baudrate):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        return ser
    except Exception as e:
        print(f"Failed to connect on {port}: {str(e)}")
        return None
    
# Save data to CSV file 
import os

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
                save_data_to_csv(data, participant, headset)
        except Exception as e:
            print(f"Error reading data: {str(e)}")

def main():
    # Setup connections
    connections = {key: setup_serial_connection(port=config['port'], baudrate=config['baudrate'])
                   for key, config in headsets.items()}
    
    try:
        while True:
            for key, ser in connections.items():
                config = headsets[key]
                read_and_process_data(ser, config['participant'], config['headset'])
    except KeyboardInterrupt:
        print("Stopping data collection.")


if __name__ == '__main__':
    main()

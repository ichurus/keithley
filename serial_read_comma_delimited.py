import serial
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


class SerialInterface:
    def __init__(self, port='COM2', baudrate=9600, timeout=2):
        """
        Initialize the serial connection.
        """
        self.echo = False
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None

    def open_connection(self):
        """Open the serial connection."""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            if self.serial_connection.is_open:
                print(f"Connection to {self.port} opened successfully.")
        except serial.SerialException as e:
            print(f"Error opening connection: {e}")

    def close_connection(self):
        """Close the serial connection."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            if self.echo:
                print(f"Connection to {self.port} closed.")

    def send_data(self, data):
        """Send data over the serial connection."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write(data.encode())
            if self.echo:
                print(f"Sent data: {data}")

    def read_data(self):
        """Read data from the serial connection."""
        if self.serial_connection and self.serial_connection.is_open:
            data = b""
            while True:
                line = self.serial_connection.readline()
                if not line:
                    break
                data += line
            if self.echo:
                print(f"Received data: {data}")
            return data
        return None

    def scan(self, start_voltage=0, stop_voltage=600, steps=20, filename='scan_result_VA.csv'):
        data = np.zeros([steps, 2])
        self.send_data(":SOUR:FUNC VOLT\r\n")
        self.send_data(":OUTP ON\r\n")

        for ip, p in enumerate(np.linspace(start_voltage, stop_voltage, steps)):
            self.send_data(f":SOUR:VOLT {p}\r\n")
            self.send_data(":MEAS:CURR?\r\n")
            response = self.read_data()

            values = response.decode('utf-8').strip().split(',')
            array = np.array(values, dtype=float)
            print(f"{array[0]}V, {array[1]}A")
            data[ip, 0] = array[0]
            data[ip, 1] = array[1]
            time.sleep(0.1)

        self.send_data(":SOUR:VOLT 0\r\n")
        self.send_data(":OUTP OFF\r\n")

        # Save as comma-delimited CSV using pandas
        df = pd.DataFrame(data, columns=["Voltage (V)", "Current (A)"])
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        result_filename = f"{filename}_{current_datetime}.csv"
        df.to_csv(result_filename, index=False)

        return data


if __name__ == "__main__":
    interface = SerialInterface(port='COM4', baudrate=9600, timeout=1)
    interface.open_connection()
    time.sleep(1)  # Wait for the connection to stabilize

    sample_name = "pad2 to pad7"
    data = interface.scan(start_voltage=-0.001, stop_voltage=0.001, steps=5, filename='scan_result_VA')

    plt.figure()
    plt.plot(data[:, 0] * 1e3, data[:, 1] * 1e6, color='red')
    plt.xlabel("Voltage (mV)")
    plt.ylabel("Current (uA)")
    plt.title(sample_name)
    plt.savefig(f"{sample_name}.png", dpi=300, format='png')
    plt.show()

    interface.close_connection()

import serial
import time

# Adjust this to match the COM port used by your u-blox GPS
PORT = 'COM4'
BAUD_RATE = 9600  # Baud rate for the u-blox GPS

def read_gps_data(port):
    with serial.Serial(port, BAUD_RATE, timeout=1) as ser:
        while True:
            try:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if line:
                    print(line)
            except serial.SerialException:
                print("Error reading from the serial port.")
                break
            except KeyboardInterrupt:
                print("Stopped by user.")
                break
            time.sleep(0.5)  # Reduce CPU usage by sleeping between reads

if __name__ == "__main__":
    print(f"Starting to read GPS data from {PORT}")
    read_gps_data(PORT)

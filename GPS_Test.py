import serial
import pytz
from datetime import datetime

def convert_to_decimal(degrees, minutes, direction):
    """
    Convert latitude and longitude from degrees and minutes to decimal format.
    Adjusts for hemisphere and formats to six decimal places.
    """
    decimal_degrees = degrees + minutes / 60
    if direction in ['S', 'W']:  # Convert southern and western hemispheres to negative
        decimal_degrees = -decimal_degrees
    return f"{decimal_degrees:.6f}"

def parse_utc_time_from_gprmc(time_str, date_str):
    """
    Parses the UTC time and date from a GPRMC sentence and converts it to a datetime object.
    """
    hours = int(time_str[0:2])
    minutes = int(time_str[2:4])
    seconds = int(time_str[4:6])
    day = int(date_str[0:2])
    month = int(date_str[2:4])
    year = int(date_str[4:6]) + 2000  # Convert YY to YYYY
    utc_datetime = datetime(year, month, day, hours, minutes, seconds, tzinfo=pytz.utc)
    timezone = pytz.timezone('America/New_York')  # Convert to Eastern Time
    local_datetime = utc_datetime.astimezone(timezone)
    return local_datetime.strftime("%m:%d:%Y %I:%M:%S %p %Z")

def process_gps_data(data, gps_data):
    """
    Processes raw GPS NMEA sentences to extract and store relevant GPS data.
    """
    if data.startswith('$GPGGA'):
        parts = data.split(',')
        if parts[6] != '0':  # Ensure there is a valid GPS fix
            gps_data['latitude'] = convert_to_decimal(int(float(parts[2]) / 100), float(parts[2]) % 100, parts[3])
            gps_data['longitude'] = convert_to_decimal(int(float(parts[4]) / 100), float(parts[4]) % 100, parts[5])
            gps_data['altitude'] = f"{float(parts[9]) * 3.28084:.2f} ft"
    elif data.startswith('$GPRMC'):
        parts = data.split(',')
        if parts[2] == 'A':  # Check for 'A' to ensure the data is active and valid
            gps_data['timestamp'] = parse_utc_time_from_gprmc(parts[1], parts[9])

ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
gps_data = {}

try:
    with open("gps_data.txt", "a") as file:
        print("GPS Logger is running. Press CTRL+C to stop.")
        while True:
            data = ser.readline().decode('ascii', errors='replace').strip()
            process_gps_data(data, gps_data)
            if 'timestamp' in gps_data and 'latitude' in gps_data and 'longitude' in gps_data:
                log_entry = f"{gps_data['timestamp']} - Latitude: {gps_data['latitude']}, Longitude: {gps_data['longitude']}, Altitude: {gps_data.get('altitude', 'N/A')}\n"
                file.write(log_entry)
                file.flush()
                print("Data logged")
                gps_data.clear()  # Clear data after logging to ensure each log is fresh
except KeyboardInterrupt:
    print("GPS Logger stopped by user.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    ser.close()
    print("Serial connection closed.")

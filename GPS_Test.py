import csv
import serial
import pytz
from datetime import datetime

def convert_to_decimal(degrees, minutes, direction):
    """Convert latitude and longitude from degrees and minutes to decimal format."""
    decimal_degrees = degrees + minutes / 60
    if direction in ['S', 'W']:
        decimal_degrees = -decimal_degrees
    return f"{decimal_degrees:.6f}"

def parse_utc_time_from_gprmc(time_str, date_str):
    """Parse UTC time and date from GPRMC sentence and convert to local time."""
    hours = int(time_str[:2])
    minutes = int(time_str[2:4])
    seconds = int(time_str[4:6])
    day = int(date_str[:2])
    month = int(date_str[2:4])
    year = int(date_str[4:6]) + 2000
    utc_datetime = datetime(year, month, day, hours, minutes, seconds, tzinfo=pytz.utc)
    local_datetime = utc_datetime.astimezone(pytz.timezone('America/New_York'))
    return local_datetime.strftime("%m:%d:%Y %I:%M:%S %p %Z")

def process_gps_data(data, gps_data):
    """Process raw GPS NMEA sentences and extract relevant information."""
    if not data.startswith(('$GPGGA', '$GPRMC')):
        return  # Ignore unsupported sentences
    
    parts = data.split(',')
    if data.startswith('$GPGGA') and len(parts) > 9:
        if parts[6] != '0':  # Valid GPS fix
            try:
                degrees_lat = int(float(parts[2]) / 100)
                minutes_lat = float(parts[2]) % 100
                degrees_lon = int(float(parts[4]) / 100)
                minutes_lon = float(parts[4]) % 100
                gps_data['latitude'] = convert_to_decimal(degrees_lat, minutes_lat, parts[3])
                gps_data['longitude'] = convert_to_decimal(degrees_lon, minutes_lon, parts[5])
                gps_data['altitude'] = f"{float(parts[9]) * 3.28084:.2f} ft"
            except ValueError:
                pass  # Handle parsing errors silently
    elif data.startswith('$GPRMC') and len(parts) > 9:
        if parts[2] == 'A':  # Active data
            gps_data['timestamp'] = parse_utc_time_from_gprmc(parts[1], parts[9])

def log_gps_data_to_csv(gps_data):
    """Log GPS data to a CSV file."""
    with open("gps_data.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        # Write the header if the file is empty
        if file.tell() == 0:
            writer.writerow(["timestamp", "latitude", "longitude", "altitude"])
        writer.writerow([
            gps_data["timestamp"],
            gps_data["latitude"],
            gps_data["longitude"],
            gps_data.get("altitude", "N/A")
        ])
    print("Data logged to CSV")

# GPS data processing loop
ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
gps_data = {}

try:
    while True:
        data = ser.readline().decode('ascii', errors='replace').strip()
        process_gps_data(data, gps_data)
        if 'timestamp' in gps_data and 'latitude' in gps_data and 'longitude' in gps_data:
            log_gps_data_to_csv(gps_data)
            gps_data.clear()
except KeyboardInterrupt:
    print("GPS Logger stopped by user.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    ser.close()
    print("Serial connection closed.")

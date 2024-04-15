import serial# Import serial library
from datetime import datetime, timedelta # Import datetime library

def convert_to_decimal(degrees, minutes, direction):
    """
    Convert latitude and longitude from degrees and minutes to decimal format.
    This adjusts for hemisphere and formats to six decimal places.
    """
    decimal_degrees = degrees + minutes / 60
    if direction in ['S', 'W']:  # Convert southern and western hemispheres to negative
        decimal_degrees = -decimal_degrees
    formatted_decimal = f"{decimal_degrees:.6f}"
    print(f"Converted to Decimal Degrees: {formatted_decimal}")  # Debugging output
    return formatted_decimal

def parse_date_from_gprmc(data):
    """
    Extract and format the date from a $GPRMC sentence.
    """
    parts = data.split(',')
    if parts[0] == '$GPRMC' and parts[2] == 'A':  # Ensure valid and active data
        day = parts[9][:2]
        month = parts[9][2:4]
        year = '20' + parts[9][4:6]  # Adjust for Y2K (Assumes 2000s)
        formatted_date = f"{month}:{day}:{year}"
        print(f"Formatted Date from GPRMC: {formatted_date}")  # Debugging output
        return formatted_date
    print("GPRMC sentence not valid or active for date parsing.")  # Debugging output
    return None

def parse_gps(data, current_date):
    """
    Parse GPS data received from the NMEA sentences.
    """
    parsed_data = {}
    if data.startswith('$GPGGA'):
        parts = data.split(',')
        if parts[6] != '0':
            latitude_deg = int(float(parts[2]) / 100)
            latitude_min = float(parts[2]) % 100
            latitude = convert_to_decimal(latitude_deg, latitude_min, parts[3])
            
            longitude_deg = int(float(parts[4]) / 100)
            longitude_min = float(parts[4]) % 100
            longitude = convert_to_decimal(longitude_deg, longitude_min, parts[5])
            
            altitude_meters = float(parts[9])
            altitude_feet = altitude_meters * 3.28084
            altitude = f"{altitude_feet:.2f} ft"
            
            parsed_data['date'] = current_date if current_date else "Date not set"
            parsed_data['coordinates'] = f"Latitude: {latitude}, Longitude: {longitude}"
            parsed_data['altitude'] = f"Altitude: {altitude}"
            print(f"Parsed GPS Data: {parsed_data}")  # Debugging output
        else:
            print("No valid GPS fix available.")  # Debugging output
    return parsed_data

ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
current_date = None  # To hold the current date parsed from $GPRMC

try:
    with open("gps_data.txt", "a") as file:
        print("GPS Logger is running. Press CTRL+C to stop.")
        while True:
            data = ser.readline().decode('ascii', errors='replace').strip()
            print(f"Received raw data: {data}")  # Debugging output
            if data.startswith('$GPRMC'):
                current_date = parse_date_from_gprmc(data)
            if data:
                parsed_data = parse_gps(data, current_date)
                if parsed_data:
                    file.write(f"{parsed_data['date']} - {parsed_data['coordinates']}, {parsed_data['altitude']}\n")
                    file.flush()
                    print(f"Logged data at {parsed_data['date']}")  # Debugging output
            else:
                print("No data received. Waiting for signal...")  # Debugging output
except KeyboardInterrupt:
    print("GPS Logger stopped by user.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    ser.close()
    print("Serial connection closed.")

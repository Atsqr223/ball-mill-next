# eventual sensor ids:
# tcsri
# 1 - Radar
# 2 - Accelerometer
# 3 - LD
# 4 - Microphone
#iitkgp
# 5 - Radar
# 6 - Accelerometer
# 7 - LD
# 8 - Microphone
#tata_steel
# 9 - Radar
# 10 - Accelerometer
# 11 - LD
# 12 - Microphone

# location ids:
# 1 - TCSRI
# 2 - IITKGP
# 3 - Tata Steel

# sensor types:
# RADAR
# ACCELEROMETER
# LD
# MICROPHONE

# operating command:
# python scripts/upload_sensor_data.py <file_path> <location_id> <sensor_id> <sensor_type>

import os
import csv
import psycopg2
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database connection string from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')

def process_sensor_data(file_path, sensor_type):
    """Process sensor data based on sensor type and return formatted data."""
    data = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        # Skip header row
        next(reader)
        
        for row in reader:
            try:
                if sensor_type == 'LD':
                    # LD sensor data has voltage (to be stored as distance) and sample_index
                    sample_index = int(row[1])
                    # Assuming 1000 Hz sampling rate for LD sensor
                    time_from_start = sample_index / 1000.0
                    data.append({
                        'distance': float(row[0]),  # Store voltage as distance
                        'timestamp': None,
                        'metadata': json.dumps({
                            'sample_index': sample_index,
                            'time_from_start': time_from_start,
                            'unit': 'seconds'
                        })
                    })
                elif sensor_type == 'ACCELEROMETER':
                    # Accelerometer data has time, x, y, z values
                    data.append({
                        'acceleration_x': float(row[1]),
                        'acceleration_y': float(row[2]),
                        'acceleration_z': float(row[3]),
                        'timestamp': None,  # We'll use the actual time value
                        'metadata': json.dumps({
                            'time_from_start': float(row[0]),  # Store original time value
                            'unit': 'seconds'
                        })
                    })
                elif sensor_type == 'RADAR':
                    # Radar data has time and voltage (to be stored as radar)
                    data.append({
                        'radar': float(row[1]),  # Store voltage in radar field
                        'timestamp': None,  # We'll use the actual time value
                        'metadata': json.dumps({
                            'time_from_start': float(row[0]),  # Store original time value
                            'unit': 'seconds'
                        })
                    })
            except (ValueError, IndexError) as e:
                print(f"Warning: Skipping row due to error: {str(e)}")
                continue
                
    if not data:
        raise ValueError("No valid data points found in the file")
        
    return data

def upload_data_to_postgres(file_path, location_id, sensor_id, sensor_type, session_id=None):
    conn = None
    cursor = None
    try:
        # Process the data based on sensor type
        sensor_data = process_sensor_data(file_path, sensor_type)
        
        print(f"Processing {len(sensor_data)} data points...")
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Get start time for the data points
        start_time = datetime.now()
        
        # Insert sensor data
        for reading in sensor_data:
            # Calculate actual timestamp using time from start
            time_from_start = json.loads(reading['metadata'])['time_from_start']
            actual_timestamp = start_time + timedelta(seconds=time_from_start)
            
            # Base values that are common for all sensor types
            values = [
                sensor_id,   # sensor_id
                actual_timestamp,     # timestamp
                reading['metadata'],      # metadata
            ]
            
            # Add session_id if provided
            if session_id is not None:
                values.insert(0, session_id)  # acquisition_session_id
            
            # Add sensor-specific values
            # Construct the SQL query based on sensor type and session presence
            if sensor_type == 'LD':
                fields = ['sensor_id', 'timestamp', 'metadata', 'distance']
                if session_id is not None:
                    fields.insert(0, 'acquisition_session_id')
                cursor.execute(
                    f"""
                    INSERT INTO sensor_data 
                    ({', '.join(fields)})
                    VALUES ({', '.join(['%s'] * len(fields))})
                    """,
                    values + [reading['distance']]
                )
            elif sensor_type == 'ACCELEROMETER':
                fields = ['sensor_id', 'timestamp', 'metadata', 
                         'acceleration_x', 'acceleration_y', 'acceleration_z']
                if session_id is not None:
                    fields.insert(0, 'acquisition_session_id')
                cursor.execute(
                    f"""
                    INSERT INTO sensor_data 
                    ({', '.join(fields)})
                    VALUES ({', '.join(['%s'] * len(fields))})
                    """,
                    values + [
                        reading['acceleration_x'],
                        reading['acceleration_y'],
                        reading['acceleration_z']
                    ]
                )
            elif sensor_type == 'RADAR':
                fields = ['sensor_id', 'timestamp', 'metadata', 'radar']
                if session_id is not None:
                    fields.insert(0, 'acquisition_session_id')
                cursor.execute(
                    f"""
                    INSERT INTO sensor_data 
                    ({', '.join(fields)})
                    VALUES ({', '.join(['%s'] * len(fields))})
                    """,
                    values + [reading['radar']]
                )
            
            # Update session end time if we're using a session
            if session_id is not None:
                cursor.execute(
                    """
                    UPDATE acquisition_sessions 
                    SET end_time = NOW()
                    WHERE id = %s
                    """,
                    (session_id,)
                )
        
        # Commit the transaction
        conn.commit()
        print(f"Successfully uploaded {len(sensor_data)} data points")
        
    except Exception as e:
        print(f"Error uploading data: {str(e)}")
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload sensor data to PostgreSQL')
    parser.add_argument('file_path', help='Path to the sensor data file')
    parser.add_argument('location_id', type=int, help='Location ID')
    parser.add_argument('sensor_id', type=int, help='Sensor ID')
    parser.add_argument('sensor_type', choices=['LD', 'ACCELEROMETER', 'RADAR'],
                        help='Type of sensor')
    parser.add_argument('--session_id', type=int, help='Existing session ID to append data to')
    
    args = parser.parse_args()
    
    try:
        print(f"Reading data from {args.file_path}...")
        upload_data_to_postgres(
            args.file_path,
            args.location_id,
            args.sensor_id,
            args.sensor_type,
            args.session_id
        )
        print("Data upload completed successfully")
    except Exception as e:
        print(f"Failed to upload data: {str(e)}")
        exit(1)

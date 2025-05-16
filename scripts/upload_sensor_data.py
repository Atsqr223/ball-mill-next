import os
import csv
import psycopg2
import json
from datetime import datetime
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
        
        for i, row in enumerate(reader):
            try:
                timestamp = datetime.now().isoformat()
                if sensor_type == 'LD':
                    # LD sensor data has one voltage value per row
                    data.append({
                        'sample_index': i,
                        'voltage': float(row[0]),
                        'timestamp': timestamp,
                    })
                elif sensor_type == 'ACCELEROMETER':
                    # Accelerometer data has x, y, z values
                    if len(row) >= 3:
                        x, y, z = map(float, row[:3])
                        data.append({
                            'sample_index': i,
                            'acceleration_x': x,
                            'acceleration_y': y,
                            'acceleration_z': z,
                            'timestamp': timestamp,
                        })
                elif sensor_type == 'RADAR':
                    # Radar data has distance value
                    data.append({
                        'sample_index': i,
                        'distance': float(row[0]),
                        'timestamp': timestamp,
                    })
            except (ValueError, IndexError) as e:
                print(f"Warning: Skipping row {i+1} due to error: {str(e)}")
                continue
                
    if not data:
        raise ValueError("No valid data points found in the file")
        
    return data

def upload_data_to_postgres(file_path, location_id, sensor_id, sensor_type):
    conn = None
    cursor = None
    try:
        # Process the data based on sensor type
        sensor_data = process_sensor_data(file_path, sensor_type)
        
        print(f"Processing {len(sensor_data)} data points...")
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Create an acquisition session
        cursor.execute(
            """
            INSERT INTO acquisition_sessions 
            (location_id, sensor_id, status, start_time, file_name, metadata)
            VALUES (%s, %s, %s, NOW(), %s, %s)
            RETURNING id
            """,
            (location_id, sensor_id, 'completed', os.path.basename(file_path), 
             json.dumps({'sensor_type': sensor_type}))
        )
        session_id = cursor.fetchone()[0]
        
        # Insert sensor data
        for reading in sensor_data:
            # Base values that are common for all sensor types
            values = [
                session_id,  # session_id
                sensor_id,   # sensor_id
                reading['sample_index'],  # sample_index
                reading['timestamp'],     # timestamp
                json.dumps({}),          # metadata (empty for now)
            ]
            
            # Add sensor-specific values
            if sensor_type == 'LD':
                cursor.execute(
                    """
                    INSERT INTO sensor_data 
                    (session_id, sensor_id, sample_index, timestamp, metadata, voltage)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    values + [reading['voltage']]
                )
            elif sensor_type == 'ACCELEROMETER':
                cursor.execute(
                    """
                    INSERT INTO sensor_data 
                    (session_id, sensor_id, sample_index, timestamp, metadata, 
                     acceleration_x, acceleration_y, acceleration_z)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    values + [
                        reading['acceleration_x'],
                        reading['acceleration_y'],
                        reading['acceleration_z']
                    ]
                )
            elif sensor_type == 'RADAR':
                cursor.execute(
                    """
                    INSERT INTO sensor_data 
                    (session_id, sensor_id, sample_index, timestamp, metadata, distance)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    values + [reading['distance']]
                )
        
        # Update session end time
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
    
    args = parser.parse_args()
    
    try:
        print(f"Reading data from {args.file_path}...")
        upload_data_to_postgres(
            args.file_path,
            args.location_id,
            args.sensor_id,
            args.sensor_type
        )
        print("Data upload completed successfully")
    except Exception as e:
        print(f"Failed to upload data: {str(e)}")
        exit(1)

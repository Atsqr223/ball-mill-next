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
        for i, row in enumerate(reader):
            if sensor_type == 'LD':
                # LD sensor data has one voltage value per row
                data.append({
                    'sample_index': i,
                    'voltage': float(row[0]),
                    'timestamp': datetime.now().isoformat(),
                })
            elif sensor_type == 'ACCELEROMETER':
                # Accelerometer data has x, y, z values
                if len(row) >= 3:
                    data.append({
                        'sample_index': i,
                        'acceleration_x': float(row[0]),
                        'acceleration_y': float(row[1]),
                        'acceleration_z': float(row[2]),
                        'timestamp': datetime.now().isoformat(),
                    })
            elif sensor_type == 'RADAR':
                # Radar data has distance value
                data.append({
                    'sample_index': i,
                    'distance': float(row[0]),
                    'timestamp': datetime.now().isoformat(),
                })
    return data

def upload_data_to_postgres(file_path, location_id, sensor_id, sensor_type):
    conn = None
    cursor = None
    try:
        # Process the data based on sensor type
        sensor_data = process_sensor_data(file_path, sensor_type)
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Create an acquisition session
        cursor.execute(
            """
            INSERT INTO acquisition_sessions 
            (location_id, sensor_id, start_time, status, file_name, metadata)
            VALUES (%s, %s, NOW(), %s, %s, %s)
            RETURNING id
            """,
            (location_id, sensor_id, 'in_progress', os.path.basename(file_path), 
             json.dumps({'sensor_type': sensor_type}))
        )
        session_id = cursor.fetchone()[0]
        
        # Insert sensor data based on sensor type
        for reading in sensor_data:
            if sensor_type == 'LD':
                cursor.execute(
                    """
                    INSERT INTO sensor_data 
                    (session_id, sensor_id, sample_index, voltage, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (session_id, sensor_id, reading['sample_index'],
                     reading['voltage'], reading['timestamp'])
                )
            elif sensor_type == 'ACCELEROMETER':
                cursor.execute(
                    """
                    INSERT INTO sensor_data 
                    (session_id, sensor_id, sample_index, acceleration_x, 
                     acceleration_y, acceleration_z, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (session_id, sensor_id, reading['sample_index'],
                     reading['acceleration_x'], reading['acceleration_y'],
                     reading['acceleration_z'], reading['timestamp'])
                )
            elif sensor_type == 'RADAR':
                cursor.execute(
                    """
                    INSERT INTO sensor_data 
                    (session_id, sensor_id, sample_index, distance, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (session_id, sensor_id, reading['sample_index'],
                     reading['distance'], reading['timestamp'])
                )
        
        # Update session status to completed
        cursor.execute(
            """
            UPDATE acquisition_sessions 
            SET status = 'completed', end_time = NOW()
            WHERE id = %s
            """,
            (session_id,)
        )
        
        # Commit the transaction
        conn.commit()
        print(f"Successfully uploaded data for session {session_id}")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error uploading data: {str(e)}")
        raise
    
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
        upload_data_to_postgres(
            args.file_path,
            args.location_id,
            args.sensor_id,
            args.sensor_type
        )
    except Exception as e:
        print(f"Failed to upload data: {str(e)}")
        exit(1)

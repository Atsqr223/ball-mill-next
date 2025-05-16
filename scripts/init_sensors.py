# Initialize sensors in the database
import os
import sys
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get database connection string from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')

# Sensor types to be added to each location
SENSOR_TYPES = [
    {
        'name': 'Radar Sensor',
        'type': 'radar',
        'status': 'active'
    },
    {
        'name': 'Microphone',
        'type': 'audio',
        'status': 'active'
    },
    {
        'name': 'Accelerometer',
        'type': 'acceleration',
        'status': 'active'
    },
    {
        'name': 'LD Sensor',
        'type': 'laser_distance',
        'status': 'active'
    }
]

# Location IDs (matching the IDs in init_locations.py)
LOCATION_IDS = [1, 2, 3]  # TCSRI, IITKGP, TCS_JAM

def init_sensors():
    conn = None
    cur = None
    try:
        # Connect to the database using the connection string from .env
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Get the actual columns in the sensors table
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'sensors'")
        columns = [row[0] for row in cur.fetchall()]
        print(f"Actual columns in sensors table: {columns}")

        # Clear existing sensors
        cur.execute("DELETE FROM sensors")

        # Insert sensors for each location
        sensor_id = 1
        current_time = datetime.now().isoformat()
        
        for location_id in LOCATION_IDS:
            for sensor_type in SENSOR_TYPES:
                # Construct the SQL query based on the actual columns
                if 'unit' in columns:
                    cur.execute(
                        """
                        INSERT INTO sensors (id, location_id, name, type, status, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (sensor_id, location_id, sensor_type['name'], sensor_type['type'], 
                         sensor_type['status'], current_time, current_time)
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO sensors (id, name, type, location_id, status, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (sensor_id, sensor_type['name'], sensor_type['type'], location_id,
                         sensor_type['status'], current_time, current_time)
                    )
                sensor_id += 1

        # Commit the changes
        conn.commit()
        print(f"Successfully initialized {(sensor_id-1)} sensors across {len(LOCATION_IDS)} locations")

    except Exception as e:
        print(f"Error initializing sensors: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    init_sensors()

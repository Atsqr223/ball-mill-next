#to init the locations.
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database connection string from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')

# Locations configuration
LOCATIONS = [
    {
        'id': 1,
        'name': 'TCSRI',
        'youtube_stream_id': 'jfKfPfyJRdk',
        'status': 'active'
    },
    {
        'id': 2,
        'name': 'IITKGP',
        'youtube_stream_id': 'jfKfPfyJRdk',
        'status': 'active'
    },
    {
        'id': 3,
        'name': 'TCS_JAM',
        'youtube_stream_id': 'jfKfPfyJRdk',
        'status': 'active'
    }
]

def init_locations():
    conn = None
    cur = None
    try:
        # Connect to the database using the connection string from .env
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Clear existing locations
        cur.execute("DELETE FROM locations")

        # Insert new locations
        for location in LOCATIONS:
            cur.execute(
                """
                INSERT INTO locations (id, name, youtube_stream_id, status)
                VALUES (%s, %s, %s, %s)
                """,
                (location['id'], location['name'], location['youtube_stream_id'], location['status'])
            )

        # Commit the changes
        conn.commit()
        print("Successfully initialized locations in the database")

    except Exception as e:
        print(f"Error initializing locations: {e}")
        sys.exit(1)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    init_locations()

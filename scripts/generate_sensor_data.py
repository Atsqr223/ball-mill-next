import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Function to generate sample sensor data
def generate_sample_data(num_rows=100):
    # Create a directory for the sample data if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate timestamps (one reading every 5 seconds)
    now = datetime.now()
    timestamps = [(now - timedelta(seconds=5*i)).strftime('%Y-%m-%d %H:%M:%S') for i in range(num_rows)]
    
    # Generate vibration sensor data with some noise and periodic patterns
    vibration_values = []
    for i in range(num_rows):
        # Base value with some sine wave pattern
        base = 0.5 + 0.3 * np.sin(i/10)
        # Add some random noise
        noise = random.uniform(-0.1, 0.1)
        # Add occasional spikes
        spike = 0.5 if random.random() < 0.05 else 0
        vibration_values.append(round(base + noise + spike, 3))
    
    # Create a DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'sensor_id': 1,  # Assuming sensor_id 1 exists in your database
        'value': vibration_values
    })
    
    # Save to CSV
    csv_path = os.path.join(data_dir, 'sample_sensor_data.csv')
    df.to_csv(csv_path, index=False)
    print(f"Sample data generated and saved to {csv_path}")
    return csv_path

if __name__ == "__main__":
    generate_sample_data(100)

import numpy as np

def get_angles_from_pixels_pipe(x, y):
    """
    Convert pixel coordinates to angles for spatial filtering in a pipe setup.
    
    Args:
        x (int): X coordinate in the heatmap (0 to width-1)
        y (int): Y coordinate in the heatmap (0 to height-1)
        
    Returns:
        tuple: (theta, phi) angles in radians, or None if invalid coordinates
    """
    try:
        # Convert pixel coordinates to normalized coordinates (-1 to 1)
        x_norm = (x / 32) * 2 - 1  # Assuming 32x32 heatmap
        y_norm = (y / 32) * 2 - 1
        
        # Ensure coordinates are within valid range
        x_norm = np.clip(x_norm, -1, 1)
        y_norm = np.clip(y_norm, -1, 1)
        
        # Convert to angles
        # For pipe setup, we use:
        # - theta: angle around the pipe (0 to 2π)
        # - phi: angle along the pipe (0 to π)
        theta = np.arctan2(y_norm, x_norm)  # Angle around pipe
        
        # Calculate radius and ensure it's within valid range for arccos
        radius = np.sqrt(x_norm**2 + y_norm**2)
        radius = np.clip(radius, 0, 1)  # Ensure radius is between 0 and 1
        phi = np.arccos(radius)  # Angle along pipe
        
        return theta, phi
    except Exception as e:
        print(f"Error converting pixel coordinates to angles: {str(e)}")
        return None 
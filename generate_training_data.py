import random
import json
import numpy as np
from datetime import datetime, timedelta

# Base location (Chennai)
BASE_LAT = 13.0827
BASE_LON = 80.2707

def generate_device_data(num_samples=10000):
    """Generate synthetic training data for device prediction and route optimization."""
    data = []

    for _ in range(num_samples):
        # Device properties
        lat = BASE_LAT + random.uniform(-0.05, 0.05)  # Wider area
        lon = BASE_LON + random.uniform(-0.05, 0.05)
        battery = random.randint(0, 100)
        active = random.choice([True, False])  # Will fail or not
        signal_strength = random.uniform(0, 1)  # 0 to 1
        distance_from_base = np.sqrt((lat - BASE_LAT)**2 + (lon - BASE_LON)**2)

        # Simulate neighbors (up to 5)
        num_neighbors = random.randint(0, 5)
        neighbors = []
        for _ in range(num_neighbors):
            n_lat = lat + random.uniform(-0.01, 0.01)
            n_lon = lon + random.uniform(-0.01, 0.01)
            n_battery = random.randint(0, 100)
            n_active = random.choice([True, False])
            neighbors.append({
                'lat': round(n_lat, 6),
                'lon': round(n_lon, 6),
                'battery': n_battery,
                'active': n_active
            })

        # Features for prediction
        features = {
            'lat': lat,
            'lon': lon,
            'battery': battery,
            'signal_strength': signal_strength,
            'distance_from_base': distance_from_base,
            'num_neighbors': num_neighbors,
            'avg_neighbor_battery': np.mean([n['battery'] for n in neighbors]) if neighbors else 0,
            'active_neighbors': sum(1 for n in neighbors if n['active'])
        }

        # Labels
        # Predict if device will remain active (for prediction model)
        will_fail = not active  # If not active, it failed

        # For route optimization: simulate optimal path cost (lower is better)
        # Cost based on battery, signal, distance
        path_cost = (100 - battery) * 0.5 + (1 - signal_strength) * 10 + distance_from_base * 100

        data.append({
            'features': features,
            'will_fail': will_fail,
            'path_cost': path_cost,
            'neighbors': neighbors
        })

    return data

if __name__ == "__main__":
    print("Generating synthetic training data...")
    data = generate_device_data(10000)
    with open('training_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Generated {len(data)} samples and saved to training_data.json")
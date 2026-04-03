import torch
import torch.nn as nn
import pickle
import numpy as np

class BigNeuralNetwork(nn.Module):
    def __init__(self, input_size, output_size, task='prediction'):
        super(BigNeuralNetwork, self).__init__()
        self.task = task

        self.layers = nn.Sequential(
            nn.Linear(input_size, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, output_size)
        )

        if task == 'prediction':
            self.layers.add_module('sigmoid', nn.Sigmoid())

    def forward(self, x):
        return self.layers(x)

class AIModel:
    def __init__(self):
        self.pred_model = None
        self.opt_model = None
        self.pred_scaler = None
        self.opt_scaler = None
        self.load_models()

    def load_models(self):
        try:
            # Load prediction model
            self.pred_model = BigNeuralNetwork(8, 1, 'prediction')
            self.pred_model.load_state_dict(torch.load('prediction_model.pth'))
            self.pred_model.eval()

            with open('prediction_scaler.pkl', 'rb') as f:
                self.pred_scaler = pickle.load(f)

            # Load optimization model
            self.opt_model = BigNeuralNetwork(8, 1, 'optimization')
            self.opt_model.load_state_dict(torch.load('optimization_model.pth'))
            self.opt_model.eval()

            with open('optimization_scaler.pkl', 'rb') as f:
                self.opt_scaler = pickle.load(f)

            print("AI models loaded successfully!")
        except FileNotFoundError:
            print("Model files not found. Please train the models first.")
        except Exception as e:
            print(f"Error loading models: {e}")

    def predict_device_failure(self, lat, lon, battery, signal_strength, distance_from_base, num_neighbors, avg_neighbor_battery, active_neighbors):
        """Predict if a device will fail."""
        if self.pred_model is None:
            return None

        features = np.array([[lat, lon, battery, signal_strength, distance_from_base, num_neighbors, avg_neighbor_battery, active_neighbors]])
        features_scaled = self.pred_scaler.transform(features)
        features_tensor = torch.tensor(features_scaled, dtype=torch.float32)

        with torch.no_grad():
            prediction = self.pred_model(features_tensor).item()

        return prediction > 0.5  # Will fail if > 0.5

    def predict_path_cost(self, lat, lon, battery, signal_strength, distance_from_base, num_neighbors, avg_neighbor_battery, active_neighbors):
        """Predict optimal path cost for routing."""
        if self.opt_model is None:
            return None

        features = np.array([[lat, lon, battery, signal_strength, distance_from_base, num_neighbors, avg_neighbor_battery, active_neighbors]])
        features_scaled = self.opt_scaler.transform(features)
        features_tensor = torch.tensor(features_scaled, dtype=torch.float32)

        with torch.no_grad():
            cost = self.opt_model(features_tensor).item()

        return cost

# Global instance
ai_model = AIModel()
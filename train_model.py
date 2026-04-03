import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error
import pickle

class DeviceDataset(Dataset):
    def __init__(self, data, scaler=None, task='prediction'):
        self.task = task
        features = []
        labels = []

        for item in data:
            feat = [
                item['features']['lat'],
                item['features']['lon'],
                item['features']['battery'],
                item['features']['signal_strength'],
                item['features']['distance_from_base'],
                item['features']['num_neighbors'],
                item['features']['avg_neighbor_battery'],
                item['features']['active_neighbors']
            ]
            features.append(feat)

            if task == 'prediction':
                labels.append(item['will_fail'])
            elif task == 'optimization':
                labels.append(item['path_cost'])

        self.features = np.array(features)
        self.labels = np.array(labels)

        if scaler is None:
            self.scaler = StandardScaler()
            self.features = self.scaler.fit_transform(self.features)
        else:
            self.scaler = scaler
            self.features = self.scaler.transform(self.features)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return torch.tensor(self.features[idx], dtype=torch.float32), torch.tensor(self.labels[idx], dtype=torch.float32 if self.task == 'optimization' else torch.long)

class BigNeuralNetwork(nn.Module):
    def __init__(self, input_size, output_size, task='prediction'):
        super(BigNeuralNetwork, self).__init__()
        self.task = task

        # Large network for "big" model
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

def train_model(data, task='prediction', epochs=50, batch_size=32):
    # Split data
    train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

    # Create datasets
    train_dataset = DeviceDataset(train_data, task=task)
    test_dataset = DeviceDataset(test_data, train_dataset.scaler, task=task)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    # Model
    input_size = 8  # Number of features
    output_size = 1 if task == 'prediction' else 1  # Binary classification or regression

    model = BigNeuralNetwork(input_size, output_size, task)

    # Loss and optimizer
    if task == 'prediction':
        criterion = nn.BCELoss()
    else:
        criterion = nn.MSELoss()

    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Training loop
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for features, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(features).squeeze()
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        if (epoch + 1) % 10 == 0:
            print(f'Epoch {epoch+1}/{epochs}, Loss: {train_loss/len(train_loader):.4f}')

    # Evaluation
    model.eval()
    predictions = []
    actuals = []
    with torch.no_grad():
        for features, labels in test_loader:
            outputs = model(features).squeeze()
            if task == 'prediction':
                predictions.extend((outputs > 0.5).int().numpy())
            else:
                predictions.extend(outputs.numpy())
            actuals.extend(labels.numpy())

    if task == 'prediction':
        acc = accuracy_score(actuals, predictions)
        print(f'Prediction Model Accuracy: {acc:.4f}')
    else:
        mse = mean_squared_error(actuals, predictions)
        print(f'Optimization Model MSE: {mse:.4f}')

    # Save model and scaler
    torch.save(model.state_dict(), f'{task}_model.pth')
    with open(f'{task}_scaler.pkl', 'wb') as f:
        pickle.dump(train_dataset.scaler, f)

    return model, train_dataset.scaler

if __name__ == "__main__":
    # Load data
    with open('training_data.json', 'r') as f:
        data = json.load(f)

    print("Training prediction model...")
    pred_model, pred_scaler = train_model(data, task='prediction', epochs=50)

    print("Training optimization model...")
    opt_model, opt_scaler = train_model(data, task='optimization', epochs=50)

    print("Models trained and saved!")
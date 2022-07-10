import torch
from torch.utils.data import Dataset, DataLoader, random_split
import torch.utils.data as util
import torch.nn as nn
import numpy as np
import os
import math

import DataRetriever as dr

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

#Some constants
CWD = os.getcwd()
INPUT_SIZE = 11
HIDDEN_SIZE = 10
LEARNING_RATE = 0.01
EPOCHS = 2 

class HistoryDataset(Dataset):

	def __init__(self): #, path = CWD):
		#Getting the data by using DataRetriever.py
		RawData = dr.HistoryScrap() #path = path)
		RawData.get_history()
		RawData.get_track_id()
		raw_data = np.array(RawData.get_features())

		#Setting up the sample size and features
		self.n_samples = raw_data.shape[0]
		self.x_data = torch.from_numpy(raw_data[:, 1:])

		#Normalizing the labels to have the values in [.9;1]
		raw_y_data = raw_data[:, [0]]
		raw_y_min = np.amin(raw_y_data)
		raw_y_max = np.amax(raw_y_data)
		scaled_y_data = .9 + ( ( (raw_y_data - raw_y_min) *0.1 ) / (raw_y_max - raw_y_min))
		self.y_data = torch.from_numpy(scaled_y_data)

	def __getitem__(self, index):
		return self.x_data[index], self.y_data[index]

	def __len__(self):
		return self.n_samples

class NNetwork(nn.Module):
	def __init__(self, input_size, hidden_size):
		super(NNetwork, self).__init__()
		self.input_size = input_size
		self.sigmoid = nn.Sigmoid()
		self.input_layer = nn.Linear(input_size, hidden_size)
		self.hidden_layer = nn.Linear(hidden_size, hidden_size)
		self.output_layer = nn.Linear(hidden_size, 1)

	def forward(self, x):
		out = self.input_layer(x)
		out = self.sigmoid(out)
		out = self.hidden_layer(out)
		out = self.sigmoid(out)
		out = self.output_layer(out)
		return out

dataset = HistoryDataset()

dataset_len = len(dataset)
train_len = math.floor(dataset_len * 0.2)
val_len = dataset_len - train_len

train_set, val_set = random_split(dataset, [train_len, val_len])

train_loader = DataLoader(dataset = train_set, batch_size = 200, shuffle = True, num_workers = 2)
val_loader = DataLoader(dataset = val_set, batch_size = 40, shuffle = False, num_workers = 2)



model = NNetwork(input_size = INPUT_SIZE, hidden_size = HIDDEN_SIZE).to(device)

criterion = nn.MSELoss()
optimizer = torch.optim.SGD(model.parameters(), lr = LEARNING_RATE)

if __name__ == '__main__':

import torch
import numpy as np
from torch import nn

class AvoidModel(nn.Module):
  def __init__(self, input_size, hidden_size, noise_size=0.01):
    super(AvoidModel, self).__init__()
    self.noise_amount = noise_size
    
    # Input = left, right, center, if robot present. 

    self.input_layer = nn.Linear(input_size, hidden_size)
    # self.hidden_layer = nn.Linear(hidden_size, hidden_size // 2)
    self.output_layer = nn.Linear(hidden_size, 2) # two motors

  # def forward(self, left, right, center, robot_found, floor_color):
  def forward(self, left, right, center, robot_found, floor_color, distance_to_wall, distance_to_robot):
      inp = self.input_layer(torch.Tensor([left, right, center, robot_found, floor_color, distance_to_wall, distance_to_robot]).float())
    #   act = torch.nn.functional.tanh(inp)

    #   hid = self.hidden_layer(act)
    #   act = torch.nn.functional.tanh(hid)

      out = self.output_layer(inp)
      norm = torch.nn.functional.tanh(out)
      return norm

  def get_parameters(self):
          return list(self.parameters())

  def mutate(self):
      """
      Mutates a random param
      """
      random_weight_index = np.random.randint(0, len(list(self.get_parameters())))

      should_mutate = np.random.random() < 0.2

      if should_mutate:
          param = self.get_parameters()[random_weight_index]
          param.data += torch.randn(param.size()) * self.noise_amount

  def crossover(self, other):
      for i, param in enumerate(self.get_parameters()):
          if i % 2 == 0:
              param.data = other.get_parameters()[i].data
      return self
  

class AvoidModelRNN(nn.Module):
    def __init__(self, input_size, hidden_size, noise_size=0.01):
        super(AvoidModelRNN, self).__init__()
        self.noise_amount = noise_size

        # Input: left, right, center, robot_found, floor_color, distance_to_wall
        self.input_layer = nn.Linear(input_size, hidden_size)
        
        # Recurrent hidden layer
        self.hidden_layer = nn.RNN(hidden_size, hidden_size // 2, nonlinearity='tanh')
        
        self.output_layer = nn.Linear(hidden_size // 2, 2)  # Two motors

        # Initial hidden state for recurrent connections
        self.hidden_state = None

    def forward(self, left, right, center, robot_found, floor_color, distance_to_wall):
        # Prepare input tensor
        inp = torch.Tensor([left, right, center, robot_found, floor_color, distance_to_wall]).float()
        
        # Pass through input layer
        inp = self.input_layer(inp)
        inp = torch.tanh(inp)

        # Prepare input for the recurrent layer (batch size of 1, sequence length of 1)
        inp = inp.unsqueeze(0).unsqueeze(0)  # Shape: (1, 1, hidden_size)
        
        # Recurrent layer with optional hidden state
        rnn_out, self.hidden_state = self.hidden_layer(inp, self.hidden_state)
        rnn_out = torch.tanh(rnn_out)

        # Pass through output layer
        out = self.output_layer(rnn_out.squeeze(0))  # Remove batch dimension
        norm = torch.tanh(out)

        return norm

    def get_parameters(self):
            return list(self.parameters())

    def mutate(self):
        """
        Mutates a random param
        """
        random_weight_index = np.random.randint(0, len(list(self.get_parameters())))

        should_mutate = np.random.random() < 0.5

        if should_mutate:
            param = self.get_parameters()[random_weight_index]
            param.data += torch.randn(param.size()) * self.noise_amount

    def crossover(self, other):
        for i, param in enumerate(self.get_parameters()):
            if i % 2 == 0:
                param.data = other.get_parameters()[i].data
        return self
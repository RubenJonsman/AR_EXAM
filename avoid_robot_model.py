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
  def forward(self, left, right, center, robot_found, floor_color):
      inp = self.input_layer(torch.Tensor([left, right, center, robot_found, floor_color]).float())
      act = torch.nn.functional.sigmoid(inp)

      # hid = self.hidden_layer(act)
      # act = torch.nn.functional.sigmoid(hid)

      out = self.output_layer(act)
      norm = torch.nn.functional.sigmoid(out)
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
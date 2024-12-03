from shapely import Point
from constants import SAFE, DANGER, WALL
from environment import Environment
from robot_pose import RobotPose

area_dict = {
    WALL: "WALL",
    DANGER: "DANGER",
    SAFE: "SAFE",
    4: "Undefined"
}

class FloorColorSensor:
    def __init__(self, node=None):
      self.color = DANGER
      self.node = node
      
    def detect_color(self):
      left_sensor = self.node.v.prox.ground.delta[0]
      right_sensor = self.node.v.prox.ground.delta[1]

      if left_sensor < 300 and right_sensor < 300:
          return WALL
      elif left_sensor < 900 and right_sensor < 930:
          return DANGER
      elif left_sensor < 1024 and right_sensor < 1024:
          return SAFE
      else:
          return 4 # unknown

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color

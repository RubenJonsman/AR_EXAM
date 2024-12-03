from constants import AVOIDER, SEEKER, STATE_COLOR_MAP
import numpy as np

lower_color = np.array([0 ,106 ,233])
upper_color = np.array([180 ,255 ,255])

class CameraSensor:
    def __init__(self, capture, type):
        self.capture = capture
        self.type = type

    def detect(self):
        if self.type == AVOIDER:
            # TODO: Detect red
            pass
        elif self.type == SEEKER:
            # TODO: Detect blue
            pass

    def get_color(self, robot):
        return  STATE_COLOR_MAP[robot.type, robot.state]


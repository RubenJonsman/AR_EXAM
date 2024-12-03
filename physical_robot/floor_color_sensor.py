from constants import SAFE, DANGER, WALL

area_dict = {WALL: "WALL", DANGER: "DANGER", SAFE: "SAFE", 4: "Undefined"}


class FloorColorSensor:
    def __init__(self, node=None):
        self.node = node

    def detect_color(self):
        left_sensor = self.node.v.prox.ground.delta[0]
        right_sensor = self.node.v.prox.ground.delta[1]

        print(left_sensor, right_sensor)

        if left_sensor < 300 and right_sensor < 300:
            return WALL
        elif left_sensor < 900 and right_sensor < 930:
            return DANGER
        elif left_sensor < 1024 and right_sensor < 1024:
            return SAFE
        else:
            return 4  # unknown

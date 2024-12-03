import random

# from avoid_robot_model import AvoidModel
from constants import (
    AVOIDER_COLOR,
    CAUGHT_STATE,
    DANGER,
    MAX_BACKUP,
    MAX_WHEEL_SPEED,
    DEFAULT_STATE,
    SAFE,
    SAFE_STATE,
    AVOIDER,
    SAFE,
    DANGER,
    WALL,
)
from camera_sensor import CameraSensor

from floor_color_sensor import FloorColorSensor
from proximity_sensor import ProximitySensor
from led import LEDHandler


class PhysicalRobot:
    def __init__(self, node, capture):
        self.node = node
        self.capture = capture
        self.type = type  # 0 avoider or 1 seeker
        self.state = DEFAULT_STATE  # 0 default, 1 safe, 2 caught

        self.floor_sensor = FloorColorSensor(node=node)
        self.proximity_sensor = ProximitySensor(node=node)
        self.camera_sensor = CameraSensor(capture=capture, type=self.type)
        self.LED = LEDHandler(node=node)

        self.back_up = 0  # counter for backing up
        self.set_motor_speeds(-30, 30)

        self.iters_since_last_detection = 0

    def set_motor_speeds(self, left_motor_speed, right_motor_speed):  # MODIFY
        self.node.v.motor.left.target = left_motor_speed
        self.node.v.motor.right.target = right_motor_speed

        self.node.flush()

    def update_robot_state_based_on_floor_color(self):
        # Stop updating the color if the avoider is caught
        if self.type == AVOIDER and self.state == CAUGHT_STATE:
            return

        self.floor_sensor.detect_color()
        color = self.floor_sensor.get_color()

        if self.state == CAUGHT_STATE:
            self.LED.change_led_color("PURPLE")
            return

        if color == SAFE:
            self.state = SAFE_STATE
            self.LED.change_led_color("ORANGE")
            return

        if color == DANGER:
            self.state = DEFAULT_STATE
            self.LED.change_led_color("RED")
            return

    def seek_robot(self):
        # self.set_motor_speeds(150, 300)
        # return

        if self.state == CAUGHT_STATE:
            self.set_motor_speeds(0, 0)
            return
        # TODO: Avoid other robots

        direction = self.camera_sensor.detect()

        print("Direction", direction)

        if direction is not None:
            base_speed = MAX_WHEEL_SPEED / 2
            left_speed = base_speed + direction * (MAX_WHEEL_SPEED - base_speed)
            right_speed = base_speed - direction * (MAX_WHEEL_SPEED - base_speed)

            sf = 1

            self.set_motor_speeds(int(left_speed * sf), int(right_speed * sf))

        elif self.iters_since_last_detection > 25:
            self.set_motor_speeds(30, -30)
            self.iters_since_last_detection = 0

        else:
            self.iters_since_last_detection += 1

    def avoid_robot(self):
        pass

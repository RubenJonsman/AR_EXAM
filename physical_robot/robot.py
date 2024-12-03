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
        self.left_motor_speed = 0
        self.right_motor_speed = 0

        self.floor_sensor = FloorColorSensor(node=node)
        self.proximity_sensor = ProximitySensor(node=node)
        self.camera_sensor = CameraSensor(capture=capture, type=self.type)
        self.LED = LEDHandler(node=node)

        self.back_up = 0  # counter for backing up

    def set_motor_speeds(self, left_motor_speed, right_motor_speed):  # MODIFY
        print("Setting motor speeds: ", left_motor_speed, right_motor_speed)
        self.left_motor_speed = left_motor_speed
        self.right_motor_speed = right_motor_speed
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

    # def get_distance_to_robot(self, other_robot): # MODIFY
    #     """ Returns a distance metric between this robot and another robot """
    #     return 0

    # if the distance to the other robot is less than threshold change the robots state to caught
    # def tag_robot(self, other_robot): # MODIFY
    #     distance = self.get_distance_to_robot(other_robot)
    #     if distance < 30:
    #         # print("Caught", other_robot)
    #         other_robot.state = CAUGHT_STATE

    def seek_robot(self):
        turn_speed = MAX_WHEEL_SPEED / 5
        (robot_found, location) = self.is_there_a_robot()  # MODIFY
        (location, other_robot) = self.camera_sensor.detect(AVOIDER_COLOR)  # MODIFY

        if other_robot is not None:
            if location == "left":
                self.set_motor_speeds(-turn_speed, turn_speed)
            elif location == "right":
                self.set_motor_speeds(turn_speed, -turn_speed)
            else:
                self.set_motor_speeds(MAX_WHEEL_SPEED, MAX_WHEEL_SPEED)
            self.tag_robot(other_robot)
        else:
            self.floor_sensor.detect_color()
            floor_color = self.floor_sensor.get_color()
            if floor_color == WALL:
                if self.back_up == 0:
                    self.back_up = MAX_BACKUP
                else:
                    self.set_motor_speeds(MAX_WHEEL_SPEED, MAX_WHEEL_SPEED)
                    self.back_up = 0

            if self.back_up > MAX_BACKUP // 2:
                self.set_motor_speeds(-MAX_WHEEL_SPEED, MAX_WHEEL_SPEED)
                self.back_up -= 1
                return
            if self.back_up > 0:
                self.set_motor_speeds(-MAX_WHEEL_SPEED, MAX_WHEEL_SPEED)
                self.back_up -= 1
                return

            left_wheel = random.randint(0, MAX_WHEEL_SPEED)
            right_wheel = random.randint(0, MAX_WHEEL_SPEED)
            self.set_motor_speeds(left_wheel, right_wheel)

    def avoid_robot(self):
        if self.state == CAUGHT_STATE:
            self.set_motor_speeds(0, 0)
            return
        # TODO: Avoid other robots

        direction = self.camera_sensor.detect()

        if direction is None:
            self.set_motor_speeds(0, 0)
        else:
            base_speed = MAX_WHEEL_SPEED / 2
            left_speed = base_speed + direction * (MAX_WHEEL_SPEED - base_speed)
            right_speed = base_speed - direction * (MAX_WHEEL_SPEED - base_speed)

            sf = 1

            self.set_motor_speeds(int(left_speed * sf), int(right_speed * sf))

import random
import time
import torch

from model import AvoidModel
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
    SEEKER,
    SAFE,
    DANGER,
    WALL,
    INPUT_SIZE,
    HIDDEN_SIZE
)
from camera_sensor import CameraSensor

from floor_color_sensor import FloorColorSensor
from proximity_sensor import ProximitySensor
from led import LEDHandler
from ir_signal import IRsignal


class PhysicalRobot:
    def __init__(self, node, capture, robot_type):
        self.node = node
        self.capture = capture
        self.type = robot_type  # 0 avoider or 1 seeker
        self.state = DEFAULT_STATE  # 0 default, 1 safe, 2 caught
        self.tx_signal = 0
        self.rx_signal = 0
        self.floor_sensor = FloorColorSensor(node=node)
        self.proximity_sensor = ProximitySensor(node=node)
        self.camera_sensor = CameraSensor(capture=capture, type=self.type)
        self.LED = LEDHandler(node=node)

        self.back_up = 0  # counter for backing up
        self.set_motor_speeds(-30, 30)

        self.iters_since_last_detection = 0


        if self.type == AVOIDER:
            self.tx_signal = 2
            model_path = "Store/model_111.pth"
            self.robot_model = AvoidModel(INPUT_SIZE, HIDDEN_SIZE)
            self.robot_model.load_state_dict(torch.load(model_path, weights_only=True))
            self.robot_model.eval()

        elif self.type == SEEKER:
            self.tx_signal = 1

    def receive_signal(self):
        self.rx_signal = self.proximity_sensor.get_proximity_signal()

    def set_motor_speeds(self, left_motor_speed, right_motor_speed):  # MODIFY
        self.node.v.motor.left.target = left_motor_speed
        self.node.v.motor.right.target = right_motor_speed

        print("left: ", left_motor_speed, "right: ", right_motor_speed)

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

        if self.floor_sensor.detect_color() == WALL:
            self.set_motor_speeds(-MAX_WHEEL_SPEED, -MAX_WHEEL_SPEED)
            for _ in range(100):
                pass
            self.set_motor_speeds(-MAX_WHEEL_SPEED, MAX_WHEEL_SPEED)
            for _ in range(100):
                pass
            return

        direction, _, _, _, _ = self.camera_sensor.detect()

        if direction is not None:
            left_speed = MAX_WHEEL_SPEED + direction * (MAX_WHEEL_SPEED // 2)
            right_speed = MAX_WHEEL_SPEED - direction * (MAX_WHEEL_SPEED // 2)

            self.set_motor_speeds(int(left_speed), int(right_speed))

        elif self.iters_since_last_detection > 25:
            left = random.randint(-MAX_WHEEL_SPEED,MAX_WHEEL_SPEED)
            right = random.randint(-MAX_WHEEL_SPEED,MAX_WHEEL_SPEED)
            self.set_motor_speeds(left, right)
            self.iters_since_last_detection = 0

        else:
            self.iters_since_last_detection += 1

    def avoid_robot(self):
        if self.state == CAUGHT_STATE:
            self.set_motor_speeds(0, 0)
            return
        

        (_, robot_found, location, self.distance_to_robot, self.distance_to_wall) = self.camera_sensor.detect()
        # self.distance_to_wall, nearest_wall = (self.camera_sensor.get_distance_and_angle_to_wall())
        if self.distance_to_wall is None:
            self.distance_to_wall = 1000

        # self.distance_to_robot, nearest_robot = self.camera_sensor.get_distance_to_robot_in_view()
        if self.distance_to_robot is None:
            self.distance_to_robot = 1000

        floor_color = self.floor_sensor.detect_color()
        left, right, center = 0, 0, 0
        if location == "left":
            left = 1
        elif location == "right":
            right = 1
        elif location == "center":
            center = 1

        robot_found_bool = 0
        if robot_found:
            robot_found_bool = 1

        # self.distance_to_wall = 1000

        floor_color = DANGER
        print(f"Left: {left} Right: {right} Center: {center} Robot Found: {robot_found_bool} Floor Color: {floor_color} Distance to Wall: {self.distance_to_wall} Distance to Robot: {self.distance_to_robot}")
        output = self.robot_model.forward(left, right, center, robot_found_bool, floor_color, self.distance_to_wall, self.distance_to_robot)
        left_wheel, right_wheel = (output[0].item() * MAX_WHEEL_SPEED, output[1].item() * MAX_WHEEL_SPEED,)
        print(left_wheel, right_wheel)
        self.set_motor_speeds(round(left_wheel), round(right_wheel))
        # self.set_motor_speeds(0,0)

        

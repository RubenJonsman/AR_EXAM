import pygame
#from sensors import CompassSensor  # Import the LidarSensor class
import math
import random
import numpy as np
from constants import BLACK_WALL_ZONE, CAMERA_RANGE, CAUGHT_STATE, MAX_BACKUP, MAX_WHEEL_SPEED, STATE_COLOR_MAP, DEFAULT_STATE, GREY_DANGER_ZONE, SAFE_STATE, SILVER_SAFE_ZONE
from shapely.geometry import  Polygon
from camera_sensor import CameraSensor
from environment import Environment
from floor_color_sensor import FloorColorSensor
from robot_pose import RobotPose

class DifferentialDriveRobot:
    def __init__(self, x, y, theta, image_path, type, axl_dist=5, wheel_radius=2.2):
        self.x = x
        self.y = y
        self.theta = theta  # Orientation in radians
        self.axl_dist = axl_dist
        self.wheel_radius = wheel_radius
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.currently_turning = 0
        self.angular_velocity = 0
        self.linear_velocity = 0

        self.type = type # 0 avoider or 1 seeker
        self.state = DEFAULT_STATE # 0 default, 1 safe, 2 caught

        self.landmarks = []
        self.left_motor_speed = 0
        self.right_motor_speed = 0
        self.compass = CompassSensor()
        self.odometry_weight = 0.0
        self.odometry_noise_level = 0.01
        self.camera_sensor = CameraSensor(camera_range=CAMERA_RANGE)

        self.floor_sensor = FloorColorSensor()
        self.back_up = 0 # counter for backing up

    def predict(self, delta_time):
        self.move(delta_time)
        # Update orientation (theta) using the robot's compass sensor
        #compass_heading = self.compass.read_compass_heading(self.theta,self.angular_velocity, delta_time)

        # Blend odometry and compass headings
        #blended_heading = (self.odometry_weight * self.theta) + ((1-self.odometry_weight) * compass_heading)

        # Update the robot's orientation
        #self.theta = blended_heading

        return RobotPose(self.x, self.y, self.theta)

    def move(self, delta_time):
        # Assume maximum linear velocity at motor speed 500
        v_max = 10  # pixels/second
        # Calculate the linear velocity of each wheel
        left_wheel_velocity = (self.left_motor_speed / 500) * v_max
        right_wheel_velocity = (self.right_motor_speed / 500) * v_max

        v_x = math.cos(self.theta) * (self.wheel_radius * (left_wheel_velocity + right_wheel_velocity) / 2)
        v_y = math.sin(self.theta) * (self.wheel_radius * (left_wheel_velocity + right_wheel_velocity) / 2)
        omega = (self.wheel_radius * (left_wheel_velocity - right_wheel_velocity)) / (2 * self.axl_dist)

        self.x += (v_x * delta_time)
        self.y += (v_y * delta_time)
        self.theta += (omega * delta_time)


    def set_motor_speeds(self, left_motor_speed, right_motor_speed):
        self.left_motor_speed = left_motor_speed
        self.right_motor_speed = right_motor_speed


    def get_robot_position(self):
        return RobotPose(self.x, self.y, self.theta)

    def update_estimated_position(self, estimated_pose):
        self.x = estimated_pose.x
        self.y= estimated_pose.y
        self.theta = estimated_pose.theta

    # def draw(self, surface):
    #     rotated_image = pygame.transform.rotate(self.image, math.degrees(-1*self.theta))
    #     self.rect.center = (int(self.x), int(self.y))
    #     new_rect = rotated_image.get_rect(center=self.rect.center)
    #     surface.blit(rotated_image, new_rect)

    #      # Calculate the left and right wheel positions
    #     half_axl = self.axl_dist
    #     left_wheel_x = self.x - half_axl * math.sin(self.theta)
    #     left_wheel_y = self.y + half_axl * math.cos(self.theta)
    #     right_wheel_x = self.x + half_axl * math.sin(self.theta)
    #     right_wheel_y = self.y - half_axl * math.cos(self.theta)

    #     # Calculate the heading line end point
    #     heading_length = 45
    #     heading_x = self.x + heading_length * math.cos(self.theta)
    #     heading_y = self.y + heading_length * math.sin(self.theta)

    #     # Draw the axle line
    #     pygame.draw.line(surface, (0, 255, 0), (left_wheel_x, left_wheel_y), (right_wheel_x, right_wheel_y), 3)

    #     # Draw the heading line
    #     color =  STATE_COLOR_MAP[self.type, self.state]
    #     pygame.draw.line(surface, color, (self.x, self.y), (heading_x, heading_y), 4)


    def draw(self, surface):
        # Rotate and draw the robot image
        rotated_image = pygame.transform.rotate(self.image, math.degrees(-1 * self.theta))
        self.rect.center = (int(self.x), int(self.y))
        new_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, new_rect)

        # Calculate the left and right wheel positions
        half_axl = self.axl_dist
        left_wheel_x = self.x - half_axl * math.sin(self.theta)
        left_wheel_y = self.y + half_axl * math.cos(self.theta)
        right_wheel_x = self.x + half_axl * math.sin(self.theta)
        right_wheel_y = self.y - half_axl * math.cos(self.theta)

        # Draw the axle line
        pygame.draw.line(surface, (0, 255, 0), (left_wheel_x, left_wheel_y), (right_wheel_x, right_wheel_y), 3)

        # Draw the heading line
        heading_length = 45
        heading_x = self.x + heading_length * math.cos(self.theta)
        heading_y = self.y + heading_length * math.sin(self.theta)
        color = STATE_COLOR_MAP[self.type, self.state]
        pygame.draw.line(surface, color, (self.x, self.y), (heading_x, heading_y), 4)

        # Add trapezoid for the camera view
        _, camera_point_list  = self.camera_sensor.create_view_frustum(self.get_robot_position())

        # Draw the trapezoid
        pygame.draw.polygon(surface, (255, 0, 0, 100), camera_point_list, width=1)

    def update_robot_state_based_on_floor_color(self, environment: Environment, robot_pose: RobotPose):
        self.floor_sensor.detect_color(environment=environment, robot_pose=robot_pose)
        color = self.floor_sensor.get_color()

        if self.state == CAUGHT_STATE:
            return

        if color == SILVER_SAFE_ZONE:
            self.state = SAFE_STATE
            return

        if color == GREY_DANGER_ZONE:
            self.state = DEFAULT_STATE
            return

    def getMotorspeeds(self):
        return (self.left_motor_speed, self.right_motor_speed)

    #Exercise 6.1 make the robot explore the environment.
    #Exercise 6.2 make the robot avoid the walls using lidar sensor data
    def explore_environment(self, lidar_scans):
        front_sensor = lidar_scans[0]
        front_right_sensor_1 = lidar_scans[len(lidar_scans)//8]
        right_sensor = lidar_scans[len(lidar_scans)//4]
        front_left_sensor_1 = lidar_scans[len(lidar_scans)//8 * 7]
        left_sensor = lidar_scans[len(lidar_scans)//4 * 3]

        wallDistance = 200
        speed = 1000
        if left_sensor < wallDistance and front_left_sensor_1 < wallDistance:
            self.set_motor_speeds(speed,0)
        elif right_sensor < wallDistance and front_right_sensor_1 < wallDistance:
            self.set_motor_speeds(0,speed)
        elif front_sensor < wallDistance:
            random_left = random.randrange(0, speed)
            random_right = random.randrange(0, speed)
            if random_right > random_left:
                self.set_motor_speeds(random_left,-random_right)
            else:
                self.set_motor_speeds(-random_left,random_right)
        else:
            self.set_motor_speeds(speed * (1 -(1/front_left_sensor_1)), speed - (1 + (1/front_right_sensor_1)))

    def avoid_robot(self, other_robots, environment):
        turn_speed = MAX_WHEEL_SPEED/5
        # (robot_found, location) = self.is_there_a_robot(*self.get_robot_position())
        robot_pose = self.get_robot_position()
        # (robot_found, location) = self.camera_sensor.detect(robot_pose, other_robots)
        # if robot_found:
        #     if location == "left":
        #         self.set_motor_speeds(-turn_speed, turn_speed)
        #     elif location == "right":
        #         self.set_motor_speeds(turn_speed, -turn_speed)
        #     else:
        #         self.set_motor_speeds(MAX_WHEEL_SPEED, MAX_WHEEL_SPEED)
        # else:
        self.floor_sensor.detect_color(robot_pose, environment)
        floor_color = self.floor_sensor.get_color()

        if floor_color == BLACK_WALL_ZONE:
            if self.back_up == 0:
                self.back_up = MAX_BACKUP
            else:
                self.set_motor_speeds(MAX_WHEEL_SPEED, MAX_WHEEL_SPEED)
                self.back_up =0

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

    def get_distance_to_robot(self, other_robot):
        selfPos = self.get_robot_position()
        x1, y1 = selfPos.x, selfPos.y
        otherPos = other_robot.get_robot_position()
        x2, y2 = otherPos.x, otherPos.y
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    # if the distance to the other robot is less than threshold change the robots state to caught
    def tag_robot(self, other_robot):
        distance = self.get_distance_to_robot(other_robot)
        if distance < 30:
            print("Caught", other_robot)
            other_robot.state = CAUGHT_STATE

    def seek_robot(self, other_robots, environment):
        turn_speed = MAX_WHEEL_SPEED/5
        # (robot_found, location) = self.is_there_a_robot(*self.get_robot_position())
        robot_pose = self.get_robot_position()
        (location, other_robot) = self.camera_sensor.detect(robot_pose, other_robots)

        # check if all robots are in the caught state
        all_caught = True
        for robot in other_robots:
            if robot.state != CAUGHT_STATE:
                all_caught = False
                break
        if all_caught:
            self.set_motor_speeds(-MAX_WHEEL_SPEED, MAX_WHEEL_SPEED)
            return

        if other_robot is not None:
            if location == "left":
                self.set_motor_speeds(-turn_speed, turn_speed)
            elif location == "right":
                self.set_motor_speeds(turn_speed, -turn_speed)
            else:
                self.set_motor_speeds(MAX_WHEEL_SPEED, MAX_WHEEL_SPEED)
            self.tag_robot(other_robot)
        else:
            self.floor_sensor.detect_color(robot_pose, environment)
            floor_color = self.floor_sensor.get_color()
            if floor_color == BLACK_WALL_ZONE:
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



    def manual_control(self, keys):
        speed = MAX_WHEEL_SPEED  # Define the base speed for manual control
        turn_speed = MAX_WHEEL_SPEED / 10  # Define the turning speed

        if keys[pygame.K_UP]:
            self.set_motor_speeds(speed, speed)  # Move forward
        elif keys[pygame.K_DOWN]:
            self.set_motor_speeds(-speed, -speed)  # Move backward
        elif keys[pygame.K_LEFT]:
            self.set_motor_speeds(-turn_speed, turn_speed)  # Turn left
        elif keys[pygame.K_RIGHT]:
            self.set_motor_speeds(turn_speed, -turn_speed)  # Turn right
        else:
            self.set_motor_speeds(0, 0)  # Stop if no keys are pressed

class CompassSensor:

    drift_rate=0.0001
    USE_DRIFT=False

    def __init__(self, noise_stddev=0.0001) -> None:
        self.noise_level = noise_stddev

    def read_compass_heading(self, start_heading, angular_velocity, delta_time):
         # Update orientation (theta) based on angular velocity
        start_heading += angular_velocity * delta_time

        # Ensure the orientation is within the range [0, 2*pi)
        start_heading = start_heading % (2 * math.pi)

        # Add a small amount of noise to the orientation
        noise = random.gauss(0, self.noise_level)
        start_heading += noise

        # Introduce a small constant angular drift
        if self.USE_DRIFT:
            drift = self.drift_rate * delta_time
            start_heading += drift

        # Return the updated theta in radians
        return start_heading

import pygame
import random, math
from shapely import LineString, Point
from lidar import LidarSensor
from pygame.locals import QUIT, KEYDOWN
from environment import Environment
from robot import DifferentialDriveRobot
from robot_pose import RobotPose
from constants import AVOIDER, BLACK_WALL_ZONE, PADDING, SEEKER, WIDTH, HEIGHT

class GameBoard:
  def __init__(self):
    # Initialize Pygame
    pygame.init()

    self.env = Environment(WIDTH, HEIGHT)

    offset = 20 + PADDING

    self.starting_positions =[
      (SEEKER, WIDTH/2, HEIGHT/2),
      (AVOIDER, WIDTH - offset, HEIGHT - offset),
      (AVOIDER, 0 + offset, 0 + offset),
      (AVOIDER, WIDTH- offset, 0 + offset),
      (AVOIDER, 0 + offset, HEIGHT- offset)
    ]

    # Initialize lidar and robot
    self.robot = DifferentialDriveRobot(WIDTH/2, HEIGHT/2, 2.6, 'thymio_small.png', type=SEEKER)

    # spawn robots in the corners
    self.robots = [DifferentialDriveRobot(x, y, 2.6, 'thymio_small.png', type=r_type) for r_type, x, y in self.starting_positions]
    self.lidar = LidarSensor()

    # For potential visualization
    self.USE_VISUALIZATION = True
    self.DRAW_LIDAR = False
    self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Robotics Simulation")

    # Timestep counter in milliseconds
    self.last_time = pygame.time.get_ticks()

    # Collision notifier, that shows you if you run into a wall
    self.showEnd = True

  def visualize(self):
    # Game loop
    running = True
    while running:
      for event in pygame.event.get():
        if event.type == QUIT:
          running = False

      keys = pygame.key.get_pressed()

      # Calculate timestep
      time_step = (pygame.time.get_ticks() - self.last_time) / 1000
      self.last_time = pygame.time.get_ticks()

      self.robots[0].manual_control(keys)

      for r in self.robots:

      # This is the odometry where we use the wheel size and speed to calculate
      # where we approximately end up.
        robot_pose = r.predict(time_step)

        # Generate Lidar scans - for these exercises, you will be given these.
        lidar_scans, _intersect_points = self.lidar.generate_scans(robot_pose, self.env.get_environment())
        # EXERCISE 6.1: make the robot move and navigate the environment based on our current sensor information and our current map.

        r.update_robot_state_based_on_floor_color(self.env, robot_pose)
        # print(self.robots[0].floor_sensor.get_color())

      # self.robot.explore_environment(lidar_scans)

      if self.USE_VISUALIZATION:
        self.screen.fill((0, 0, 0))
        self.env.draw(self.screen)
        for robot in self.robots:
          robot.draw(self.screen)

        if self.DRAW_LIDAR:
          self.lidar.draw(robot_pose, _intersect_points, self.screen)

        pygame.display.flip()
        pygame.display.update()

    # Quit Pygame
    pygame.quit()

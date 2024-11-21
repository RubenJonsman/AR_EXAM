from collections import defaultdict

import numpy as np
import pygame
import random, math

from matplotlib import pyplot as plt
from scipy.stats import linregress
from shapely import LineString, Point
from lidar import LidarSensor
from pygame.locals import QUIT, KEYDOWN
from environment import Environment
from robot import DifferentialDriveRobot
from robot_pose import RobotPose
from constants import AVOIDER, BLACK_WALL_ZONE, CAUGHT_STATE, CONCURRENT_GAMES, EPISODE_TIME, PADDING, SEEKER, WIDTH, \
    HEIGHT

from avoid_robot_model import AvoidModel


class GameBoard:
    def __init__(self):
        # Initialize Pygame
        self.episode_start_time = None
        self.fitness_scores = defaultdict()
        self.gamesRobots = None
        self.trend_y = None
        self.trend_x = None
        self.slope = None
        self.recent_means = None
        self.recent_episodes = None

        pygame.init()

        self.env = Environment(WIDTH, HEIGHT)
        self.games = CONCURRENT_GAMES
        self.population_size = 4 * self.games
        self.TOP_N = self.population_size // 2

        self.trainingTime = EPISODE_TIME

        self.mean_fitness_history = {}  # Stores mean fitness over time for visualization
        plt.ion()  # Enable interactive mode for live-updating
        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Fitness Over Time")
        self.ax.set_xlabel("Episode")
        self.ax.set_ylabel("Fitness")
        self.mean_line, = self.ax.plot([], [], 'b-', label="Mean Fitness")  # Mean fitness line
        self.min_line, = self.ax.plot([], [], 'g-', label="Min Fitness")  # Min fitness line
        self.max_line, = self.ax.plot([], [], 'r-', label="Max Fitness")  # Max fitness line
        self.trend_line, = self.ax.plot([], [], 'k--', label="5-episode Trend")  # Trend line for the last 5 episodes

        self.episodes, self.mean_fitness_values, self.min_fitness_values, self.max_fitness_values = [], [], [], []  # Lists to store data for plotting
        self.ax.legend()  # Show legend for lines

        offset = 20 + PADDING

        self.starting_positions = [
            (SEEKER, WIDTH / 2, HEIGHT / 2),
            (AVOIDER, WIDTH - offset, HEIGHT - offset),
            (AVOIDER, 0 + offset, 0 + offset),
            (AVOIDER, WIDTH - offset, 0 + offset),
            (AVOIDER, 0 + offset, HEIGHT - offset)
        ]

        # spawn robots in the corners
        self.initialize_robots()
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

    def initialize_robots(self):
        # spawn robots in the corners
        self.gamesRobots = [
            [DifferentialDriveRobot(x, y, 2.6, 'thymio_small.png', type=r_type) for r_type, x, y in
             self.starting_positions]
            for _ in range(self.games)
        ]

    def update_trend_line(self):
        # Calculate trend line for the last 5 episodes if there are enough data points
        if len(self.mean_fitness_values) >= 5:
            self.recent_episodes = self.episodes[-5:]
            self.recent_means = self.mean_fitness_values[-5:]
            self.slope, intercept, _, _, _ = linregress(self.recent_episodes, self.recent_means)
            self.trend_x = np.array([self.recent_episodes[0], self.recent_episodes[-1]])
            self.trend_y = intercept + self.slope * self.trend_x
            self.trend_line.set_xdata(self.trend_x)
            self.trend_line.set_ydata(self.trend_y)
        else:
            self.trend_line.set_xdata([])
            self.trend_line.set_ydata([])

    def visualize(self):
        # Game loop
        running = True
        episode_count = 0  # Track episode count separately
        self.episode_start_time = pygame.time.get_ticks()

        while running:
            current_time = pygame.time.get_ticks()
            # print(current_time - self.episode_start_time, self.trainingTime)
            if (current_time - self.episode_start_time) >= self.trainingTime:
                # Calculate mean, min, max fitness values
                # mean_fitness = np.mean(self.fitness_scores)
                # min_fitness = np.min(self.fitness_scores)
                # max_fitness = np.max(self.fitness_scores)
                #
                # # Update live plot data
                # self.episodes.append(episode_count)
                # self.mean_fitness_values.append(mean_fitness)
                # self.min_fitness_values.append(min_fitness)
                # self.max_fitness_values.append(max_fitness)
                #
                # self.mean_line.set_xdata(self.episodes)
                # self.mean_line.set_ydata(self.mean_fitness_values)
                # self.min_line.set_xdata(self.episodes)
                # self.min_line.set_ydata(self.min_fitness_values)
                # self.max_line.set_xdata(self.episodes)
                # self.max_line.set_ydata(self.max_fitness_values)

                # Update trend line for the last 5 episodes
                # self.update_trend_line()

                # Rescale axes based on data
                # self.ax.relim()
                # self.ax.autoscale_view()
                # plt.draw()
                # plt.pause(0.01)  # Pause to update the figure

                episode_count += 1
                robot_scores = {}
                sorted_indices = np.argsort(self.fitness_scores)

                rank_weights = np.zeros(self.population_size)
                rank = 2
                for i in sorted_indices:
                    rank_weights[i] = 1 / rank
                    rank += 1
                rank_weights /= np.sum(rank_weights)

                top_n_indices = sorted_indices[-self.TOP_N:]
                all_models = np.array([model.avoid_model for model in np.array(self.gamesRobots).flatten() if
                                       model.avoid_model is not None])
                top_n_models = list(all_models[top_n_indices])
                rest_models = self.population_size - self.TOP_N
                new_models = top_n_models

                i = 0
                while i < rest_models:
                    two_robots = np.random.choice(all_models, size=2, p=rank_weights)
                    robot1_model = two_robots[0]
                    robot2_model = two_robots[1]
                    print(type(robot1_model))
                    new_robot_1 = robot1_model.crossover(robot2_model)
                    new_robot_2 = robot2_model.crossover(robot1_model)

                    new_models.append(new_robot_1)
                    new_models.append(new_robot_2)

                    i += 2

                for model in new_models:
                    model.mutate()

                robot_index = 0
                # Reassign models to the existing robots
                for model in np.array(self.gamesRobots).flatten():
                    if model.avoid_model is not None:
                        model.avoid_model = new_models[robot_index]
                        robot_index += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Calculate timestep
            time_step = (pygame.time.get_ticks() - self.last_time) / 1000
            self.last_time = pygame.time.get_ticks()

            for index in range(self.games):
                self.gamesRobots[index][0].seek_robot(self.gamesRobots[index][1:], self.env)

            for game in range(self.games):
                for idx, r in enumerate(self.gamesRobots[game]):
                    if idx != 0:
                        if r.state != CAUGHT_STATE:
                            other_robots = [robot for i, robot in enumerate(self.gamesRobots[game]) if i != idx]
                            # r.avoid_robot(other_robots, self.env)
                            reward = r.avoid_robot_model(other_robots, self.env)
                            # IDK HOW TO STORE THE FITNESS VALUES because someone decided to put all the robots into the same list :upsidedown:
                        else:
                            r.set_motor_speeds(0, 0)
                    # This is the odometry where we use the wheel size and speed to calculate
                    # where we approximately end up.
                    robot_pose = r.predict(time_step)

                    # Generate Lidar scans - for these exercises, you will be given these.
                    lidar_scans, _intersect_points = self.lidar.generate_scans(robot_pose, self.env.get_environment())

                    r.update_robot_state_based_on_floor_color(self.env, robot_pose)

                if self.USE_VISUALIZATION:
                    self.screen.fill((0, 0, 0))
                    self.env.draw(self.screen)
                    for game_index in range(self.games):
                        for robot in self.gamesRobots[game_index]:
                            robot.draw(self.screen)

                        if self.DRAW_LIDAR:
                            self.lidar.draw(robot_pose, _intersect_points, self.screen)

                        pygame.display.flip()
                        pygame.display.update()

        # Quit Pygame
        pygame.quit()

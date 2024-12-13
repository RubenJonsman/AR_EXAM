from collections import defaultdict
import os
import time
from typing import List

import numpy as np
import pygame
import random, math
import torch
from matplotlib import pyplot as plt
from scipy.stats import linregress
from shapely import LineString, Point

# from lidar import LidarSensor
from pygame.locals import QUIT, KEYDOWN
from environment import Environment
from robot import DifferentialDriveRobot
from robot_pose import RobotPose
from constants import (
    AVOIDER,
    WALL,
    CAUGHT_STATE,
    CONCURRENT_GAMES,
    EPISODE_TIME,
    PADDING,
    SEEKER,
    WIDTH,
    HEIGHT,
    PLAY_GAME,
    HIDDEN_SIZE,
    INPUT_SIZE
)

from avoid_robot_model import AvoidModel
# from avoid_robot_model import AvoidModelRNN as AvoidModel
# import pygad


class GameBoard:
    def __init__(self):
        # Initialize Pygame
        self.episode_start_time = None
        self.fitness_scores = defaultdict(int)
        self.gamesRobots = None
        self.trend_y = None
        self.trend_x = None
        self.slope = None
        self.recent_means = None
        self.recent_episodes = None
        pygame.init()
        # Move the Pygame window to avoid overlap with matplotlib windows
        os.environ['SDL_VIDEO_WINDOW_POS'] = "-2000,300"

        self.env = Environment(WIDTH, HEIGHT)
        self.games = CONCURRENT_GAMES
        self.population_size = 4 * self.games
        self.TOP_N = self.population_size // 3

        self.trainingTime = EPISODE_TIME * 1000

        self.mean_fitness_history = {}  # Stores mean fitness over time for visualization
        plt.ion()  # Enable interactive mode for live-updating

        # Create first figure for fitness over time
        self.fig, self.ax = plt.subplots()
        self.fig.canvas.manager.window.move(-700, 100)  # Move the first figure window
        self.ax.set_title("Fitness Over Time")
        self.ax.set_xlabel("Episode")
        self.ax.set_ylabel("Fitness")
        # Despline top and right spline
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.grid()  # Add grid lines

        (self.mean_line,) = self.ax.plot(
            [], [], "b-", label="Mean Fitness"
        )  # Mean fitness line
        (self.min_line,) = self.ax.plot(
            [], [], "g-", label="Min Fitness"
        )  # Min fitness line
        (self.max_line,) = self.ax.plot(
            [], [], "r-", label="Max Fitness"
        )  # Max fitness line
        (self.trend_line,) = self.ax.plot(
            [], [], "k--", label="5-episode Trend"
        )  # Trend line for the last 5 episodes

        (
            self.episodes,
            self.mean_fitness_values,
            self.min_fitness_values,
            self.max_fitness_values,
        ) = [], [], [], []  # Lists to store data for plotting
        self.ax.legend()  # Show legend for lines

        # Create second figure for survival time over time
        self.fig2, self.ax2 = plt.subplots()
        self.fig2.canvas.manager.window.move(-700, 700)  # Move the second figure window
        self.ax2.set_title("Survival Time Over Time")
        self.ax2.set_xlabel("Episode")
        self.ax2.set_ylabel("Survival Time")
        # Despline top and right spline
        self.ax2.spines['top'].set_visible(False)
        self.ax2.spines['right'].set_visible(False)
        self.ax2.grid()  # Add grid lines

         
        (self.mean_line_surival,) = self.ax2.plot(
            [], [], "b-", label="Mean Survival Time"
        )  # Mean fitness line
        (self.min_line_survival,) = self.ax2.plot(
            [], [], "g-", label="Min Survival Time"
        )  # Min fitness line
        (self.max_line_survival,) = self.ax2.plot(
            [], [], "r-", label="Max Survival Time"
        )  # Max fitness line
        # (self.trend_line_survival,) = self.ax2.plot(
        #     [], [], "k--", label="5-episode Survival Time Trend"
        # )  # Trend line for the last 5 episodes

        (
            self.episodes2,
            self.mean_survival_time_values,
            self.min_survival_time_values,
            self.max_survival_time_values,
        ) = [], [], [], []  # Lists to store data for plotting
        self.ax2.legend()  # Show legend for lines



        offset = 20 + PADDING
        offset = 100 + PADDING
        if PLAY_GAME:
            self.starting_positions = [
                (SEEKER, WIDTH / 2, HEIGHT / 2),
                (AVOIDER, WIDTH - offset, HEIGHT - offset),
                (AVOIDER, 0 + offset, 0 + offset),
                (AVOIDER, WIDTH - offset, 0 + offset),
                (AVOIDER, 0 + offset, HEIGHT - offset),
            ]
        else:
            # self.starting_positions = [
            #     (SEEKER, WIDTH / 2, HEIGHT / 2),
            #     (AVOIDER, WIDTH / 2 + offset, HEIGHT / 2),
            #     (AVOIDER, WIDTH / 2 + offset, HEIGHT / 2),
            #     (AVOIDER, WIDTH / 2 + offset, HEIGHT / 2),
            #     (AVOIDER, WIDTH / 2 + offset, HEIGHT / 2),
            # ]
            offset = 50 + PADDING
            self.starting_positions = [
                (SEEKER, WIDTH / 2, HEIGHT / 2),
                (AVOIDER, WIDTH - offset, HEIGHT - offset),
                (AVOIDER, 0 + offset, 0 + offset),
                (AVOIDER, WIDTH - offset, 0 + offset),
                (AVOIDER, 0 + offset, HEIGHT - offset),
            ]

        # spawn robots in the corners
        self.initialize_robots()
        # self.lidar = LidarSensor()

        # For potential visualization
        self.USE_VISUALIZATION = True
        # self.DRAW_LIDAR = False
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Robotics Simulation")

        # Timestep counter in milliseconds
        self.last_time = pygame.time.get_ticks()

        # Collision notifier, that shows you if you run into a wall
        self.showEnd = True

    def initialize_robots(self, models=None, episode_count=0):
        """
        Initialize robots for each game.
        If models are provided, assign them to the robots.

        Parameters:
        - models (list): A list of models to assign to the robots. If None, robots are initialized without models.
        """

        if episode_count > 100:
            self.starting_positions = [
            (SEEKER, WIDTH / 2, HEIGHT / 2),
            (AVOIDER, random.randint(PADDING, WIDTH-PADDING), random.randint(PADDING, HEIGHT-PADDING)),
            (AVOIDER, random.randint(PADDING, WIDTH-PADDING), random.randint(PADDING, HEIGHT-PADDING)),
            (AVOIDER, random.randint(PADDING, WIDTH-PADDING), random.randint(PADDING, HEIGHT-PADDING)),
            (AVOIDER, random.randint(PADDING, WIDTH-PADDING), random.randint(PADDING, HEIGHT-PADDING)),
        ]
            
        robot_id = 0
        self.gamesRobots: List[DifferentialDriveRobot] = []  # Initialize the main list
        models = (models or [None] * self.population_size)  # Default to None if no models provided
        model_index = 0  # Track the index in the models list

        for _ in range(self.games):  # Loop over the number of games
            game_robots = []  # List for robots in the current game
            for (r_type, x, y) in self.starting_positions:  # Loop over the starting positions
                angle_in_degrees = random.randint(0, 360)
                angle_in_radians = math.radians(angle_in_degrees)
                if r_type != SEEKER:
                    if PLAY_GAME:
                    # Load the robot model from file
                        model_path = "Store/model_111.pth"
                        robot_model = AvoidModel(INPUT_SIZE, HIDDEN_SIZE)
                        robot_model.load_state_dict(torch.load(model_path, weights_only=True))
                        robot_model.eval()
                    else:
                        robot_model = (models[model_index] if model_index < len(models) else None)

                    robot = DifferentialDriveRobot(x, y, angle_in_radians, "thymio_small.png", type=r_type, id=robot_id, model_state=robot_model)
                    model_index += 1  # Increment the model index
                else:
                    angle_in_degrees = random.randint(0, 360)
                    angle_in_radians = math.radians(angle_in_degrees)
                    robot = DifferentialDriveRobot(x, y, angle_in_radians, "thymio_small.png", type=r_type, id=robot_id, model_state=None)
                
                game_robots.append(robot)  # Add robot to the current game's list
                robot_id += 1  # Increment the unique ID
            self.gamesRobots.append(game_robots)  # Add the game's robots to the main list

    def update_trend_line(self):
        """
        Update the trend line for the last 5 episodes based on mean fitness values.
        If there are fewer than 5 episodes, the trend line is cleared.
        """
        # Calculate trend line for the last 5 episodes if there are enough data points
        if len(self.mean_fitness_values) >= 5:
            self.recent_episodes = self.episodes[-5:]
            self.recent_means = self.mean_fitness_values[-5:]
            self.slope, intercept, _, _, _ = linregress(
                self.recent_episodes, self.recent_means
            )
            self.trend_x = np.array([self.recent_episodes[0], self.recent_episodes[-1]])
            self.trend_y = intercept + self.slope * self.trend_x
            self.trend_line.set_xdata(self.trend_x)
            self.trend_line.set_ydata(self.trend_y)
        else:
            self.trend_line.set_xdata([])
            self.trend_line.set_ydata([])

    def visualize(self):
        # Game loop
        # time_start = time.time()
        running = True
        episode_count = 0  # Track episode count separately
        self.episode_start_time = pygame.time.get_ticks()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            current_time = pygame.time.get_ticks()

            # Increase training time as episode count increases, limit to maximum of 1 minute
            if PLAY_GAME:
                self.trainingTime = 60000
            elif episode_count > 250:
                count = 1
                while os.path.exists(f"experiments/fitness_over_time_{count}.pdf"):
                    count += 1
                # plt.savefig(f"experiments/fitness_over_time_{count}.pdf")
                # plt.savefig(f"experiments/survival_time_{count}.pdf")
                self.fig.savefig(f"experiments/fitness_over_time_{count}.pdf")
                self.fig2.savefig(f"experiments/survival_time_{count}.pdf")
                return
            else:
                self.trainingTime = min(EPISODE_TIME * 1000 + episode_count * 100, 60000)
                if (current_time - self.episode_start_time) >= self.trainingTime:
                    print(f"training time at {self.trainingTime / 1000} secs")

                    # Calculate mean, min, max fitness values

                    fitness_scored_list = list(self.fitness_scores.values())
                    robot_id_list = list(self.fitness_scores.keys())

                    print("fitness scores", fitness_scored_list)

                    mean_fitness = np.mean(fitness_scored_list)
                    min_fitness = np.min(fitness_scored_list)
                    max_fitness = np.max(fitness_scored_list)

                    # Update live plot data
                    self.episodes.append(episode_count)
                    self.mean_fitness_values.append(mean_fitness)
                    self.min_fitness_values.append(min_fitness)
                    self.max_fitness_values.append(max_fitness)

                    self.mean_line.set_xdata(self.episodes)
                    self.mean_line.set_ydata(self.mean_fitness_values)
                    self.min_line.set_xdata(self.episodes)
                    self.min_line.set_ydata(self.min_fitness_values)
                    self.max_line.set_xdata(self.episodes)
                    self.max_line.set_ydata(self.max_fitness_values)


                    survival_time_scores = [robot.time_survived for robot in np.array(self.gamesRobots).flatten() if robot.type == AVOIDER]
                    max_possible_survival_time = self.trainingTime / 1000
                    normalized_survival_time_scores = [score / max_possible_survival_time for score in survival_time_scores]
                    print("normalized survival time scores", normalized_survival_time_scores)
                    mean_survival_time = np.mean(normalized_survival_time_scores)
                    min_survival_time = np.min(normalized_survival_time_scores)
                    max_survival_time = np.max(normalized_survival_time_scores)

                    print(f" mean normalized survival time: {mean_survival_time}, min normalized survival time: {min_survival_time}, max normalized survival time: {max_survival_time}")
                    
                    # print("survival time scores", survival_time_scores)
                    # mean_survival_time = np.mean(survival_time_scores)
                    # min_survival_time = np.min(survival_time_scores)
                    # max_survival_time = np.max(survival_time_scores)
                    # print(f" mean survival time: {mean_survival_time}, min survival time: {min_survival_time}, max survival time: {max_survival_time}")

                    # Update live plot data
                    self.episodes2.append(episode_count)
                    self.mean_survival_time_values.append(mean_survival_time)
                    self.min_survival_time_values.append(min_survival_time)
                    self.max_survival_time_values.append(max_survival_time)

                    self.mean_line_surival.set_xdata(self.episodes2)
                    self.mean_line_surival.set_ydata(self.mean_survival_time_values)
                    self.min_line_survival.set_xdata(self.episodes2)
                    self.min_line_survival.set_ydata(self.min_survival_time_values)
                    self.max_line_survival.set_xdata(self.episodes2)
                    self.max_line_survival.set_ydata(self.max_survival_time_values)
                    
                    self.ax2.relim()
                    self.ax2.autoscale_view()



                    # Update trend line for the last 5 episodes
                    self.update_trend_line()

                    # Rescale axes based on data
                    self.ax.relim()
                    self.ax.autoscale_view()
                    plt.draw()
                    plt.pause(0.01)  # Pause to update the figure

                    episode_count += 1
                    robot_scores = {}

                    sorted_indices = np.argsort(fitness_scored_list)

                    rank_weights = np.zeros(self.population_size)
                    rank = 2
                    for i in sorted_indices:
                        rank_weights[i] = 1 / rank
                        rank += 1
                    rank_weights /= np.sum(rank_weights)
                    top_n_indices = sorted_indices[-self.TOP_N :]
                    all_models = np.array(
                        [
                            model.avoid_model
                            for model in np.array(self.gamesRobots).flatten()
                            if model.avoid_model is not None
                        ]
                    )
                    top_n_models = list(all_models[top_n_indices])
                    rest_models = self.population_size - self.TOP_N
                    new_models = top_n_models

                    i = 0
                    while i < rest_models:
                        two_robots = np.random.choice(all_models, size=2, p=rank_weights)
                        robot1_model = two_robots[0]
                        robot2_model = two_robots[1]
                        new_robot_1 = robot1_model.crossover(robot2_model)
                        new_robot_2 = robot2_model.crossover(robot1_model)

                        new_models.append(new_robot_1)
                        new_models.append(new_robot_2)

                        i += 2

                    for model in new_models:
                        model.mutate()

                    # robot_index = 0
                    # # Reassign models to the existing robots
                    # for model in np.array(self.gamesRobots).flatten():
                    #     if model.avoid_model is not None:
                    #         model.avoid_model = new_models[robot_index]
                    #         robot_index += 1
                    #         print(f"Updating model for {robot_index}")
                    import os
                    if not os.path.exists("models"):
                        os.makedirs("models")
                    
                    
                    torch.save(top_n_models[0].state_dict(), f"models/model_{episode_count}.pth")

                    model_files = sorted(os.listdir("models"), key=lambda x: int(x.split('_')[1].split('.')[0]))
                    # if len(model_files) > 5:
                    #     for file in model_files[:-5]:
                    #         os.remove(f"models/{file}")

                    self.episode_start_time = current_time
                    self.initialize_robots(new_models, episode_count)
                    self.fitness_scores = defaultdict(int)
                    for robot in np.array(self.gamesRobots).flatten():
                        if robot.avoid_model is not None:
                            robot.time_survived = 0

            # Calculate timestep
            time_step = (pygame.time.get_ticks() - self.last_time) / 1000
            self.last_time = pygame.time.get_ticks()

            for index in range(self.games):
                self.gamesRobots[index][0].seek_robot(
                    self.gamesRobots[index][1:], self.env
                )

            for game in range(self.games):
                for idx, r in enumerate(self.gamesRobots[game]):
                    if idx != 0:
                        if r.state != CAUGHT_STATE:
                            other_robots = [
                                robot
                                for i, robot in enumerate(self.gamesRobots[game])
                                if i != idx
                            ]
                            # r.avoid_robot(other_robots, self.env)
                            reward = r.avoid_robot_model(
                                other_robots, self.env, self.trainingTime
                            )
                            self.fitness_scores[r.id] += reward / r.fitness_counts
                            r.time_survived += time_step

                        else:
                            r.set_motor_speeds(0, 0)
                    # This is the odometry where we use the wheel size and speed to calculate
                    # where we approximately end up.
                    robot_pose = r.predict(time_step)

                    # Generate Lidar scans - for these exercises, you will be given these.
                    # lidar_scans, _intersect_points = self.lidar.generate_scans(robot_pose, self.env.get_environment())

                    r.update_robot_state_based_on_floor_color(self.env, robot_pose)
                    # if (time.time() - time_start) > 60:
                    #     time_stop = time.time()
                    #     print(f"Robot {r.id} caught at {time_stop - time_start} seconds", time_stop, time_start)


                    #     plt.close(self.fig)  # Close the matplotlib window
                    #     return 60
                        
                    # if r.state == CAUGHT_STATE:
                    #     time_stop = time.time()
                    #     print(f"Robot {r.id} caught at {time_stop - time_start} seconds", time_stop, time_start)
                    #     plt.close(self.fig)  # Close the matplotlib window
                    #     return time_stop - time_start

                if self.USE_VISUALIZATION:
                    self.screen.fill((0, 0, 0))
                    self.env.draw(self.screen)
                    for game_index in range(self.games):
                        for robot in self.gamesRobots[game_index]:
                            robot.draw(self.screen)

                        # if self.DRAW_LIDAR:
                        #     self.lidar.draw(robot_pose, _intersect_points, self.screen)

                        pygame.display.flip()
                        pygame.display.update()

        # Quit Pygame
        pygame.quit()
        plt.ioff()  # Turn off interactive mode
        plt.show()  # Keep the plot open after Pygame window closes
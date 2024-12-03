from shapely import Point
from constants import WALL, DANGER, SAFE
from environment import Environment
from robot_pose import RobotPose


class FloorColorSensor:
    def __init__(self):
        self.color = DANGER

    def detect_color(self, robot_pose: RobotPose, environment: Environment):
        # Fake color sensor that checks if the robot is on top of the safe zone

        # If robot is within the safe zone. This is a square in the middle of the environment
        is_within_safe_zone = Point(robot_pose.x, robot_pose.y).within(
            environment.safe_zone_rect
        )

        if is_within_safe_zone:
            self.color = SAFE
            return

        collided = environment.checkCollision(robot_pose)
        # If robot is on top of the walls
        if collided:
            self.color = WALL
            return

        self.color = DANGER

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color

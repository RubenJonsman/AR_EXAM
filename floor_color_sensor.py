from shapely import Point
from constants import BLACK_WALL_ZONE, GREY_DANGER_ZONE, SILVER_SAFE_ZONE
from environment import Environment
from robot_pose import RobotPose


class FloorColorSensor:
    def __init__(self):
      self.color = GREY_DANGER_ZONE
    def detect_color(self, robot_pose: RobotPose, environment: Environment):
        # Fake color sensor that checks if the robot is on top of the safe zone

        # If robot is within the safe zone. This is a square in the middle of the environment
        is_within_safe_zone = Point(robot_pose.x, robot_pose.y).within(environment.safe_zone_rect)

        print(is_within_safe_zone)
        if is_within_safe_zone:
            self.color = SILVER_SAFE_ZONE
            return

        collided = environment.checkCollision(robot_pose)
        # If robot is on top of the walls
        if collided:
          self.color = BLACK_WALL_ZONE
          return

        self.color = GREY_DANGER_ZONE

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color

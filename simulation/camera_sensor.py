from shapely.geometry import Polygon, Point

from constants import AVOIDER, CAMERA_RANGE, STATE_COLOR_MAP
import math

from robot_pose import RobotPose


class CameraSensor:
    def __init__(self, type, camera_range=CAMERA_RANGE):
        self.camera_range = camera_range
        self.type = type

    # def detect(self, x, y, theta, other_robots):
    #     # Create a view frustrum polygon that uses the robot's position and orientation
    #     polygon = Polygon([(x, y), (x + self.camera_range, y + self.camera_range), (x + self.camera_range, y - self.camera_range)])

    #     # Check if any of the other robots are in the view frustrum
    #     for other_robot in other_robots:
    #         if polygon.contains(other_robot.get_position()):
    #             if self.get_color(other_robot) == AVOIDER_COLOR:
    #               return True, other_robot.get_position()

    #     return False, None

    def create_view_frustum(self, robot_pose):
        # Define the base dimensions of the camera trapezoid relative to the robot
        top_width = self.camera_range * 0.5  # Half-width at the top
        base_width = self.camera_range * 0.05  # Half-width at the base
        height = self.camera_range  # Depth of the trapezoid

        # Vertices of the trapezoid before rotation (robot at origin)
        trapezoid_vertices = [
            (-top_width, height),  # Bottom left
            (top_width, height),  # Bottom right
            (base_width, 0),  # Top right
            (-base_width, 0),  # Top left
        ]

        # Rotate and translate trapezoid to match robot's position and orientation
        rotated_vertices = []
        theta = robot_pose.theta + (
            (math.pi / 2) if self.type == AVOIDER else -(math.pi / 2)
        )
        for vx, vy in trapezoid_vertices:
            # Apply rotation using the robot's theta
            rotated_x = robot_pose.x + (vx * math.cos(theta) - vy * math.sin(theta))
            rotated_y = robot_pose.y + (vx * math.sin(theta) + vy * math.cos(theta))
            rotated_vertices.append((rotated_x, rotated_y))

        # Create the view frustum polygon
        polygon = Polygon(rotated_vertices)
        return polygon, rotated_vertices

    def object_direction(self, self_pose, object_pose):
        self_x, self_y, self_theta = self_pose.x, self_pose.y, self_pose.theta

        object_x, object_y = object_pose.x, object_pose.y

        # Translate object position to robot's local frame
        dx = object_x - self_x
        dy = object_y - self_y

        # Rotate object position by negative self_theta to align with robot's forward direction
        local_x = (
            -math.sin(self_theta) * dx + math.cos(self_theta) * dy
        )  # Lateral offset

        threshold = 15  # tune such that center is actually center

        # Determine direction based on the local_y coordinate
        if abs(local_x) <= threshold:
            return "center"
        elif local_x > 0:
            return "right"
        else:
            return "left"

    def get_distance_and_angle_to_wall(self, robot_pose: RobotPose, walls):
        # Create a view frustum polygon that uses the robot's position and orientation
        polygon, _ = self.create_view_frustum(robot_pose)

        nearest_distance = float("inf")
        nearest_wall = None

        # Check if any of the walls are in the view frustum
        for wall in walls:
            if polygon.intersects(wall):
                # Calculate the distance from the robot to the wall
                distance = robot_pose.distance_to(wall)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_wall = wall

        if nearest_wall is not None:
            return nearest_distance, nearest_wall
        else:
            return None, None

    def get_distance_to_robot_in_view(self, robot_pose: RobotPose, other_robots):
        # Create a view frustum polygon that uses the robot's position and orientation
        polygon, _ = self.create_view_frustum(robot_pose)

        nearest_distance = float("inf")
        nearest_robot = None

        # Check for other robots in the view frustum
        for other_robot in other_robots:
            other_robot_pose = other_robot.get_robot_position()
            if polygon.contains(Point(other_robot_pose.x, other_robot_pose.y)):
                # Calculate the distance from the robot to the other robot
                x1, y1 = robot_pose.x, robot_pose.y
                x2, y2 = other_robot_pose.x, other_robot_pose.y
                distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_robot = other_robot

        if nearest_robot is not None:
            return nearest_distance, nearest_robot
        else:
            return None, None

    def detect(self, robot_pose, other_robots, object_color):
        polygon, _ = self.create_view_frustum(robot_pose)

        # Check for other robots in the view frustum
        for other_robot in other_robots:
            other_robot_pose = other_robot.get_robot_position()
            if polygon.contains(Point(other_robot_pose.x, other_robot_pose.y)):
                if self.get_color(other_robot) == object_color:
                    dir = self.object_direction(robot_pose, other_robot_pose)
                    return dir, other_robot

        return None, None

    def get_color(self, robot):
        return STATE_COLOR_MAP[robot.type, robot.state]

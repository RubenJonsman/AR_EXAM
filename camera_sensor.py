from shapely.geometry import Polygon, Point

from constants import AVOIDER_COLOR, STATE_COLOR_MAP
import math

class CameraSensor:
    def __init__(self, camera_range = 100):
        self.camera_range = camera_range

    # def detect(self, x, y, theta, other_robots):
    #     # Create a view frustrum polygon that uses the robot's position and orientation
    #     polygon = Polygon([(x, y), (x + self.camera_range, y + self.camera_range), (x + self.camera_range, y - self.camera_range)])

    #     # Check if any of the other robots are in the view frustrum
    #     for other_robot in other_robots:
    #         if polygon.contains(other_robot.get_position()):
    #             if self.get_color(other_robot) == AVOIDER_COLOR:
    #               return True, other_robot.get_position()
                
    #     return False, None

    def create_view_frustum(self, x, y, theta):
        # Define the base dimensions of the camera trapezoid relative to the robot
        base_width = self.camera_range * 0.5  # Half-width at the base
        top_width = self.camera_range * 0.2  # Half-width at the top
        height = self.camera_range           # Depth of the trapezoid
        
        # Vertices of the trapezoid before rotation (robot at origin)
        trapezoid_vertices = [
            (-base_width, height),  # Bottom left
            (base_width, height),   # Bottom right
            (top_width, 0),         # Top right
            (-top_width, 0),        # Top left
        ]

        # Rotate and translate trapezoid to match robot's position and orientation
        rotated_vertices = []
        theta -= math.pi /2
        for vx, vy in trapezoid_vertices:
            # Apply rotation using the robot's theta
            rotated_x = x + (vx * math.cos(theta) - vy * math.sin(theta))
            rotated_y = y + (vx * math.sin(theta) + vy * math.cos(theta))
            rotated_vertices.append((rotated_x, rotated_y))

        # Create the view frustum polygon
        polygon = Polygon(rotated_vertices)
        return polygon, rotated_vertices


    def detect(self, x, y, theta, other_robots):
        polygon, _ = self.create_view_frustum(x, y, theta)

        # Check for other robots in the view frustum
        for other_robot in other_robots:
            other_robot_pos = other_robot.get_robot_position()
            x, y, theta = other_robot_pos.x, other_robot_pos.y, other_robot_pos.theta
            if polygon.contains(Point(x, y)):
                if self.get_color(other_robot) == AVOIDER_COLOR:
                    return True, (x, y, theta)

        return False, None

    def get_color(self, robot):
        return  STATE_COLOR_MAP[robot.type, robot.state]



from shapely import LineString, Point


class RobotPose:
    def __init__(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta
    #this is for pretty printing
    def __repr__(self) -> str:
        return f"x:{self.x},y:{self.y},theta:{self.theta}"
    
    def distance_to(self, wall: LineString):
        return wall.distance(Point(self.x, self.y))

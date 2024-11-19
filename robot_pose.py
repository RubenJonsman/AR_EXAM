
class RobotPose:
    def __init__(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta
    #this is for pretty printing
    def __repr__(self) -> str:
        return f"x:{self.x},y:{self.y},theta:{self.theta}"

from constants import AVOIDER, BLACK_WALL_ZONE
from robot_class import PhysicalRobot
from tdmclient import ClientAsync
import cv2

with ClientAsync() as client:
    async def prog():
        with await client.lock() as node:
            await node.wait_for_variables({"prox.horizontal"})
            cap = cv2.VideoCapture(0)
            robot = PhysicalRobot(node=node, capture=cap)
                                        

            while True:
                # Pseudo code
                robot.avoid_robot(other_robots, self.env)

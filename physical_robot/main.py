from robot import PhysicalRobot
from tdmclient import ClientAsync
import time
import cv2

with ClientAsync() as client:

    async def prog():
        with await client.lock() as node:
            await node.wait_for_variables({"prox.horizontal"})
            cap = cv2.VideoCapture(0)
            robot = PhysicalRobot(node=node, capture=cap)
            try:
                while True:
                    # Pseudo code
                    robot.avoid_robot()
                    await client.sleep(0.025)
                    # time.sleep(0.5)
            except KeyboardInterrupt:
                robot.set_motor_speeds(0, 0)

    client.run_async_program(prog)

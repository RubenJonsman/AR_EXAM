from utils.led_change import change_color
from robot import PhysicalRobot
from tdmclient import ClientAsync
import time
import cv2
from constants import LED_STATE_COLOR_MAP, SEEKER, AVOIDER
import sys

if __name__ == "__main__":
    print(sys.argv)

    if sys.argv[1].lower() == "seeker":
        robot_type = SEEKER

    if sys.argv[1].lower() == "avoider":
        robot_type = AVOIDER

    with ClientAsync() as client:

        async def prog():
            with await client.lock() as node:
                await node.wait_for_variables({"prox.horizontal"})
                while True:
                    cap = cv2.VideoCapture(0)
                    robot = PhysicalRobot(node=node, capture=cap, robot_type=robot_type)
                    await robot.init_robot()
                    try:
                        while True:
                            await robot.run()
                            await client.sleep(0.025)
                    except KeyboardInterrupt as e:
                        print(f"Error in main loop: {e}")
                        robot.set_motor_speeds(0, 0)

        client.run_async_program(prog)

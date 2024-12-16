from robot import PhysicalRobot
from tdmclient import ClientAsync
import cv2
from constants import AUTO_RESTART, SEEKER, AVOIDER
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
                print("Waiting for variables")
                await node.wait_for_variables({"prox.horizontal"})
                print("Variables ready")

                print("Initializing robot")

                cap = cv2.VideoCapture(0)
                robot = PhysicalRobot(
                    node=node,
                    capture=cap,
                    robot_type=robot_type,
                    auto_restart=AUTO_RESTART,
                )

                print("Robot initialized")
                try:
                    while True:
                        await robot.run()
                        await client.sleep(1 / 60)
                except KeyboardInterrupt as e:
                    print(f"Error in main loop: {e}")
                    robot.set_motor_speeds(0, 0)

        client.run_async_program(prog)

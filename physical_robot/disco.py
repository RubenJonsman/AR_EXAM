from utils.led_change import change_color
from tdmclient import ClientAsync
from constants import SEEKER, AVOIDER
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
                    await change_color(node, "red")
                    await node.run()
                    await client.sleep(0.025)

                    await change_color(node, "green")
                    await node.run()
                    await client.sleep(0.025)

                    await change_color(node, "blue")
                    await node.run()
                    await client.sleep(0.025)

        client.run_async_program(prog)

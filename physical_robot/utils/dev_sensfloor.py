# sens floor

# Higher values = more reflection (like white surfaces)
# Lower values = less reflection (like black surfaces)

from constants import *

from tdmclient import ClientAsync

area_dict = {
    DANGER: "Grey Danger Zone",
    SAFE: "Silver Safe Zone",
    WALL: "Black Wall Zone",
    4: "Undefined",
}

# REFLECTIVE SENSOR VALUES
# GREY L: 663, 665,
# GREY R: 517, 520,
# BLACK L: 107, 106, 95 (getting closer at 300)
# BLACK R: 101, 88 (getting closer at 375)


def area_reader(left_sensor, right_sensor):
    if left_sensor < 300 and right_sensor < 300:
        return WALL
    elif left_sensor < 900 and right_sensor < 930:
        return DANGER
    elif left_sensor < 1024 and right_sensor < 1024:
        return SAFE
    else:
        return 4  # needs to be defined


# ground_sensor_program = """
# # Initialize timer
# timer.period[0] = 100  # 100ms interval
# """


with ClientAsync() as client:

    async def prog():
        with await client.lock() as node:
            # Compile and send program
            # error = await node.compile(ground_sensor_program)
            # if error is not None:
            #     print(f"Compilation error: {error['error_msg']}")
            #     return

            # await node.run()
            # Wait for ground sensors to be ready
            await node.wait_for_variables({"prox.ground.delta"})
            print("Thymio started successfully!")

            while True:
                try:
                    # Get ground sensor values
                    # These are the reflected light values
                    ground_left_sensor = node.v.prox.ground.delta[
                        0
                    ]  # Left ground sensor
                    ground_right_sensor = node.v.prox.ground.delta[
                        1
                    ]  # Right ground sensor

                    print("\nGround Sensor Values:")
                    print(f"Left  ground sensor: {ground_left_sensor}")
                    print(f"Right ground sensor: {ground_right_sensor}")
                    print("-" * 40)  # Separator line

                    # You can add color detection logic here
                    # Higher values usually mean lighter colors (white)
                    # Lower values usually mean darker colors (black)
                    _area = area_reader(ground_left_sensor, ground_right_sensor)
                    print(area_dict[_area])
                    print("*" * 40)  # Separator line

                    # if ground_left_sensor > 500 and ground_right_sensor > 500:
                    #     print("Detected light surface (possibly white)")
                    # elif ground_left_sensor < 200 and ground_right_sensor < 200:
                    #     print("Detected dark surface (possibly black)")

                    await client.sleep(1)  # Wait 100ms before next reading

                except Exception as e:
                    print(f"Error reading sensors: {e}")
                    break

    print("Program started")
    client.run_async_program(prog)

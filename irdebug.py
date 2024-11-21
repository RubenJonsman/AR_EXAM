from tdmclient import ClientAsync

seeker_program = """
var send_interval = 200  # time in milliseconds
timer.period[0] = send_interval

# Use 'call' for LED commands
call leds.top(32, 0, 0)
call leds.bottom.left(32, 0, 0)
call leds.bottom.right(32, 0, 0)

call prox.comm.enable(1)
onevent timer0
    prox.comm.tx = 1
"""

with ClientAsync() as client:
    async def prog():
        """
        Asynchronous function controlling the Thymio.
        """
        with await client.lock() as node:
            # Compile and send the program to the Thymio.
            error = await node.compile(seeker_program)
            if error is not None:
                print(f"Compilation error: {error['error_msg']}")
            else:
                error = await node.run()
                if error is not None:
                    print(f"Error {error['error_code']}")

            # Wait for the robot's proximity sensors to be ready.
            await node.wait_for_variables({"prox.horizontal"})
            print("Thymio started successfully!")

            while True:
                try:
                    # get the values of the proximity sensors
                    prox_values = node.v.prox.horizontal
                    print(f"Proximity values: {prox_values}")

                    message = node.v.prox.comm.rx
                    print(f"message from Thymio: {message}")

                    if sum(prox_values) > 20000:
                        break

                    node.flush()  # Send the set commands to the robot.
                    await client.sleep(0.3)  # Pause before next iteration

                except Exception as e:
                    print(f"Error reading sensors: {e}")
                    break

            # Once out of the loop, stop the robot
            print("Thymio stopped successfully!")
            await node.compile("""
                call leds.top(32,0,0)
                motor.left.target = 0
                motor.right.target = 0
            """)
            await node.run()

    print("Program started")
    client.run_async_program(prog)
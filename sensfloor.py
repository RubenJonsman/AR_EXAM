# sens floor

# Higher values = more reflection (like white surfaces)
# Lower values = less reflection (like black surfaces)

from constants import *

from tdmclient import ClientAsync

ground_sensor_program = """
# Initialize timer
timer.period[0] = 100  # 100ms interval
"""

with ClientAsync() as client:
    async def prog():
        with await client.lock() as node:
            # Compile and send program
            error = await node.compile(ground_sensor_program)
            if error is not None:
                print(f"Compilation error: {error['error_msg']}")
                return
            
            await node.run()
            # Wait for ground sensors to be ready
            await node.wait_for_variables({"prox.ground.delta"})
            print("Thymio started successfully!")

            while True:
                try:
                    # Get ground sensor values
                    # These are the reflected light values
                    ground_left = node.v.prox.ground.delta[0]    # Left ground sensor
                    ground_right = node.v.prox.ground.delta[1]   # Right ground sensor
                    
                    print("\nGround Sensor Values:")
                    print(f"Left  ground sensor: {ground_left}")
                    print(f"Right ground sensor: {ground_right}")
                    print("-" * 40)  # Separator line
                    
                    # You can add color detection logic here
                    # Higher values usually mean lighter colors (white)
                    # Lower values usually mean darker colors (black)
                    if ground_left > 500 and ground_right > 500:
                        print("Detected light surface (possibly white)")
                    elif ground_left < 200 and ground_right < 200:
                        print("Detected dark surface (possibly black)")
                    
                    await client.sleep(1)  # Wait 100ms before next reading
                    
                except Exception as e:
                    print(f"Error reading sensors: {e}")
                    break

    print("Program started")
    client.run_async_program(prog)
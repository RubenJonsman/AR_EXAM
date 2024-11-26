from tdmclient import ClientAsync

sensor_program = """
# Initialize timer
timer.period[0] = 1000  # 100ms interval

# Enable proximity sensors
call prox.comm.enable(1)
"""

with ClientAsync() as client:
   async def prog():
       with await client.lock() as node:
           # Compile and send program
           error = await node.compile(sensor_program)
           if error is not None:
               print(f"Compilation error: {error['error_msg']}")
               return
           
           await node.run()
           await node.wait_for_variables({"prox.horizontal"})
           print("Thymio started successfully!")

           while True:
               try:
                   # Get all 7 proximity sensor values
                   front_left2 = node.v.prox.horizontal[0]    # Leftmost
                   front_left1 = node.v.prox.horizontal[1]    # Left
                   front_center = node.v.prox.horizontal[2]   # Center
                   front_right1 = node.v.prox.horizontal[3]   # Right
                   front_right2 = node.v.prox.horizontal[4]   # Rightmost
                   back_left = node.v.prox.horizontal[5]      # Back left
                   back_right = node.v.prox.horizontal[6]     # Back right


                   print(f"Node ID: {node.id.hex()}")
                   print("\nProximity Sensor Values:")
                   print(f"Front Left 2  (Leftmost) : {front_left2}")
                   print(f"Front Left 1  (Left)     : {front_left1}")
                   print(f"Front Center (Center)    : {front_center}")
                   print(f"Front Right 1 (Right)    : {front_right1}")
                   print(f"Front Right 2 (Rightmost): {front_right2}")
                   print(f"Back Left               : {back_left}")
                   print(f"Back Right              : {back_right}")
                   print("-" * 40)  # Separator line
                   
                   await client.sleep(1)
                   
               except Exception as e:
                   print(f"Error reading sensors: {e}")
                   break

   print("Program started")
   client.run_async_program(prog)
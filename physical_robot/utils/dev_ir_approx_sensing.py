from tdmclient import ClientAsync

sensor_program = """
# Initialize timer
timer.period[0] = 1000  # 100ms interval

# Enable proximity sensors
call prox.comm.enable(1)
"""

def object_detection_approx_sensor(node):
    object_detection_array = [0,0,0,0]
    front_left2 = node.v.prox.horizontal[0]    # Leftmost
    front_left1 = node.v.prox.horizontal[1]    # Left
    front_center = node.v.prox.horizontal[2]   # Center
    front_right1 = node.v.prox.horizontal[3]   # Right
    front_right2 = node.v.prox.horizontal[4]   # Rightmost
    back_left = node.v.prox.horizontal[5]      # Back left
    back_right = node.v.prox.horizontal[6]     # Back right
    if front_left2 > 0 or front_left1 > 0:
        object_detection_array[0] = 1
        # 0 position 1
    if front_center > 0:
        object_detection_array[1] = 1
        # 1 position 1
    if front_right1 > 0 or front_right2 > 0:
        object_detection_array[2] = 1
        # 2 position 1
    if back_left > 0 or back_right > 0:
        object_detection_array[3] = 1

    return object_detection_array

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
                   object_detection_array = object_detection_approx_sensor(node)
                   print(object_detection_array)
                   
                   
                   await client.sleep(1)
                   
               except Exception as e:
                   print(f"Error reading sensors: {e}")
                   break

   print("Program started")
   client.run_async_program(prog)
import cv2
from tdmclient import ClientAsync
from led_change import change_color
import numpy as np
import time


camera = cv2.VideoCapture(0)


def camera_loop(camera):
    ret, frame = camera.read()

    if not ret:
        print("failed to grab frame")
        exit(1)

    # flip x
    flipped_frame = cv2.flip(frame, 1)
    # flip y
    flipped_frame = cv2.flip(flipped_frame, 0)

    # Apply blur to reduce noise
    blurred_frame = cv2.GaussianBlur(flipped_frame, (5, 5), 10)
    # cv2.imwrite("./imgs/blurred_frame.jpg", blurred_frame)

    # Convert to HSV
    hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

    lower_color = np.array([0 ,106 ,233])
    upper_color = np.array([180 ,255 ,255])

    mask = cv2.inRange(hsv, lower_color, upper_color)
    # cv2.imwrite("./imgs/mask.jpg", mask)
    blurred_mask = cv2.GaussianBlur(mask, (3, 3), 0)
    # cv2.imwrite("./imgs/blurred_mask.jpg", blurred_mask)

    contours, _ = cv2.findContours(
        blurred_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    cx = 360
    ball_detected = False
    ball_count = 0
    for contour in contours:
        M = cv2.moments(contour)
        area = cv2.contourArea(contour)
        if area > 500:
            ball_count += 1
            ball_detected = True

            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                # self.positions.append([cx, cy])

    center_region_size = 100
    center_region_center = 320
    center_region_left_edge = center_region_center - center_region_size
    center_region_right_edge = center_region_center + center_region_size

    print(cx)
    if ball_count > 0:
        if cx < center_region_left_edge:
            print("left")
        elif cx > center_region_right_edge:
            print("right")
        else:
            print("forward")
    # if self.draw_contours:
    contour_image = cv2.drawContours(blurred_mask, contours, -1, (0, 255, 0), 3)

    print("i see " + str(ball_count) + " balls")
    cv2.imwrite("./imgs/contour_image.jpg", blurred_mask)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        exit(0)

    time.sleep(1 / 5)


with ClientAsync() as client:

    async def prog():
        print("Starting LED sequence...")
        with await client.lock() as node:
            error = await node.compile("""
            # Turn off all leds
            call leds.circle(0, 0, 0, 0, 0, 0, 0, 0)
            call leds.top(0, 0, 0)
            call leds.bottom.left(0, 0, 32)
            call leds.bottom.right(0, 0, 32)
            # leds.prox.h(0, 0, 0, 0, 0, 0, 0, 0)
            # leds.prox.v(0, 0)
            # leds.buttons(0, 0, 0, 0)
            motor.left.target = 0
            motor.right.target = 0
            """)
            if error is not None:
                print(f"Compilation error: {error['error_msg']}")
                return

            await node.run()
            await client.sleep(2)

    client.run_async_program(prog)
    while True:
        camera_loop(camera)

#             # Blue
#             print("Setting Blue")
#             # error = await node.compile(led_blue)
#             error = await change_color(node, "blue")
#             if error is not None:
#                 print(f"Compilation error: {error['error_msg']}")
#                 return
#             await node.run()
#             await client.sleep(2)

#             # Green
#             print("Setting Green")
#             # error = await node.compile(led_green)
#             error = await change_color(node, "green")
#             if error is not None:
#                 print(f"Compilation error: {error['error_msg']}")
#                 return
#             await node.run()
#             await client.sleep(2)

#             # Red
#             print("Setting Red")
#             # error = await node.compile(led_red)
#             error = await change_color(node, "red")
#             if error is not None:
#                 print(f"Compilation error: {error['error_msg']}")
#                 return
#             await node.run()
#             await client.sleep(2)

#             # Back to Blue
#             print("Back to Blue")
#             # error = await node.compile(led_blue)
#             error = await change_color(node, "blue")
#             if error is not None:
#                 print(f"Compilation error: {error['error_msg']}")
#                 return
#             await node.run()
#             await client.sleep(2)

#     print("Program started")
#     client.run_async_program(prog)
#     print("Program finished")

import cv2
from tdmclient import ClientAsync
from led_change import change_color
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
    blurred_frame = cv2.GaussianBlur(flipped_frame, (5, 5), 0)
    hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
    # resize image
    cv2.imwrite("./imgs/flip.jpg", flipped_frame)
    cv2.imwrite("./imgs/hsv.jpg", flipped_frame)

    lower_color = (36, 25, 50)
    upper_color = (70, 255, 255)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    blurred_frame = cv2.GaussianBlur(mask, (3, 3), 0)

    contours, _ = cv2.findContours(
        blurred_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    cx = 360
    ball_detected = False
    ball_count = 0
    for contour in contours:
        M = cv2.moments(contour)
        area = cv2.contourArea(contour)
        if area > 1000:
            ball_count += 1
            ball_detected = True

            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                # self.positions.append([cx, cy])

    # if self.draw_contours:
    contour_image = cv2.drawContours(blurred_frame, contours, -1, (0, 255, 0), 3)

    print("i see " + str(ball_count) + " balls")
    cv2.imwrite("./imgs/contour_image.jpg", blurred_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        exit(0)

    time.sleep(1/5)

with ClientAsync() as client:

    async def prog():
        print("Starting LED sequence...")
        with await client.lock() as node:
            error = await node.compile("""
            # Turn off all leds
            call leds.circle(0, 0, 0, 0, 0, 0, 0, 0)
            call leds.top(0, 0, 0)
            call leds.bottom.left(0, 32, 0)
            call leds.bottom.right(0, 32, 0)
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
